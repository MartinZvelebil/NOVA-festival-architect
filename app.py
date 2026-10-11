"""Festival Architect: the whole planner on one screen.

Start it with `uv run streamlit run app.py`. Everything here is presentation: the rules,
the money and the timetable all come from logic.py.
"""
import time

import streamlit as st
from streamlit_calendar import calendar
from streamlit_extras.metric_cards import style_metric_cards

import logic

CARDS_PER_ROW = 4
# Every card is the same height, so a row lines up whether or not an artist is booked
# or priced out of what is left.
CARD_HEIGHT = 210

# The two stage colours from CLAUDE.md, in stage order. A colour always means a stage.
STAGE_COLOURS = ["#865D36", "#4A5D3A"]
PAPER = "#F3EADF"
WARM_SAND = "#AC8968"
SOIL = "#3E362E"
OLIVE = "#4A5D3A"

# The brief describes one festival day but never dates it. The calendar needs some date to
# draw, so we pick one; nothing is stored against it and no rule ever reads it.
FESTIVAL_DAY = "2026-06-20"


# ---------- what the organiser is holding ----------

def armed_artist_id():
    """Return the artist picked up from the catalogue, or None when none is held."""
    if "armed_artist" in st.session_state:
        return st.session_state["armed_artist"]
    return None


def arm_artist(artist_id):
    """Pick an artist up, or put them down again when they are already held."""
    if armed_artist_id() == artist_id:
        del st.session_state["armed_artist"]
    else:
        st.session_state["armed_artist"] = artist_id


def disarm_artist():
    """Put down whoever is held, after they are booked."""
    if "armed_artist" in st.session_state:
        del st.session_state["armed_artist"]


# ---------- messages that survive a redraw ----------

# How long a message stays on screen, in seconds.
MESSAGE_SECONDS = 10


def remember_message(text):
    """Keep a message so it survives the redraws that follow an accepted change."""
    st.session_state["message"] = {"text": text, "good": True,
                                   "until": time.monotonic() + MESSAGE_SECONDS}


def remember_refusal(text):
    """Keep a refusal so it survives the redraws that put things back."""
    st.session_state["message"] = {"text": text, "good": False,
                                   "until": time.monotonic() + MESSAGE_SECONDS}


def seconds_left():
    """Return how long the message on screen still has, or 0 when there is none."""
    if "message" not in st.session_state:
        return 0
    left = st.session_state["message"]["until"] - time.monotonic()
    if left < 0:
        return 0
    return left


@st.fragment(run_every="0.5s")
def show_messages():
    """Print what the last change left behind, with a bar showing how long it will stay.

    A fragment that redraws itself twice a second, so the bar drains on its own. Without it
    the message would vanish on the next redraw, which is far too fast to read.
    """
    left = seconds_left()
    if left <= 0:
        if "message" in st.session_state:
            del st.session_state["message"]
        return

    message = st.session_state["message"]
    if message["good"]:
        st.success(message["text"])
    else:
        st.warning(message["text"])
    st.progress(left / MESSAGE_SECONDS)


# ---------- the calendar ----------

def calendar_version():
    """Return which drawing of the calendar we are on."""
    if "calendar_version" in st.session_state:
        return st.session_state["calendar_version"]
    return 0


def redraw_calendar():
    """Draw the calendar from scratch, so a refused change snaps back to where it was."""
    st.session_state["calendar_version"] = calendar_version() + 1


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
        # The times we send are wall-clock times with no zone. Pinning the calendar to UTC
        # keeps it that way, so a clicked slot comes back as the time the organiser saw.
        "timeZone": "UTC",
        "slotMinTime": logic.opens() + ":00",
        "slotMaxTime": logic.closes() + ":00",
        "slotDuration": "00:30:00",
        "snapDuration": "00:05:00",
        "slotMinHeight": 46,
        "expandRows": True,
        "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "slotLabelFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
        "allDaySlot": False,
        "headerToolbar": {"left": "", "center": "", "right": ""},
        "height": 760,
        # A final plan cannot be dragged. Set lengths belong to the artist, so never resizable.
        "editable": not logic.is_final(),
        "eventStartEditable": not logic.is_final(),
        "eventDurationEditable": False,
        "eventResizableFromStart": False,
        "selectable": False,
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


