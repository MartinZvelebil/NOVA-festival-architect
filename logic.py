"""Business rules of Festival Architect: the catalogue, the timetable, the budget and the plan.

Nothing here is built yet. Every function below is a signature the acceptance tests
(tests/test_acceptance.py) already call. Build them one at a time until the tests go green.
"""
import db

# ---------- settings ----------
# The numbers of the brief live in data/settings.csv, one row per setting, so the festival day,
# the budget and the finalisation rule can be changed without touching the code. The values that
# ASSIGNMENT.md asks for are the ones shipped in seed/settings.csv. Read a setting through these
# functions rather than opening the table yourself.

def setting(key):
    """Return one setting from the settings table, as the text it is stored as."""
    raise NotImplementedError("settings: not built yet")


def opens():
    """Return the time the festival opens, e.g. '14:00' (FA R2)."""
    raise NotImplementedError("settings: not built yet")


def closes():
    """Return the time the festival closes, e.g. '23:00' (FA R2)."""
    raise NotImplementedError("settings: not built yet")


def budget():
    """Return the artist budget in whole euros, e.g. 10000 (FA R4)."""
    raise NotImplementedError("settings: not built yet")


def min_artists_to_finalise():
    """Return how many booked artists a plan needs before it may be made final (FA05)."""
    raise NotImplementedError("settings: not built yet")


# ---------- times ----------

def to_minutes(time_text):
    """Turn a stored time like '16:30' into minutes since midnight, e.g. 990."""
    raise NotImplementedError("FA R2: not built yet")


def to_time_text(minutes):
    """Turn minutes since midnight back into a stored time like '16:30'."""
    raise NotImplementedError("FA R2: not built yet")


def end_time(artist_id, start_time):
    """Return the time an artist's set would finish if it started at start_time (FA02)."""
    raise NotImplementedError("FA02: not built yet")


# ---------- the catalogue ----------

def all_artists():
    """Return every artist in the catalogue as a list of dicts."""
    raise NotImplementedError("FA01: not built yet")


def get_artist(artist_id):
    """Find one artist by id. Returns the artist dict, or None if there is no such artist."""
    raise NotImplementedError("FA01: not built yet")


def all_stages():
    """Return every stage as a list of dicts."""
    raise NotImplementedError("FA01: not built yet")


def is_booked(artist_id):
    """Say whether this artist is already somewhere in the lineup (FA R1)."""
    raise NotImplementedError("FA R1: not built yet")


# ---------- the lineup ----------

def all_bookings():
    """Return every booking as a list of dicts."""
    raise NotImplementedError("FA03: not built yet")


def get_booking(booking_id):
    """Find one booking by id. Returns the booking dict, or None if there is no such booking."""
    raise NotImplementedError("FA03: not built yet")


def timetable(stage_id):
    """Return one stage's performances in time order, each with artist name, start and end (FA03)."""
    raise NotImplementedError("FA03: not built yet")


# ---------- the budget ----------

def total_fees():
    """Return the total booking fees of the current lineup, counting each artist once (FA R1)."""
    raise NotImplementedError("FA R4: not built yet")


def remaining_budget():
    """Return how much of the budget is still free (FA03)."""
    raise NotImplementedError("FA R4: not built yet")


# ---------- changing the plan ----------
# Every function below returns the reason it refused, in plain language the organiser can read.
# An empty string "" means the change was accepted (FA02).

def check_booking(artist_id, stage_id, start_time, booking_id=None):
    """Return why this performance cannot be accepted, or '' if it can.

    booking_id names the booking being replaced, so an edit does not clash with itself (FA R5).
    """
    raise NotImplementedError("FA02: not built yet")


def add_booking(artist_id, stage_id, start_time):
    """Add one performance to the lineup, or refuse and say why (FA02)."""
    raise NotImplementedError("FA02: not built yet")


def edit_booking(booking_id, stage_id, start_time):
    """Move a performance to another stage or start time, or refuse and say why (FA04)."""
    raise NotImplementedError("FA04: not built yet")


def remove_booking(booking_id):
    """Take a performance out of the lineup, releasing its slot and its fee (FA04)."""
    raise NotImplementedError("FA04: not built yet")


# ---------- draft and final ----------

def plan_status():
    """Return 'draft' or 'final' (FA05)."""
    raise NotImplementedError("FA05: not built yet")


def finalise_plan():
    """Mark the plan final, or refuse and say why (FA05)."""
    raise NotImplementedError("FA05: not built yet")


def reopen_plan():
    """Put a final plan back into draft so it can be edited again (FA05)."""
    raise NotImplementedError("FA05: not built yet")
