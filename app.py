"""Festival Architect: every screen of the app lives here. Start it with `uv run streamlit run app.py`."""
from datetime import time

import streamlit as st
from streamlit_calendar import calendar
from streamlit_extras.metric_cards import style_metric_cards

import logic

SCREENS = ["Book an artist", "The lineup"]
CARDS_PER_ROW = 4
CARD_HEIGHT = 190

# The two stage colours from CLAUDE.md, in stage order. A colour always means a stage.
STAGE_COLOURS = ["#865D36", "#4A5D3A"]
SOIL = "#3E362E"
PAPER = "#F3EADF"
WARM_SAND = "#AC8968"

# The brief describes one festival day but never dates it. The calendar needs some date to
# draw, so we pick one; nothing is stored against it and no rule ever reads it.
FESTIVAL_DAY = "2026-06-20"

# The detail panel stands as tall as the calendar next to it, so the row never changes shape.
DETAIL_HEIGHT = 760


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
    # A fixed height keeps every card in the row the same size, whether or not the
    # artist's name wraps onto a second line.
    with column.container(border=True, height=CARD_HEIGHT):
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


def clock_value(time_text):
    """Turn a stored time like '16:30' into the clock value a time picker wants."""
    minutes = logic.to_minutes(time_text)
    return time(minutes // 60, minutes % 60)


def opening_time():
    """Return the festival's opening time as a clock value, for the time picker's default."""
    return clock_value(logic.opens())


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
    left, middle, right = st.columns(3)
    left.metric("Artists booked", len(logic.all_bookings()))
    middle.metric("Artist fees", str(logic.total_fees()) + " €")
    right.metric("Budget left", str(logic.remaining_budget()) + " €")
    style_metric_cards(background_color=WARM_SAND, border_left_color=STAGE_COLOURS[1],
                       border_color=WARM_SAND, box_shadow=False)


def stage_colour(stage_id):
    """Return the colour of one stage, by its position in the stages table."""
    stages = logic.all_stages()
    for position in range(len(stages)):
        if stages[position]["id"] == str(stage_id):
            return STAGE_COLOURS[position % len(STAGE_COLOURS)]
    return STAGE_COLOURS[0]


def calendar_events():
    """Turn every performance into one block the calendar can draw."""
    events = []
    for stage in logic.all_stages():
        for performance in logic.timetable(stage["id"]):
            events.append({
                "id": performance["booking_id"],
                "title": performance["name"],
                "start": FESTIVAL_DAY + "T" + performance["start_time"] + ":00",
                "end": FESTIVAL_DAY + "T" + performance["end_time"] + ":00",
                "resourceId": stage["id"],
                "backgroundColor": stage_colour(stage["id"]),
                "borderColor": stage_colour(stage["id"]),
                "textColor": PAPER,
            })
    return events


def calendar_options():
    """Describe the day the calendar draws: one column per stage, opening time to closing time."""
    resources = []
    for stage in logic.all_stages():
        resources.append({"id": stage["id"], "title": stage["name"]})
    return {
        "initialView": "resourceTimeGridDay",
        "initialDate": FESTIVAL_DAY,
        "slotMinTime": logic.opens() + ":00",
        "slotMaxTime": logic.closes() + ":00",
        "slotDuration": "00:30:00",
        # A half-hour slot needs real height, or a 40-minute set clips its own name.
        "slotMinHeight": 46,
        "expandRows": True,
        "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "slotLabelFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "allDaySlot": False,
        "headerToolbar": {"left": "", "center": "", "right": ""},
        "height": 760,
        # Blocks can be dragged to another time or stage; every drag still goes through
        # logic.edit_booking, so the rules decide. Length belongs to the artist, so no resizing.
        "editable": True,
        "eventStartEditable": True,
        "eventDurationEditable": False,
        "eventResizableFromStart": False,
        "resources": resources,
    }


CALENDAR_CSS = """
    .fc { background-color: #AC8968; border-radius: 10px; padding: 8px; }
    .fc a { color: #3E362E; }
    .fc .fc-col-header-cell-cushion { color: #3E362E; font-weight: 700;
        text-transform: uppercase; letter-spacing: .12em; font-size: .8em; }
    .fc .fc-timegrid-slot-label-cushion { color: #3E362E; opacity: .7; font-size: .8em; }
    .fc-theme-standard td, .fc-theme-standard th,
    .fc-theme-standard .fc-scrollgrid { border-color: rgba(62,54,46,.22); }
    .fc-event-title { font-weight: 700; }
    .fc-timegrid-event .fc-event-main { padding: 2px 4px; overflow: hidden; }
    .fc-timegrid-event .fc-event-time { font-size: .72em; opacity: .85; }
    .fc-timegrid-event .fc-event-title { font-size: .86em; line-height: 1.15; }
    .fc-timegrid-event { cursor: pointer; }
"""


# ---------- screen 1: book an artist ----------

def show_booking():
    """Catalogue plus the form that adds one performance to the lineup."""
    st.title("Book an artist")
    show_remembered_message()
    show_budget()

    st.subheader("The catalogue")
    artists = logic.all_artists()
    # One st.columns per row, not one for the whole catalogue: a row of columns is only as
    # tall as its own cards, so a long artist name cannot push the row below it out of line.
    for first in range(0, len(artists), CARDS_PER_ROW):
        row = artists[first:first + CARDS_PER_ROW]
        columns = st.columns(CARDS_PER_ROW)
        for position in range(len(row)):
            show_artist_card(row[position], columns[position])

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
    """The festival day as a calendar: one column per stage, opening time to closing time."""
    st.title("The lineup")
    show_remembered_message()
    show_remembered_refusal()
    show_budget()
    st.caption("Drag a performance to another time or stage. "
               "Click one to see the artist behind it.")

    if len(logic.all_bookings()) == 0:
        st.caption("Nothing booked yet. Add a performance first.")
        return

    # The calendar on the left, the detail of whatever was clicked on the right, so a click
    # always has a visible effect without the organiser having to scroll to find it.
    timetable_column, detail_column = st.columns([3, 1])
    with timetable_column:
        clicked = calendar(events=calendar_events(), options=calendar_options(),
                           custom_css=CALENDAR_CSS,
                           key="timetable-" + str(calendar_version()))
        apply_dragged_change(clicked)
    with detail_column:
        show_clicked_performance(clicked)

    with st.expander("Change a performance by hand"):
        show_revise(clicked_booking_id(clicked))

    with st.expander("The same lineup as a list"):
        show_lineup_as_a_list()


def booking_label(booking_id):
    """Turn a booking id into the text shown in the performance picker."""
    booking = logic.get_booking(booking_id)
    artist = logic.get_artist(booking["artist_id"])
    return (artist["name"] + " · " + logic.stage_name(booking["stage_id"])
            + " · " + booking["start_time"])


def booked_ids():
    """Return the ids of every performance in the lineup, in time order within each stage."""
    ids = []
    for stage in logic.all_stages():
        for performance in logic.timetable(stage["id"]):
            ids.append(performance["booking_id"])
    return ids


def position_of(booking_id, ids):
    """Return where a performance sits in the picker, or 0 when it is not there."""
    for position in range(len(ids)):
        if ids[position] == booking_id:
            return position
    return 0


def show_revise(clicked_id):
    """Move a performance to another stage or time, or take it out of the lineup (FA04)."""
    ids = booked_ids()
    if len(ids) == 0:
        return

    # the block just clicked in the timetable is the one the form opens on
    booking_id = st.selectbox("Performance", ids, index=position_of(clicked_id, ids),
                              format_func=booking_label)
    booking = logic.get_booking(booking_id)

    with st.form("edit_booking"):
        stage_id = st.selectbox("Move to stage", stage_ids(),
                                index=position_of(booking["stage_id"], stage_ids()),
                                format_func=stage_label)
        picked = st.time_input("Move to start time", value=clock_value(booking["start_time"]),
                               step=300)
        start_time = logic.to_time_text(picked.hour * 60 + picked.minute)
        move, remove = st.columns(2)
        moved = move.form_submit_button("Move performance", use_container_width=True)
        removed = remove.form_submit_button("Remove from lineup", use_container_width=True)

    if moved:
        refusal = logic.edit_booking(booking_id, stage_id, start_time)
        if refusal == "":
            remember_message(booking_label(booking_id) + " — moved.")
            redraw_calendar()
            st.rerun()
        else:
            st.warning(refusal)
    if removed:
        name = logic.get_artist(booking["artist_id"])["name"]
        refusal = logic.remove_booking(booking_id)
        if refusal == "":
            remember_message(name + " is out of the lineup. The fee is back in the budget.")
            redraw_calendar()
            st.rerun()
        else:
            st.warning(refusal)


def dragged_change(payload):
    """Return (booking_id, stage_id, start_time) when a block was dragged, or None.

    The calendar reports the block's new position; it is a request, not a decision.
    """
    if not isinstance(payload, dict):
        return None
    if payload.get("callback") != "eventChange":
        return None
    event = payload.get("eventChange", {}).get("event", {})
    booking_id = event.get("id")
    stage_id = event.get("resourceId")
    starts_at = event.get("start", "")
    if booking_id is None or stage_id is None or "T" not in starts_at:
        return None
    # "2026-06-20T16:30:00+00:00" -> "16:30"
    return booking_id, str(stage_id), starts_at.split("T")[1][:5]


def calendar_version():
    """Return which drawing of the calendar we are on."""
    if "calendar_version" in st.session_state:
        return st.session_state["calendar_version"]
    return 0


def redraw_calendar():
    """Draw the calendar from scratch, so a refused drag snaps back to where it was."""
    st.session_state["calendar_version"] = calendar_version() + 1


def remember_refusal(text):
    """Keep a refusal so it survives the redraw that puts the block back."""
    st.session_state["refusal"] = text


def show_remembered_refusal():
    """Print the refusal left by the last rejected drag, once."""
    if "refusal" in st.session_state:
        st.warning(st.session_state["refusal"])
        del st.session_state["refusal"]


def apply_dragged_change(payload):
    """Ask logic to accept a dragged block, and say so when it refuses (FA04)."""
    change = dragged_change(payload)
    if change is None:
        return
    booking_id, stage_id, start_time = change

    booking = logic.get_booking(booking_id)
    if booking is None:
        return
    if booking["stage_id"] == stage_id and booking["start_time"] == start_time:
        # the calendar is only telling us where the block already is
        return

    refusal = logic.edit_booking(booking_id, stage_id, start_time)
    if refusal == "":
        remember_message(booking_label(booking_id) + " — moved.")
    else:
        remember_refusal(refusal)
    redraw_calendar()
    st.rerun()


def clicked_booking_id(clicked):
    """Return the booking id of the block the organiser clicked, or None if they clicked none."""
    if not isinstance(clicked, dict):
        return None
    if clicked.get("callback") != "eventClick":
        return None
    return clicked.get("eventClick", {}).get("event", {}).get("id")


def show_clicked_performance(clicked):
    """Show everything about the performance whose block was clicked (FA01, FA03).

    Stands in its own column beside the calendar, so it is on screen before the click happens.
    """
    booking_id = clicked_booking_id(clicked)

    if booking_id is None:
        with st.container(border=True, height=DETAIL_HEIGHT):
            st.markdown("#### The performance")
            st.caption("Click a block in the timetable to see the artist behind it.")
        return

    booking = logic.get_booking(booking_id)
    if booking is None:
        return
    artist = logic.get_artist(booking["artist_id"])

    with st.container(border=True, height=DETAIL_HEIGHT):
        st.markdown("#### " + artist["name"])
        st.caption(artist["genre"])
        st.divider()
        st.metric("Plays", booking["start_time"] + "–"
                  + logic.end_time(artist["id"], booking["start_time"]))
        st.metric("Stage", logic.stage_name(booking["stage_id"]))
        st.metric("Set length", artist["duration_min"] + " min")
        st.metric("Fee", artist["fee"] + " €")


def show_lineup_as_a_list():
    """Every performance in words, so the timetable can be checked against the data by hand."""
    for stage in logic.all_stages():
        st.subheader(stage["name"])
        performances = logic.timetable(stage["id"])
        if len(performances) == 0:
            st.caption("Nothing on this stage yet.")
        for performance in performances:
            st.markdown("**" + performance["start_time"] + "–" + performance["end_time"]
                        + "** · " + performance["name"] + " · " + performance["genre"])


# ---------- this part runs on every click ----------

st.set_page_config(page_title="Festival Architect", layout="wide")
st.sidebar.title("Festival Architect")
screen = st.sidebar.radio("Screen", SCREENS)
st.sidebar.caption("The plan lives in data/*.csv. Reset it with `uv run python seed.py`.")

if screen == "Book an artist":
    show_booking()
else:
    show_lineup()
