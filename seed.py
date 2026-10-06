"""Reset the live database: uv run python seed.py copies seed/*.csv over data/*.csv."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SEED_DIR = os.path.join(HERE, "seed")
DATA_DIR = os.path.join(HERE, "data")
TABLES = ["artists", "stages", "bookings", "plan", "settings"]


def reset(data_dir=DATA_DIR):
    """Copy every pristine CSV from seed/ into the data folder and say so."""
    for table in TABLES:
        source = os.path.join(SEED_DIR, table + ".csv")
        target = os.path.join(data_dir, table + ".csv")
        shutil.copyfile(source, target)
        print("Restored " + os.path.relpath(target, HERE) + " from seed/" + table + ".csv")
    print("Done. The plan is back to its original state.")


# This block only runs when you type `uv run python seed.py`, not when tests import the file.
if __name__ == "__main__":
    reset()
