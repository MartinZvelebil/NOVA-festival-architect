"""specs/task-3-timetable.md: the timetable and the budget panel (FA03).

Written before the code, so they are red until logic.timetable exists.
"""
import db
import logic
from conftest import APP_FILE, make_artist, save_catalogue, use_temp_data


def names_in(rows):
    """Return just the artist names of a timetable, to make comparisons short."""
    names = []
    for row in rows:
        names.append(row["name"])
    return names


# ---------- time order ----------

def test_the_timetable_is_in_time_order_not_booking_order(tmp_path, monkeypatch):
    """An 18:00 set booked first still comes after a 15:00 set booked second."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="45"),
        make_artist("3", duration_min="30"),
    ])
    logic.add_booking("1", "1", "18:00")
    logic.add_booking("2", "1", "15:00")
    logic.add_booking("3", "1", "16:30")

    assert names_in(logic.timetable("1")) == ["Artist 2", "Artist 3", "Artist 1"]


def test_each_entry_carries_its_start_and_end(tmp_path, monkeypatch):
    """A 45-minute set booked at 15:00 runs to 15:45, and the timetable says so."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="45")])
    logic.add_booking("1", "1", "15:00")

    performance = logic.timetable("1")[0]
    assert performance["name"] == "Artist 1"
    assert performance["start_time"] == "15:00"
    assert performance["end_time"] == "15:45"


# ---------- stages are separate ----------

def test_each_stage_holds_only_its_own_performances(tmp_path, monkeypatch):
    """Two artists at 16:00 on different stages appear one per stage, not two on either."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="60"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "2", "16:00")

    assert names_in(logic.timetable("1")) == ["Artist 1"]
    assert names_in(logic.timetable("2")) == ["Artist 2"]


def test_an_empty_stage_has_an_empty_timetable(tmp_path, monkeypatch):
    """A stage nobody plays on returns no performances at all, not None."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])
    logic.add_booking("1", "1", "16:00")

    assert logic.timetable("2") == []


# ---------- the money follows the lineup ----------

def test_the_totals_follow_the_booked_artists(tmp_path, monkeypatch):
    """A 2,000 and a 1,500 artist make 3,500 spent and 6,500 left."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="60"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "2", "16:00")

    assert logic.total_fees() == 3500
    assert logic.remaining_budget() == 6500


def test_a_refused_booking_leaves_the_totals_alone(tmp_path, monkeypatch):
    """A clash changes neither the timetable nor the money."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="60"),
    ])
    logic.add_booking("1", "1", "16:00")

    assert logic.add_booking("2", "1", "16:30") != ""
    assert names_in(logic.timetable("1")) == ["Artist 1"]
    assert logic.total_fees() == 2000
    assert logic.remaining_budget() == 8000


# ---------- the screen ----------

def test_the_timetable_survives_a_restart(tmp_path, monkeypatch):
    """The timetable is built from the saved bookings, so it is the same after reopening."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="45"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "2", "17:00")
    before = [logic.timetable("1"), logic.timetable("2"), logic.total_fees()]

    # nothing is held in memory: reading the tables again is what reopening the app does
    assert db.load_table("bookings") != []
    after = [logic.timetable("1"), logic.timetable("2"), logic.total_fees()]
    assert after == before


def test_the_lineup_screen_renders(tmp_path, monkeypatch):
    """The timetable screen runs from top to bottom without raising."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])
    logic.add_booking("1", "1", "16:00")

    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(APP_FILE)
    app.run()
    app.sidebar.radio[0].set_value("The lineup").run()
    assert not app.exception
    assert app.title[0].value == "The lineup"
