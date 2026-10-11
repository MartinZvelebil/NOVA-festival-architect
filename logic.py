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
    for row in db.load_table("settings"):
        if row["key"] == key:
            return row["value"]
    return ""


def opens():
    """Return the time the festival opens, e.g. '14:00' (FA R2)."""
    return setting("opens")


def closes():
    """Return the time the festival closes, e.g. '23:00' (FA R2)."""
    return setting("closes")


def budget():
    """Return the artist budget in whole euros, e.g. 10000 (FA R4)."""
    # The CSV gives us the text "10000"; every sum in the app wants a number.
    return int(setting("budget"))


def min_artists_to_finalise():
    """Return how many booked artists a plan needs before it may be made final (FA05)."""
    return int(setting("min_artists_to_finalise"))


# ---------- times ----------

def to_minutes(time_text):
    """Turn a stored time like '16:30' into minutes since midnight, e.g. 990.

    Every rule about time compares these numbers, never the text. "9:00" < "14:00" is False
    in Python, because the character "9" sorts after "1": text is not time.
    """
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)


def to_time_text(minutes):
    """Turn minutes since midnight back into a stored time like '16:30'.

    Both halves are padded to two digits, so the text we write back looks like the text we read.
    """
    hours = minutes // 60
    rest = minutes % 60
    return str(hours).rjust(2, "0") + ":" + str(rest).rjust(2, "0")


def end_time(artist_id, start_time):
    """Return the time an artist's set would finish if it started at start_time (FA02)."""
    artist = get_artist(artist_id)
    finishes = to_minutes(start_time) + int(artist["duration_min"])
    return to_time_text(finishes)


# ---------- the catalogue ----------

def all_artists():
    """Return every artist in the catalogue as a list of dicts."""
    return db.load_table("artists")


def get_artist(artist_id):
    """Find one artist by id. Returns the artist dict, or None if there is no such artist."""
    for artist in all_artists():
        # ids come out of the CSV as text, so compare them as text
        if artist["id"] == str(artist_id):
            return artist
    return None


def all_stages():
    """Return every stage as a list of dicts."""
    return db.load_table("stages")


def is_booked(artist_id):
    """Say whether this artist is already somewhere in the lineup (FA R1)."""
    for booking in all_bookings():
        if booking["artist_id"] == str(artist_id):
            return True
    return False


# ---------- the lineup ----------

def all_bookings():
    """Return every booking as a list of dicts."""
    return db.load_table("bookings")


def get_booking(booking_id):
    """Find one booking by id. Returns the booking dict, or None if there is no such booking."""
    for booking in all_bookings():
        if booking["id"] == str(booking_id):
            return booking
    return None


def timetable(stage_id):
    """Return one stage's performances in time order, each with artist name, start and end (FA03).

    Built from the saved bookings every time it is called, so the timetable and the budget
    are always two views of the same rows and cannot drift apart.
    """
    performances = []
    for booking in all_bookings():
        if booking["stage_id"] != str(stage_id):
            continue
        artist = get_artist(booking["artist_id"])
        performances.append({
            "booking_id": booking["id"],
            "artist_id": artist["id"],
            "name": artist["name"],
            "genre": artist["genre"],
            "start_time": booking["start_time"],
            "end_time": end_time(artist["id"], booking["start_time"]),
        })
    # sorted by the real minute, not by the text: "9:00" would otherwise come after "14:00"
    performances.sort(key=lambda performance: to_minutes(performance["start_time"]))
    return performances


# ---------- the budget ----------

def total_fees():
    """Return the total booking fees of the current lineup, counting each artist once (FA R1).

    Always added up from the saved bookings, never stored, so the lineup and the money
    cannot drift apart.
    """
    total = 0
    for booking in all_bookings():
        artist = get_artist(booking["artist_id"])
        total = total + int(artist["fee"])
    return total


def remaining_budget():
    """Return how much of the budget is still free (FA03)."""
    return budget() - total_fees()


# ---------- changing the plan ----------
# Every function below returns the reason it refused, in plain language the organiser can read.
# An empty string "" means the change was accepted (FA02).

def stage_name(stage_id):
    """Return the name of one stage, or the id itself if there is no such stage."""
    for stage in all_stages():
        if stage["id"] == str(stage_id):
            return stage["name"]
    return str(stage_id)


