"""The six acceptance scenarios of ASSIGNMENT.md, one section per scenario.

These tests describe the product the brief asks for, so they are red until it is built.
Never change a test to make it pass: change the code until the test is happy.
"""
import db
import logic
from conftest import make_artist, save_catalogue, use_temp_data


def booking_of(artist_id):
    """Find the booking of one artist in the current lineup, so a test can edit or remove it."""
    for booking in logic.all_bookings():
        if booking["artist_id"] == artist_id:
            return booking
    return None


# ---------- Scenario A1: same stage conflict ----------

def test_a1_overlap_on_the_same_stage_is_rejected(tmp_path, monkeypatch):
    """A second set that starts while the first is still running is refused, with a reason."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="45"),
    ])

    assert logic.add_booking("1", "1", "16:00") == ""
    assert logic.end_time("1", "16:00") == "17:00"

    refusal = logic.add_booking("2", "1", "16:30")
    assert refusal != ""
    assert len(logic.all_bookings()) == 1


def test_a1_starting_exactly_when_the_previous_set_ends_is_allowed(tmp_path, monkeypatch):
    """No setup buffer is required: 17:00 is free the moment the 16:00-17:00 set finishes."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="45"),
    ])

    assert logic.add_booking("1", "1", "16:00") == ""
    assert logic.add_booking("2", "1", "17:00") == ""
    assert len(logic.all_bookings()) == 2


# ---------- Scenario A2: different stages ----------

def test_a2_two_artists_may_play_at_the_same_time_on_different_stages(tmp_path, monkeypatch):
    """The same start time on Stage 1 and Stage 2 is fine: only one stage at a time is the rule."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="60"),
    ])

    assert logic.add_booking("1", "1", "16:00") == ""
    assert logic.add_booking("2", "2", "16:00") == ""
    assert len(logic.all_bookings()) == 2


# ---------- Scenario A3: festival boundaries ----------

def test_a3_a_set_may_not_start_before_the_festival_opens(tmp_path, monkeypatch):
    """One minute before 14:00 is still before 14:00."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    assert logic.add_booking("1", "1", "13:59") != ""
    assert len(logic.all_bookings()) == 0


def test_a3_a_set_may_not_run_past_the_festival_close(tmp_path, monkeypatch):
    """A 60-minute set starting at 22:01 would end at 23:01, after the 23:00 close."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    assert logic.add_booking("1", "1", "22:01") != ""
    assert len(logic.all_bookings()) == 0


def test_a3_a_set_that_ends_exactly_at_the_close_is_allowed(tmp_path, monkeypatch):
    """A 60-minute set starting at 22:00 ends at 23:00, which is the last allowed minute."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    assert logic.add_booking("1", "1", "22:00") == ""
    assert logic.end_time("1", "22:00") == "23:00"


# ---------- Scenario A4: budget and duplicates ----------

def test_a4_a_booking_that_fits_the_budget_exactly_is_accepted(tmp_path, monkeypatch):
    """With 9,000 committed, a 1,000 artist spends the budget to the last euro."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="9000", duration_min="60"),
        make_artist("2", fee="1000", duration_min="60"),
    ])

    assert logic.add_booking("1", "1", "14:00") == ""
    assert logic.total_fees() == 9000
    assert logic.remaining_budget() == 1000

    assert logic.add_booking("2", "1", "15:00") == ""
    assert logic.total_fees() == logic.budget()
    assert logic.remaining_budget() == 0


def test_a4_a_booking_one_euro_over_the_budget_is_rejected(tmp_path, monkeypatch):
    """With 9,000 committed, a 1,001 artist is refused and nothing is charged."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="9000", duration_min="60"),
        make_artist("2", fee="1001", duration_min="60"),
    ])

    assert logic.add_booking("1", "1", "14:00") == ""
    assert logic.add_booking("2", "1", "15:00") != ""
    assert logic.total_fees() == 9000
    assert len(logic.all_bookings()) == 1


def test_a4_an_artist_cannot_be_booked_twice_on_any_stage(tmp_path, monkeypatch):
    """One artist, one performance: a second booking is refused even on the other stage."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", fee="1000", duration_min="60")])

    assert logic.add_booking("1", "1", "14:00") == ""
    assert logic.is_booked("1") is True

    assert logic.add_booking("1", "2", "18:00") != ""
    assert len(logic.all_bookings()) == 1
    assert logic.total_fees() == 1000


# ---------- Scenario A5: edit and remove ----------

def test_a5_a_rejected_edit_leaves_the_original_booking_untouched(tmp_path, monkeypatch):
    """Moving a set onto a busy slot is refused, and the set stays where it was."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="45"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "1", "17:00")
    second = booking_of("2")

    assert logic.edit_booking(second["id"], "1", "16:30") != ""

    unchanged = booking_of("2")
    assert unchanged["stage_id"] == "1"
    assert unchanged["start_time"] == "17:00"
    assert len(logic.all_bookings()) == 2


