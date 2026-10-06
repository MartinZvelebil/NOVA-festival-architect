"""These tests should always pass. If one fails, something is wrong with the data, not the rules.

They check the "first release" promises of ASSIGNMENT.md: two stages, at least eight artists,
and a catalogue where at least four of them fit inside the 10,000 euro budget.
"""
import os

import db
import seed
from conftest import REPO, TABLES, use_temp_data


def test_tables_load_with_the_right_columns():
    """The four CSV tables open and have the columns db.py says they have."""
    for table in TABLES:
        rows = db.load_table(table)
        if table != "bookings":
            assert len(rows) > 0
        for row in rows:
            assert list(row.keys()) == db.COLUMNS[table]


def test_the_catalogue_has_eight_artists_and_two_stages():
    """ASSIGNMENT.md asks for at least eight fictional artists on two stages."""
    assert len(db.load_table("artists")) >= 8
    assert len(db.load_table("stages")) == 2


def test_every_artist_has_a_positive_fee_and_duration():
    """A fee and a set length in whole minutes, both above zero, for every artist."""
    for artist in db.load_table("artists"):
        assert artist["name"] != ""
        assert artist["genre"] != ""
        assert int(artist["fee"]) > 0
        assert int(artist["duration_min"]) > 0


def test_four_artists_fit_inside_the_budget():
    """The four cheapest artists together cost 10,000 euro or less, so a lineup is possible."""
    fees = []
    for artist in db.load_table("artists"):
        fees.append(int(artist["fee"]))
    fees.sort()
    budget = 0
    for row in db.load_table("settings"):
        if row["key"] == "budget":
            budget = int(row["value"])
    assert sum(fees[:4]) <= budget


def test_the_settings_table_holds_the_numbers_of_the_brief():
    """seed/settings.csv ships the festival ASSIGNMENT.md describes, one row per setting."""
    values = {}
    for row in db.load_table("settings"):
        values[row["key"]] = row["value"]
    assert values["opens"] == "14:00"
    assert values["closes"] == "23:00"
    assert values["budget"] == "10000"
    assert values["min_artists_to_finalise"] == "4"


def test_the_plan_starts_as_an_empty_draft():
    """A fresh copy of the data has no bookings and a plan in draft."""
    assert db.load_table("bookings") == []
    plan = db.load_table("plan")
    assert len(plan) == 1
    assert plan[0]["status"] == "draft"


def test_seed_restores_the_data(tmp_path, monkeypatch):
    """After changing the data, seed.reset puts every table back exactly as it was."""
    use_temp_data(tmp_path, monkeypatch)
    db.append_row("bookings", {
        "id": "1", "artist_id": "1", "stage_id": "1", "start_time": "16:00",
    })
    assert len(db.load_table("bookings")) == 1

    seed.reset(str(tmp_path))

    for table in TABLES:
        with open(os.path.join(REPO, "seed", table + ".csv"), encoding="utf-8") as file:
            pristine = file.read()
        with open(os.path.join(tmp_path, table + ".csv"), encoding="utf-8") as file:
            restored = file.read()
        assert restored == pristine
