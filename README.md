# Festival Architect

Festival Architect turns an artist wishlist into a lineup that can actually run. One festival day,
two stages, eight artists and a €10,000 budget: pick an artist up from the catalogue, drop them
into a free slot on the timetable, and the app either books them or explains, in a sentence, why
it cannot. When at least four artists are booked, the plan can be made final — and a final plan is
read-only until it is explicitly reopened as a draft.

It is a solo project for Introduction to Programming, Nova SBE 2026/27 (Block 2, Product 03). The
business requirements it is built against are in `ASSIGNMENT.md`.

## Run it

Open the folder in a terminal, then:

```
uv run streamlit run app.py
```

That one command installs Python and the libraries the first time (a minute), then starts the app.
No `uv`? Install it once — macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`, Windows:
`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` — and open a
new terminal.

## Reset the data

The app writes to the CSV files in `data/` as you plan. To get the empty draft back:

```
uv run python seed.py
```

It copies the pristine CSVs from `seed/` over `data/` and tells you what it restored.

## Run the tests

```
uv run pytest
```

All of them are green. A single file runs with `uv run pytest tests/test_acceptance.py`.

## How you use it

1. **Browse the catalogue** at the bottom of the page: genre, fee and set length on every card,
   with the already-booked artists greyed out.
2. **Pick an artist up**, then click a free slot in the timetable. They play on that stage, from
   that time, for as long as their set lasts. Clicking a free slot first and choosing the artist
   there works too.
3. **Move a performance** by dragging it to another time or another stage; **click it** to see the
   artist behind it and to cancel it. Cancelling gives the fee back.
4. **Watch the sidebar**: artists booked, artist fees and budget left are recomputed from the
   saved bookings after every accepted change.
5. **Finalise the lineup** from the sidebar once four artists are booked. Reopen it as a draft to
   change it again.

Anything that breaks a rule is refused with a sentence an organiser can read — "Palco Tejo is busy
from 16:00 to 17:00 with Luna Vermelha." — and nothing is written.

## Folder map

```
app.py               all the Streamlit screens (start here)
logic.py             the business rules: artists, bookings, timetable, budget, finalisation
db.py                reads and writes the CSV files: load_table, save_table, append_row, next_id
seed.py              uv run python seed.py -> resets data/ from seed/
data/artists.csv     the live "database", one file per table
data/stages.csv
data/bookings.csv
data/plan.csv
data/settings.csv
seed/                pristine copies of those five files
.streamlit/config.toml  the colour theme
tests/conftest.py    shared test helpers (a throwaway copy of the data for each test)
tests/test_smoke.py      always green: the app renders, the tables load, seed restores
tests/test_settings.py   the festival day, the budget and the finalisation rule come from settings
tests/test_acceptance.py the six acceptance scenarios A1-A6 of ASSIGNMENT.md
tests/test_timetable.py  the timetable and the budget panel
tests/test_catalogue.py  the one-screen catalogue, the calendar and the messages
specs/               what to build, one file per task (start with specs/00-task-list.md)
issues/              what is broken, one file per bug
ASSIGNMENT.md        the business requirements (FA01-FA05, FA R1-R5, scenarios A1-A6)
CLAUDE.md            notes for the AI assistant: how to run things, the conventions
pyproject.toml       the libraries, pinned (uv reads this)
```

## Where each requirement lives

Every rule in `ASSIGNMENT.md` is one function in `logic.py` and at least one test.

| Requirement | The rule in `logic.py` | A test that proves it |
| --- | --- | --- |
| FA01 Browse artists | `all_artists`, `is_booked` | `test_catalogue.py::test_an_artist_over_the_budget_names_the_shortfall` |
| FA02 Schedule a performance | `check_booking`, `add_booking`, `end_time` | `test_acceptance.py::test_a1_overlap_on_the_same_stage_is_rejected` |
| FA03 Review the plan | `timetable`, `total_fees`, `remaining_budget` | `test_timetable.py::test_the_timetable_is_in_time_order_not_booking_order` |
| FA04 Revise a booking | `edit_booking`, `remove_booking` | `test_acceptance.py::test_a5_removing_a_booking_releases_its_slot_and_its_fee` |
| FA05 Finalise and reopen | `can_finalise`, `finalise_plan`, `reopen_plan` | `test_acceptance.py::test_a6_four_valid_bookings_can_be_finalised` |
| FA R1 Artist availability | `is_booked`, the duplicate check in `check_booking` | `test_acceptance.py::test_a4_an_artist_cannot_be_booked_twice_on_any_stage` |
| FA R2 Time and stage | `to_minutes`, `overlaps`, the day check in `check_booking` | `test_acceptance.py::test_a3_a_set_that_ends_exactly_at_the_close_is_allowed` |
| FA R3 Simultaneous performances | the stage filter in `check_booking` | `test_acceptance.py::test_a2_two_artists_may_play_at_the_same_time_on_different_stages` |
| FA R4 Budget | `remaining_budget`, the fee check in `check_booking` | `test_acceptance.py::test_a4_a_booking_one_euro_over_the_budget_is_rejected` |
| FA R5 Valid edits | `edit_booking` (replacement, not addition), `is_final` | `test_acceptance.py::test_a5_a_rejected_edit_leaves_the_original_booking_untouched` |

## How it is built

The dependency direction is one-way: `app.py` → `logic.py` → `db.py`. `db.py` knows nothing about
festivals, `logic.py` knows nothing about Streamlit, and `app.py` decides nothing about the rules.
That is what lets the tests check every rule without rendering a screen.

Good to know: everything that comes out of a CSV file is text. Ids are `"3"`, not `3`; fees are
`"1200"`, not `1200`; times are `"16:00"`. Convert with `int()` when you need a number, and compare
times as minutes since midnight (`logic.to_minutes`), never as text — `"9:00" < "14:00"` is False
in Python, because the character `9` sorts after `1`.
