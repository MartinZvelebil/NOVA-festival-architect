"""The whole database layer: reads and writes the CSV files in data/."""
import csv
import os

# data/ sits next to this file, so the app works no matter where you run it from.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# One entry per table: the column names, in the order they appear in the CSV.
COLUMNS = {
    "artists": ["id", "name", "genre", "fee", "duration_min"],
    "stages": ["id", "name"],
    "bookings": ["id", "artist_id", "stage_id", "start_time"],
    "plan": ["id", "status"],
    "settings": ["key", "value"],
}


def table_path(table):
    """Return the full path of the CSV file behind a table name."""
    return os.path.join(DATA_DIR, table + ".csv")


def load_table(table):
    """Read every row of a table and return them as a list of dicts."""
    rows = []
    with open(table_path(table), newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            rows.append(row)
    return rows


def save_table(table, rows):
    """Overwrite a whole table with the given rows (a list of dicts)."""
    with open(table_path(table), "w", newline="", encoding="utf-8") as file:
        # lineterminator keeps the files clean when you open them in VS Code
        writer = csv.DictWriter(file, fieldnames=COLUMNS[table], lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def append_row(table, row):
    """Add one row to the end of a table without rewriting the others."""
    with open(table_path(table), "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=COLUMNS[table], lineterminator="\n")
        writer.writerow(row)


def next_id(table):
    """Return the next free id for a table: the highest existing id plus one."""
    highest = 0
    for row in load_table(table):
        if int(row["id"]) > highest:
            highest = int(row["id"])
    return highest + 1
