"""Festival Architect: every screen of the app lives here. Start it with `uv run streamlit run app.py`."""
from datetime import time

import streamlit as st

import logic

SCREENS = ["Book an artist", "The lineup"]
CARDS_PER_ROW = 4


# ---------- small helpers ----------

def artist_label(artist_id):
    """Turn an artist id into the text shown in the artist picker."""
    artist = logic.get_artist(artist_id)
    return artist["name"] + " — " + artist["genre"]


def stage_label(stage_id):
    """Turn a stage id into the stage's name."""
    return logic.stage_name(stage_id)


def chosen_artist_id():
    """Return the artist the organiser clicked in the catalogue, or None if they clicked none."""
    if "chosen_artist" in st.session_state:
        return st.session_state["chosen_artist"]
    return None


def choose_artist(artist_id):
    """Remember which artist was clicked, so the form below opens on that artist."""
    st.session_state["chosen_artist"] = artist_id


def remember_message(text):
    """Keep a message so it survives the redraw that follows an accepted booking."""
    st.session_state["message"] = text


def show_remembered_message():
    """Print the message left by the last accepted booking, once."""
    if "message" in st.session_state:
        st.success(st.session_state["message"])
        del st.session_state["message"]


def forget_artist():
    """Drop the remembered choice, after a booking is made or the artist is gone."""
    if "chosen_artist" in st.session_state:
        del st.session_state["chosen_artist"]


def show_artist_card(artist, column):
    """Draw one artist as a card. Clicking it picks that artist in the form below.

    Every card carries a button, booked or not, so all the cards in a row are the same height.
    A booked artist's button is greyed out and says so.
    """
    booked = logic.is_booked(artist["id"])
    with column.container(border=True):
        if booked:
            # grey, so a card you cannot pick looks different before you read it
            st.markdown("#### :grey[" + artist["name"] + "]")
            st.caption(artist["genre"] + " · " + artist["fee"] + " € · "
                       + artist["duration_min"] + " min")
            st.button("Already playing", key="pick_" + artist["id"], disabled=True,
                      use_container_width=True)
        else:
            st.markdown("#### " + artist["name"])
            st.caption(artist["genre"] + " · **" + artist["fee"] + " €** · "
                       + artist["duration_min"] + " min")
            chosen = artist["id"] == chosen_artist_id()
            st.button("Chosen" if chosen else "Choose", key="pick_" + artist["id"],
                      disabled=chosen, use_container_width=True,
                      type="primary" if chosen else "secondary",
                      on_click=choose_artist, args=(artist["id"],))


def free_artist_ids():
    """Return the ids of the artists that are not in the lineup yet."""
    ids = []
    for artist in logic.all_artists():
        if not logic.is_booked(artist["id"]):
            ids.append(artist["id"])
    return ids


def opening_time():
    """Return the festival's opening time as a clock value, for the time picker's default."""
    minutes = logic.to_minutes(logic.opens())
    return time(minutes // 60, minutes % 60)


def chosen_position(free):
    """Return where the clicked artist sits in the picker, or 0 when nothing was clicked."""
    chosen = chosen_artist_id()
    for position in range(len(free)):
        if free[position] == chosen:
            return position
    return 0


def stage_ids():
    """Return the ids of every stage."""
    ids = []
    for stage in logic.all_stages():
        ids.append(stage["id"])
    return ids


# ---------- the money ----------

def show_budget():
    """The two numbers that must agree with the lineup after every accepted change."""
    left, right = st.columns(2)
    left.metric("Artist fees", str(logic.total_fees()) + " €")
    right.metric("Budget left", str(logic.remaining_budget()) + " €")


# ---------- screen 1: book an artist ----------

def show_booking():
    """Catalogue plus the form that adds one performance to the lineup."""
    st.title("Book an artist")
    show_remembered_message()
    show_budget()

    st.subheader("The catalogue")
    artists = logic.all_artists()
    columns = st.columns(CARDS_PER_ROW)
    for position in range(len(artists)):
        # fill the row left to right, then start the next one
        show_artist_card(artists[position], columns[position % CARDS_PER_ROW])

    st.subheader("Add a performance")
    free = free_artist_ids()
    if len(free) == 0:
        st.caption("Every artist in the catalogue is already playing.")
        return

    with st.form("add_booking"):
        artist_id = st.selectbox("Artist", free, index=chosen_position(free),
                                 format_func=artist_label)
        stage_id = st.selectbox("Stage", stage_ids(), format_func=stage_label)
        picked = st.time_input("Start time", value=opening_time(), step=300)
        start_time = logic.to_time_text(picked.hour * 60 + picked.minute)
        if st.form_submit_button("Add performance"):
            refusal = logic.add_booking(artist_id, stage_id, start_time)
            if refusal == "":
                forget_artist()
                remember_message(logic.get_artist(artist_id)["name"] + " plays at "
                                 + start_time + " on " + logic.stage_name(stage_id) + ".")
                # redraw, so the catalogue and the budget show the booking we just made
                st.rerun()
            else:
                st.warning(refusal)


# ---------- screen 2: the lineup ----------

def show_lineup():
    """Every booked performance, one stage after another. Task 3 turns this into a timetable."""
    st.title("The lineup")
    show_budget()

    bookings = logic.all_bookings()
    if len(bookings) == 0:
        st.caption("Nothing booked yet. Add a performance first.")
        return

    for stage in logic.all_stages():
        st.subheader(stage["name"])
        playing = False
        for booking in bookings:
            if booking["stage_id"] != stage["id"]:
                continue
            playing = True
            artist = logic.get_artist(booking["artist_id"])
            ends = logic.end_time(artist["id"], booking["start_time"])
            st.markdown("**" + booking["start_time"] + "–" + ends + "** · "
                        + artist["name"] + " · " + artist["genre"])
        if not playing:
            st.caption("Nothing on this stage yet.")


# ---------- this part runs on every click ----------

st.set_page_config(page_title="Festival Architect")
st.sidebar.title("Festival Architect")
screen = st.sidebar.radio("Screen", SCREENS)
st.sidebar.caption("The plan lives in data/*.csv. Reset it with `uv run python seed.py`.")

if screen == "Book an artist":
    show_booking()
else:
    show_lineup()
