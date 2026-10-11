"""Festival Architect: every screen of the app lives here. Start it with `uv run streamlit run app.py`."""
import streamlit as st

import logic

SCREENS = ["Book an artist", "The lineup"]


# ---------- small helpers ----------

def artist_label(artist_id):
    """Turn an artist id into the text shown in the artist picker."""
    artist = logic.get_artist(artist_id)
    return artist["name"] + " — " + artist["genre"]


def stage_label(stage_id):
    """Turn a stage id into the stage's name."""
    return logic.stage_name(stage_id)


def artist_line(artist):
    """Build the one-line summary of an artist used in the catalogue."""
    return ("**" + artist["name"] + "** · " + artist["genre"] + " · "
            + artist["fee"] + " € · " + artist["duration_min"] + " min")


def free_artist_ids():
    """Return the ids of the artists that are not in the lineup yet."""
    ids = []
    for artist in logic.all_artists():
        if not logic.is_booked(artist["id"]):
            ids.append(artist["id"])
    return ids


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
    show_budget()

    st.subheader("The catalogue")
    for artist in logic.all_artists():
        line = artist_line(artist)
        if logic.is_booked(artist["id"]):
            line = line + " · **booked**"
        st.markdown(line)

    st.subheader("Add a performance")
    free = free_artist_ids()
    if len(free) == 0:
        st.caption("Every artist in the catalogue is already playing.")
        return

    with st.form("add_booking"):
        artist_id = st.selectbox("Artist", free, format_func=artist_label)
        stage_id = st.selectbox("Stage", stage_ids(), format_func=stage_label)
        start_time = st.text_input("Start time", value=logic.opens())
        if st.form_submit_button("Add performance"):
            refusal = logic.add_booking(artist_id, stage_id, start_time)
            if refusal == "":
                st.success(logic.get_artist(artist_id)["name"] + " plays at " + start_time
                           + " on " + logic.stage_name(stage_id) + ".")
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
