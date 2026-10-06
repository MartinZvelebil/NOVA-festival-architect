"""Shared test setup. pytest loads this file automatically before the tests."""
import os
import shutil
import sys

# The tests live in tests/ and the app one folder up, so make the app importable.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

import db

APP_FILE = os.path.join(REPO, "app.py")
TABLES = ["artists", "stages", "bookings", "plan", "settings"]


def use_temp_data(tmp_path, monkeypatch):
    """Copy seed/*.csv into a throwaway folder and point db at it, so data/ is never touched."""
    for table in TABLES:
        source = os.path.join(REPO, "seed", table + ".csv")
        shutil.copyfile(source, os.path.join(tmp_path, table + ".csv"))
    monkeypatch.setattr(db, "DATA_DIR", str(tmp_path))


def make_artist(artist_id, fee="1000", duration_min="60", genre="pop"):
    """Build one artist row for a test, with only the fields that matter passed in."""
    return {
        "id": artist_id,
        "name": "Artist " + artist_id,
        "genre": genre,
        "fee": fee,
        "duration_min": duration_min,
    }


def make_stage(stage_id):
    """Build one stage row for a test."""
    return {"id": stage_id, "name": "Stage " + stage_id}


def save_catalogue(artists, stages=2):
    """Replace the catalogue with these artists and that many stages, and start from an empty draft.

    Use this instead of the seed data whenever a test needs particular fees or durations.
    """
    db.save_table("artists", artists)
    stage_rows = []
    for number in range(1, stages + 1):
        stage_rows.append(make_stage(str(number)))
    db.save_table("stages", stage_rows)
    db.save_table("bookings", [])
    db.save_table("plan", [{"id": "1", "status": "draft"}])


def set_setting(key, value):
    """Change one setting in the throwaway copy of settings.csv, leaving the others alone.

    Use it to prove a rule reads the config; the acceptance tests keep the shipped values.
    """
    rows = db.load_table("settings")
    for row in rows:
        if row["key"] == key:
            row["value"] = str(value)
    db.save_table("settings", rows)


def ids_of(rows):
    """Return just the ids of a list of rows, to make comparisons short."""
    ids = []
    for row in rows:
        ids.append(row["id"])
    return ids


def booking_ids(rows):
    """Return the artist ids of a list of bookings, in the order given."""
    artist_ids = []
    for row in rows:
        artist_ids.append(row["artist_id"])
    return artist_ids