def overlaps(first_start, first_end, second_start, second_end):
    """Say whether two sets share any minute. Touching end to end is not an overlap (FA R2)."""
    return first_start < second_end and second_start < first_end


def check_booking(artist_id, stage_id, start_time, booking_id=None):
    """Return why this performance cannot be accepted, or '' if it can.

    booking_id names the booking being replaced, so an edit does not clash with itself (FA R5).
    """
    artist = get_artist(artist_id)
    starts = to_minutes(start_time)
    ends = starts + int(artist["duration_min"])

    # FA R1: one artist, one performance. The booking being edited is allowed to be that artist.
    for booking in all_bookings():
        if booking["artist_id"] != str(artist_id):
            continue
        if booking_id is not None and booking["id"] == str(booking_id):
            continue
        return artist["name"] + " is already playing at " + booking["start_time"] + " on " \
            + stage_name(booking["stage_id"]) + "."

    # FA R2: the set has to fit inside the festival day.
    if starts < to_minutes(opens()):
        return "The festival opens at " + opens() + ". " + artist["name"] \
            + " cannot start at " + start_time + "."
    if ends > to_minutes(closes()):
        return artist["name"] + " plays for " + artist["duration_min"] \
            + " minutes, so a " + start_time + " start would run to " + to_time_text(ends) \
            + ". The festival closes at " + closes() + "."

    # FA R2: one stage cannot hold two sets at once. Other stages are free to clash (FA R3).
    for booking in all_bookings():
        if booking["stage_id"] != str(stage_id):
            continue
        if booking_id is not None and booking["id"] == str(booking_id):
            continue
        other = get_artist(booking["artist_id"])
        other_starts = to_minutes(booking["start_time"])
        other_ends = other_starts + int(other["duration_min"])
        if overlaps(starts, ends, other_starts, other_ends):
            return stage_name(stage_id) + " is busy from " + booking["start_time"] + " to " \
                + to_time_text(other_ends) + " with " + other["name"] + "."

    # FA R4: the fee has to fit what is left. An edit does not pay the fee twice.
    already_paying = booking_id is not None and get_booking(booking_id) is not None \
        and get_booking(booking_id)["artist_id"] == str(artist_id)
    if not already_paying:
        fee = int(artist["fee"])
        if fee > remaining_budget():
            return artist["name"] + " costs " + str(fee) + " euro and only " \
                + str(remaining_budget()) + " euro is left."

    return ""


def add_booking(artist_id, stage_id, start_time):
    """Add one performance to the lineup, or refuse and say why (FA02)."""
    refusal = check_booking(artist_id, stage_id, start_time)
    if refusal != "":
        # Nothing is written when we refuse: the saved plan stays exactly as it was.
        return refusal
    db.append_row("bookings", {
        "id": db.next_id("bookings"),
        "artist_id": str(artist_id),
        "stage_id": str(stage_id),
        "start_time": start_time,
    })
    return ""


def edit_booking(booking_id, stage_id, start_time):
    """Move a performance to another stage or start time, or refuse and say why (FA04).

    An edit replaces the booking rather than adding one (FA R5): the artist stays the same,
    the fee is charged once, and the booking being moved is ignored while looking for clashes,
    so a set never clashes with itself.
    """
    booking = get_booking(booking_id)
    if booking is None:
        return "That performance is not in the lineup."

    refusal = check_booking(booking["artist_id"], stage_id, start_time, booking_id=booking_id)
    if refusal != "":
        # Nothing is written when we refuse: the performance stays where it was.
        return refusal

    bookings = all_bookings()
    for position in range(len(bookings)):
        if bookings[position]["id"] == str(booking_id):
            bookings[position] = {
                "id": booking["id"],
                "artist_id": booking["artist_id"],
                "stage_id": str(stage_id),
                "start_time": start_time,
            }
    db.save_table("bookings", bookings)
    return ""


def remove_booking(booking_id):
    """Take a performance out of the lineup, releasing its slot and its fee (FA04).

    The fee is not stored anywhere, so dropping the row is all it takes: total_fees adds up
    what is left, and the artist becomes bookable again.
    """
    if get_booking(booking_id) is None:
        return "That performance is not in the lineup."

    remaining = []
    for booking in all_bookings():
        if booking["id"] != str(booking_id):
            remaining.append(booking)
    db.save_table("bookings", remaining)
    return ""


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