# ---------- reading what the calendar reports ----------

def clicked_booking_id(payload):
    """Return the booking id of the block that was clicked, or None if none was."""
    if not isinstance(payload, dict):
        return None
    if payload.get("callback") != "eventClick":
        return None
    return payload.get("eventClick", {}).get("event", {}).get("id")


def clicked_slot(payload):
    """Return (stage_id, start_time) of the empty slot that was clicked, or None."""
    if not isinstance(payload, dict):
        return None
    if payload.get("callback") != "dateClick":
        return None
    click = payload.get("dateClick", {})
    stage_id = click.get("resource", {}).get("id")
    clicked_at = click.get("date", "")
    if stage_id is None or "T" not in clicked_at:
        return None
    # "2026-06-20T15:30:00.000Z" -> "15:30"
    return str(stage_id), clicked_at.split("T")[1][:5]


def dragged_change(payload):
    """Return (booking_id, stage_id, start_time) when a block was dragged, or None."""
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
    return booking_id, str(stage_id), starts_at.split("T")[1][:5]


# ---------- acting on what the calendar reports ----------

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
        remember_message(logic.get_artist(booking["artist_id"])["name"] + " moved.")
    else:
        remember_refusal(refusal)
    redraw_calendar()
    st.rerun()


def place_armed_artist(payload):
    """Book whoever is held into the slot that was clicked: two clicks, one performance."""
    artist_id = armed_artist_id()
    slot = clicked_slot(payload)
    if artist_id is None or slot is None:
        return
    stage_id, start_time = slot

    refusal = logic.add_booking(artist_id, stage_id, start_time)
    if refusal == "":
        remember_message(logic.get_artist(artist_id)["name"] + " plays at " + start_time
                         + " on " + logic.stage_name(stage_id) + ".")
        disarm_artist()
    else:
        remember_refusal(refusal)
    redraw_calendar()
    st.rerun()


def cancel_performance(booking_id):
    """Take a performance out of the lineup (FA04)."""
    booking = logic.get_booking(booking_id)
    if booking is None:
        return
    name = logic.get_artist(booking["artist_id"])["name"]

    refusal = logic.remove_booking(booking_id)
    if refusal == "":
        remember_message(name + " is out of the lineup. The fee is back in the budget.")
    else:
        remember_refusal(refusal)
    redraw_calendar()
    st.rerun()


# ---------- the sidebar: the plan and the money ----------

# Streamlit paints its own green and amber into st.success and st.warning, and neither colour is
# in the palette. Both messages get the warm sand card, soil text and one olive edge instead: the
# sentence carries the good or the bad news, not the colour.
MESSAGE_CSS = """
    <style>
    div[data-testid="stAlert"] { background-color: %s; color: %s;
        border: 1px solid %s; border-left: 5px solid %s; border-radius: 8px; }
    div[data-testid="stAlert"] p, div[data-testid="stAlert"] svg { color: %s; fill: %s; }
    </style>
""" % (WARM_SAND, SOIL, OLIVE, OLIVE, SOIL, SOIL)


def style_the_messages():
    """Put every message on the palette, so no Streamlit green or amber is left on screen."""
    st.markdown(MESSAGE_CSS, unsafe_allow_html=True)


def style_the_metric_cards():
    """Give every metric on the page its card. One call styles them all, wherever they are.

    It injects a stylesheet, so it has to run on every draw, not only when a performance
    happens to be selected.
    """
    style_metric_cards(background_color=WARM_SAND, border_left_color=STAGE_COLOURS[1],
                       border_color=WARM_SAND, box_shadow=False)


