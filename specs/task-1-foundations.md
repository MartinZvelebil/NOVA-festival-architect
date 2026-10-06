# Task 1 — Settings and the clock

> Branch `task-1-foundations`. No screen in this task: it is the arithmetic every later rule
> stands on. Build it first and the rest of the project stops being about dates.

## Why

Every rule in the brief is a comparison between two moments — does this set start after the gates
open, does it end before the close, does it run into the set already on that stage. Stored times
are text, and comparing text is not comparing time: in Python `"9:00" < "14:00"` is `False`,
because the character `"9"` sorts after `"1"`. Until the app turns a time into a number, every
scheduling rule built on top of it is quietly wrong. The festival's numbers also belong in
`data/settings.csv`, so the budget or the closing time can change without touching the code.

## What

Implements the settings layer plus the time arithmetic used by FA R2 and FA R4.

- [ ] `logic.setting(key)` returns one value from the `settings` table, as the text it is stored as.
- [ ] `logic.opens()` and `logic.closes()` return the festival's opening and closing time as text
      (`"14:00"`, `"23:00"` with the shipped settings).
- [ ] `logic.budget()` and `logic.min_artists_to_finalise()` return **whole numbers**
      (`10000` and `4`), because everything that comes out of a CSV is text until you convert it.
- [ ] `logic.to_minutes(time_text)` turns `"16:30"` into `990`, the number of minutes since
      midnight.
- [ ] `logic.to_time_text(minutes)` turns `990` back into `"16:30"`, always two digits for the
      hour and two for the minutes.
- [ ] `logic.all_artists()` returns the catalogue, and `logic.get_artist(artist_id)` returns one
      artist by id, or `None` when there is no such artist.
- [ ] `logic.end_time(artist_id, start_time)` returns when that artist's set would finish:
      the start plus the artist's `duration_min`.
- [ ] Changing a value in `data/settings.csv` changes what these functions return. Nothing reads
      the budget or the opening time from anywhere else, ever.

## Out of scope

- Any booking, any rule, any refusal. Nothing yet decides whether a performance is allowed.
- Any screen. `app.py` does not exist at the end of this task.
- Times that cross midnight. The festival opens and closes on the same day.

## Done when

`uv run pytest tests/test_settings.py` has its first three tests green, and these hold:

- **Reads the shipped festival.** `logic.opens()` is `"14:00"`, `logic.closes()` is `"23:00"`,
  `logic.budget()` is the number `10000`, `logic.min_artists_to_finalise()` is the number `4`.
- **Converts both ways.** `logic.to_minutes("16:30")` is `990`, `logic.to_time_text(990)` is
  `"16:30"`, and `logic.to_time_text(logic.to_minutes("09:05"))` is `"09:05"` — the padding
  survives the round trip.
- **Adds a duration.** For a 60-minute artist, `logic.end_time(artist_id, "22:00")` is `"23:00"`.
  For a 45-minute artist starting at `"16:30"`, it is `"17:15"`.
- **Follows the config.** Change `budget` to `4500` in `data/settings.csv`, and `logic.budget()`
  returns `4500` with no code change. Run `uv run python seed.py` and it is `10000` again.

Commit as `Task 1: read the settings and do the time arithmetic`.