def test_a5_a_valid_edit_moves_the_set_without_duplicating_it(tmp_path, monkeypatch):
    """An edit replaces the booking: the artist is not booked twice and the fee is charged once."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="45"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "1", "17:00")
    second = booking_of("2")

    assert logic.edit_booking(second["id"], "2", "16:30") == ""

    moved = booking_of("2")
    assert moved["stage_id"] == "2"
    assert moved["start_time"] == "16:30"
    assert len(logic.all_bookings()) == 2
    assert logic.total_fees() == 3500


def test_a5_removing_a_booking_releases_its_slot_and_its_fee(tmp_path, monkeypatch):
    """After a removal the money comes back and another artist can take the free slot."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="60"),
    ])
    logic.add_booking("1", "1", "16:00")
    first = booking_of("1")

    assert logic.remove_booking(first["id"]) == ""
    assert logic.total_fees() == 0
    assert logic.remaining_budget() == logic.budget()
    assert logic.is_booked("1") is False

    assert logic.add_booking("2", "1", "16:00") == ""


# ---------- Scenario A6: save and finalise ----------

def finalisation_catalogue():
    """Five artists that all fit the budget and the day, used by the finalisation tests.

    Only four get booked. The spare one is there so that a refused booking can only be
    about the plan being final, never about the budget, the clock or a duplicate artist.
    """
    return [
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="60"),
        make_artist("3", fee="1000", duration_min="60"),
        make_artist("4", fee="2500", duration_min="60"),
        make_artist("5", fee="1000", duration_min="60"),
    ]


def book_artists(how_many):
    """Book that many artists back to back on Stage 1, starting when the festival opens."""
    start = logic.to_minutes(logic.opens())
    for number in range(1, how_many + 1):
        logic.add_booking(str(number), "1", logic.to_time_text(start))
        start = start + 60


def test_a6_an_accepted_booking_is_on_disk_straight_away(tmp_path, monkeypatch):
    """The lineup survives closing the app because it is written to the CSV, not kept in memory."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())

    logic.add_booking("1", "1", "16:00")

    saved = db.load_table("bookings")
    assert len(saved) == 1
    assert saved[0]["artist_id"] == "1"
    assert saved[0]["stage_id"] == "1"
    assert saved[0]["start_time"] == "16:00"
    assert logic.total_fees() == 2000


def test_a6_a_rejected_booking_changes_nothing_on_disk(tmp_path, monkeypatch):
    """A refusal leaves the saved lineup exactly as it was."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())
    logic.add_booking("1", "1", "16:00")
    before = db.load_table("bookings")

    assert logic.add_booking("2", "1", "16:30") != ""
    assert db.load_table("bookings") == before


def test_a6_three_artists_are_not_enough_to_finalise(tmp_path, monkeypatch):
    """Finalisation needs at least four booked artists, and says so when it refuses."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())
    book_artists(3)

    assert logic.finalise_plan() != ""
    assert logic.plan_status() == "draft"


def test_a6_four_valid_bookings_can_be_finalised(tmp_path, monkeypatch):
    """With four bookings and every rule passing, the plan becomes final and is saved as final."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())
    book_artists(4)

    assert logic.finalise_plan() == ""
    assert logic.plan_status() == "final"
    assert db.load_table("plan")[0]["status"] == "final"


def test_a6_a_final_plan_is_read_only(tmp_path, monkeypatch):
    """While the plan is final, nothing can be added, moved or removed."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())
    book_artists(4)
    logic.finalise_plan()
    first = booking_of("1")

    assert logic.add_booking("5", "2", "20:00") != ""
    assert logic.edit_booking(first["id"], "2", "20:00") != ""
    assert logic.remove_booking(first["id"]) != ""
    assert len(logic.all_bookings()) == 4


def test_a6_reopening_a_final_plan_makes_it_editable_again(tmp_path, monkeypatch):
    """Only an explicit reopen returns a final plan to draft."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue(finalisation_catalogue())
    book_artists(4)
    logic.finalise_plan()

    assert logic.reopen_plan() == ""
    assert logic.plan_status() == "draft"
    assert db.load_table("plan")[0]["status"] == "draft"

    first = booking_of("1")
    assert logic.remove_booking(first["id"]) == ""