def show_tutorial():
    """A few lines on how to plan a festival, for anyone opening the app for the first time."""
    with st.expander("How this works"):
        st.markdown(
            "**Book an artist.** Press **Pick up** on a card in the catalogue below, then click "
            "a free slot in the timetable. The artist plays on that stage, from that time, for "
            "as long as their set lasts. You can also click a free slot first and choose the "
            "artist there."
        )
        st.markdown(
            "**Move or cancel one.** Drag a performance to another time or another stage. "
            "Click it to see the artist behind it, and to cancel it — cancelling gives the fee "
            "back."
        )
        st.markdown(
            "**The rules decide.** The festival runs " + logic.opens() + " to " + logic.closes()
            + ", one performance at a time per stage, each artist only once, and "
            + str(logic.budget()) + " € in total. Anything that breaks a rule is refused and "
            "explained, and nothing changes."
        )
        st.markdown(
            "**Finish the plan.** Once " + str(logic.min_artists_to_finalise())
            + " artists are booked, use **Finalise the lineup** in the sidebar. A final lineup "
            "cannot be changed until you reopen it as a draft."
        )


def show_sidebar():
    """The plan's status and the budget, shared by everything on the page."""
    st.sidebar.title("Festival Architect")
    st.sidebar.caption(logic.opens() + " to " + logic.closes() + " · "
                       + str(len(logic.all_stages())) + " stages")

    st.sidebar.metric("Artists booked", len(logic.all_bookings()))
    st.sidebar.metric("Artist fees", str(logic.total_fees()) + " €")
    st.sidebar.metric("Budget left", str(logic.remaining_budget()) + " €")

    st.sidebar.divider()
    show_plan_status()
    st.sidebar.divider()
    st.sidebar.caption("The plan lives in data/*.csv. Reset it with `uv run python seed.py`.")


def show_plan_status():
    """Say whether the plan is a draft or final, and offer the way across (FA05)."""
    if logic.is_final():
        st.sidebar.markdown("**This lineup is final.**")
        st.sidebar.caption("Nothing can change until you reopen it.")
        if st.sidebar.button("Reopen as draft", use_container_width=True):
            logic.reopen_plan()
            remember_message("The plan is a draft again. You can change the lineup.")
            redraw_calendar()
            st.rerun()
        return

    refusal = logic.can_finalise()
    st.sidebar.markdown("**This lineup is a draft.**")
    if refusal != "":
        st.sidebar.caption(refusal)
    if st.sidebar.button("Finalise the lineup", use_container_width=True,
                         disabled=refusal != "", type="primary"):
        problem = logic.finalise_plan()
        if problem == "":
            remember_message("The lineup is final.")
        else:
            remember_refusal(problem)
        redraw_calendar()
        st.rerun()


# ---------- the right-hand panel ----------

def show_panel(payload):
    """Whatever the organiser last clicked: a performance, a free slot, or nothing yet."""
    booking_id = clicked_booking_id(payload)
    if booking_id is not None and logic.get_booking(booking_id) is not None:
        show_performance(booking_id)
        return

    slot = clicked_slot(payload)
    if slot is not None and not logic.is_final():
        show_slot_form(slot)
        return

    show_hint()


def show_hint():
    """What to do, for an organiser who has not clicked anything yet."""
    with st.container(border=True):
        st.markdown("#### The performance")
        if logic.is_final():
            st.caption("Click a performance to see the artist behind it.")
            return
        held = armed_artist_id()
        if held is None:
            st.caption("Pick an artist below, then click a free slot to book them. "
                       "Click a performance to see it, or drag it to move it.")
        else:
            st.caption("Holding **" + logic.get_artist(held)["name"]
                       + "**. Click a free slot in the timetable to book them.")


def show_performance(booking_id):
    """Everything about one performance, and the way to cancel it (FA01, FA04)."""
    booking = logic.get_booking(booking_id)
    artist = logic.get_artist(booking["artist_id"])

    with st.container(border=True):
        st.markdown("#### " + artist["name"])
        st.caption(artist["genre"])
        st.metric("Plays", booking["start_time"] + "–"
                  + logic.end_time(artist["id"], booking["start_time"]))
        st.metric("Stage", logic.stage_name(booking["stage_id"]))
        st.metric("Set length", artist["duration_min"] + " min")
        st.metric("Fee", artist["fee"] + " €")
        if not logic.is_final():
            if st.button("Cancel this performance", key="cancel_" + booking["id"],
                         use_container_width=True):
                cancel_performance(booking["id"])


