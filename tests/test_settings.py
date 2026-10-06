"""The rules read data/settings.csv instead of hard-coded numbers.

The acceptance tests in test_acceptance.py check the festival ASSIGNMENT.md asks for, with the
values shipped in seed/settings.csv. These tests check the other half: change a setting and the
rules move with it. Red until the settings functions and the rules that use them are built.
"""
import db
import logic
from conftest import make_artist, save_catalogue, set_setting, use_temp_data


# ---------- reading the settings ----------

def test_the_shipped_settings_are_the_ones_the_brief_asks_for(tmp_path, monkeypatch):
    """A fresh copy of the data describes the festival of ASSIGNMENT.md: 14:00-23:00, 10,000, 4."""
    use_temp_data(tmp_path, monkeypatch)
    assert logic.opens() == "14:00"
    assert logic.closes() == "23:00"
    assert logic.budget() == 10000
    assert logic.min_artists_to_finalise() == 4


def test_settings_come_back_as_numbers_where_they_are_numbers(tmp_path, monkeypatch):
    """Everything in a CSV is text, so budget() and min_artists_to_finalise() convert it."""
    use_temp_data(tmp_path, monkeypatch)
    assert isinstance(logic.setting("budget"), str)
    assert isinstance(logic.budget(), int)
    assert isinstance(logic.min_artists_to_finalise(), int)


def test_a_changed_setting_is_read_back(tmp_path, monkeypatch):
    """Editing the settings table is enough; no code change is needed to move the budget."""
    use_temp_data(tmp_path, monkeypatch)
    set_setting("budget", 4500)
    assert logic.budget() == 4500


# ---------- the rules follow the settings ----------

def test_the_budget_rule_uses_the_configured_budget(tmp_path, monkeypatch):
    """With a 3,000 euro budget, a 3,001 euro artist is refused and a 3,000 euro one is not."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="3001", duration_min="60"),
        make_artist("2", fee="3000", duration_min="60"),
    ])
    set_setting("budget", 3000)

    assert logic.add_booking("1", "1", "16:00") != ""
    assert logic.add_booking("2", "1", "16:00") == ""
    assert logic.remaining_budget() == 0


def test_the_opening_time_rule_uses_the_configured_opening(tmp_path, monkeypatch):
    """Move the opening to 12:00 and a 12:00 start becomes legal, while 11:59 does not."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="60"),
    ])
    set_setting("opens", "12:00")

    assert logic.add_booking("1", "1", "11:59") != ""
    assert logic.add_booking("2", "1", "12:00") == ""


def test_the_closing_time_rule_uses_the_configured_close(tmp_path, monkeypatch):
    """Move the close to 20:00 and a set that would run past it is refused."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="60"),
    ])
    set_setting("closes", "20:00")

    assert logic.add_booking("1", "1", "19:30") != ""
    assert logic.add_booking("2", "1", "19:00") == ""
    assert logic.end_time("2", "19:00") == "20:00"


def test_the_finalisation_rule_uses_the_configured_minimum(tmp_path, monkeypatch):
    """With the minimum set to 2, a two-artist lineup may be finalised."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="1000", duration_min="60"),
        make_artist("2", fee="1000", duration_min="60"),
    ])
    set_setting("min_artists_to_finalise", 2)

    logic.add_booking("1", "1", "16:00")
    assert logic.finalise_plan() != ""

    logic.add_booking("2", "1", "17:00")
    assert logic.finalise_plan() == ""
    assert logic.plan_status() == "final"


def test_a_longer_festival_day_makes_more_room(tmp_path, monkeypatch):
    """Opening earlier and closing later lets a set sit where it did not fit before."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="120")])

    assert logic.add_booking("1", "1", "22:00") != ""

    set_setting("closes", "23:59")
    assert logic.add_booking("1", "1", "22:00") == ""