def show_slot_form(slot):
    """Book into the slot that was clicked: the stage and the time are already decided (FA02)."""
    stage_id, start_time = slot
    free = free_artist_ids()

    with st.container(border=True):
        st.markdown("#### Book into " + start_time)
        st.caption(logic.stage_name(stage_id))
        if len(free) == 0:
            st.caption("Every artist is already playing.")
            return
        with st.form("book_into_slot"):
            artist_id = st.selectbox("Artist", free, format_func=artist_label)
            if st.form_submit_button("Add performance", use_container_width=True,
                                     type="primary"):
                refusal = logic.add_booking(artist_id, stage_id, start_time)
                if refusal == "":
                    remember_message(logic.get_artist(artist_id)["name"] + " plays at "
                                     + start_time + " on " + logic.stage_name(stage_id) + ".")
                    disarm_artist()
                else:
                    remember_refusal(refusal)
                redraw_calendar()
                st.rerun()


# ---------- the catalogue ----------

def artist_label(artist_id):
    """Turn an artist id into the text shown in a picker."""
    artist = logic.get_artist(artist_id)
    return artist["name"] + " — " + artist["genre"]


def free_artist_ids():
    """Return the ids of the artists that are not in the lineup yet."""
    ids = []
    for artist in logic.all_artists():
        if not logic.is_booked(artist["id"]):
            ids.append(artist["id"])
    return ids


def shortfall_text(artist):
    """Say how far over the remaining budget an artist is, or '' when they fit (FA01)."""
    over = int(artist["fee"]) - logic.remaining_budget()
    if over > 0:
        return str(over) + " € over budget"
    return ""


def show_catalogue():
    """Every artist, with what they play, what they cost and how long they are on (FA01)."""
    st.subheader("The catalogue")
    artists = logic.all_artists()
    for first in range(0, len(artists), CARDS_PER_ROW):
        row = artists[first:first + CARDS_PER_ROW]
        columns = st.columns(CARDS_PER_ROW)
        for position in range(len(row)):
            show_artist_card(row[position], columns[position])


def show_artist_card(artist, column):
    """One artist as a card. Clicking it picks the artist up, ready for a free slot."""
    booked = logic.is_booked(artist["id"])
    held = artist["id"] == armed_artist_id()
    over_budget = shortfall_text(artist)

    with column.container(border=True, height=CARD_HEIGHT):
        if booked:
            st.markdown("#### :grey[" + artist["name"] + "]")
        else:
            st.markdown("#### " + artist["name"])
        st.caption(artist["genre"] + " · **" + artist["fee"] + " €** · "
                   + artist["duration_min"] + " min")
        # The budget line is always printed, empty when the artist fits, so that every
        # button in the row starts at the same height.
        if over_budget != "" and not booked:
            st.caption(":grey[" + over_budget + "]")
        else:
            st.caption("&nbsp;", unsafe_allow_html=True)

        if logic.is_final():
            # a final plan picks nobody up, so no card carries a button at all
            return
        if booked:
            # the same button, greyed out: without it the row would not line up
            st.button("Already playing", key="booked_" + artist["id"], disabled=True,
                      use_container_width=True)
            return
        st.button("Holding" if held else "Pick up", key="arm_" + artist["id"],
                  use_container_width=True, type="primary" if held else "secondary",
                  on_click=arm_artist, args=(artist["id"],))


# ---------- this part runs on every click ----------

st.set_page_config(page_title="Festival Architect", layout="wide")
show_sidebar()

st.title("The festival")
show_tutorial()
show_messages()

timetable_column, panel_column = st.columns([3, 1])
with timetable_column:
    reported = calendar(events=calendar_events(), options=calendar_options(),
                        custom_css=CALENDAR_CSS, key="timetable-" + str(calendar_version()))
    apply_dragged_change(reported)
    place_armed_artist(reported)
with panel_column:
    show_panel(reported)

show_catalogue()
style_the_metric_cards()
style_the_messages()
