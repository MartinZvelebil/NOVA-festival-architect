# Festival Architect — notes for Claude

Solo project for Introduction to Programming, Nova SBE 2026/27. The requirements live in
`ASSIGNMENT.md` (Block 2, Product 03). The person asking is a **beginner** and is graded on
understanding the code, not on owning it. **Teach, don't just do.**

This project deliberately copies the shape of the two course starter apps in the parent folder
(`../splitit`, `../tiny-crm`). When something here is unclear, look at how they did it and do the
same — they are the reference implementation for every convention below.

## Running things

- Run the app: `uv run streamlit run app.py` — uv installs Python and the libraries by itself.
  Never use `pip` or `python -m venv`.
- Reset the data: `uv run python seed.py` (copies `seed/*.csv` over `data/*.csv`).
- Tests: `uv run pytest`. Run a single file with `uv run pytest tests/test_feature_1.py`.
- If `uv` is missing, install it: macOS `curl -LsSf https://astral.sh/uv/install.sh | sh`,
  Windows `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`.
  Then open a new terminal.

## Project layout

Keep this exact structure — the same three-file split as SplitIt and Tiny CRM:

```
app.py               all the Streamlit screens (entry point)
logic.py             the business rules: artists, bookings, timetable, budget, finalisation
db.py                reads and writes the CSV files: load_table, save_table, append_row, next_id
seed.py              uv run python seed.py -> resets data/ from seed/
data/*.csv           the live "database", one file per table
seed/*.csv           pristine copies of the same files
.streamlit/config.toml  the colour theme (see "How it looks")
tests/conftest.py    shared test helpers (a throwaway copy of the data for each test)
tests/test_*.py      one file per feature or bug
specs/               what to build, one file per feature
issues/              what is broken, one file per bug
ASSIGNMENT.md        the business requirements (FA01–FA05, FA R1–R5, scenarios A1–A6)
README.md            what the app is, how to run it, folder map
pyproject.toml       the libraries, pinned (uv reads this)
```

The dependency direction is one-way and must stay that way: `app.py` → `logic.py` → `db.py`.
`db.py` knows nothing about festivals; `logic.py` knows nothing about Streamlit.

- **`db.py`** — the whole database layer. A `COLUMNS` dict declares each table's columns in CSV
  order. `DATA_DIR` is built from `os.path.dirname(os.path.abspath(__file__))` so the app works no
  matter which folder you run it from. `save_table` and `append_row` use
  `csv.DictWriter(..., lineterminator="\n")`.
- **`logic.py`** — every rule from `ASSIGNMENT.md`. Constants at the top (stages, opening and
  closing time, the €10,000 budget). Validation and conflict checks live here, never in `app.py`.
- **`app.py`** — screens only: read input, call `logic`, render the result. No CSV access, no rule
  decisions. Group the screens into `show_*` functions and route at the bottom.

## Data conventions

- **Everything that comes out of a CSV is text.** Ids are `"3"`, fees are `"1200"`, times are
  `"16:00"`. Convert with `int()` / `float()` where you need numbers, and compare ids with
  `row["id"] == str(the_id)`.
- Dates and times are stored zero-padded (`"16:00"`, not `"4pm"`). Compare them as real values
  (minutes since midnight, or `datetime.time`), never as strings — string comparison of times and
  dates is exactly the bug Tiny CRM plants in `issues/002`.
- Money: keep fees whole euros as text in the CSV and convert on read. Never store a computed
  total; recompute it from the bookings so the timetable and the budget can never disagree
  (FA03, FA R4).
- `data/` is the live database and is written by the app. `seed/` is pristine and is only changed
  deliberately. Adding a column means touching three places: `COLUMNS` in `db.py`, the files in
  `seed/`, then `uv run python seed.py`. **Never edit `data/` by hand.**
- Persistence is a graded requirement (FA R5 / scenario A6): every accepted change is written to
  CSV immediately, and a rejected action leaves the files untouched.

## Code style

Match the starter apps — the grader reads this code, so plainness beats cleverness.

- Beginner-level Python: `for` loops and `if` statements over comprehensions, `lambda`, classes,
  decorators or `dataclasses`. A plain `dict` per row is the data model.
- Every module, function and test has a one-line docstring saying what it does in plain words.
- Full words for names: `remaining_budget`, not `rem_bud`. Functions are verbs
  (`book_artist`, `remove_booking`), predicates read as questions (`is_stage_free`).
- Comments explain *why*, not *what*, and only where a rule is non-obvious.
- Standard library only, plus the pinned libraries in `pyproject.toml` (`streamlit`, `pytest`,
  `streamlit-extras`, `streamlit-calendar`). Do not add a dependency without asking.
- Every function that rejects something explains why in plain language — "Stage A is busy until
  17:00", not `False` (FA02).

## How it looks

The app should look like a festival programme, not a spreadsheet. The palette is a bottle-green
bar wall, off-white print paper, one hot riso red and the amber of a hanging bulb:

| Colour | Hex | Used for |
| --- | --- | --- |
| Bottle green | `#0D4234` | the page background |
| Deep green | `#125140` | cards, sidebar, inputs |
| Riso red | `#E8432C` | buttons, links, the selected thing, Stage 1 |
| Paper | `#F3EADF` | text |
| Bulb amber | `#E9A13B` | warnings, refusals, Stage 2 |

- The four Streamlit colours live in `.streamlit/config.toml`. **Change a colour there, never in
  `app.py`.** Streamlit picks the file up by itself when you run the app.
- Red and amber are the two stage colours in the timetable. Nothing else uses them, so a colour
  always means a stage.

### Which widget to use where

- **The timetable is a `streamlit-calendar` day view**, one column per stage, 14:00 to 23:00 down
  the side. This is the main screen (FA03) and the one place a real component earns its keep.
  Docs: https://github.com/im-perativa/streamlit-calendar
- **`streamlit-extras` for polish only** — styled metric cards for the budget numbers, badges for
  "already booked". Nothing that holds state. Gallery: https://arnaudmiribel.github.io/streamlit-extras/
- **Plain Streamlit for everything else**: forms, selectboxes, lists, buttons.

Both packages are pinned in `pyproject.toml` and are hard requirements — if the calendar fails to
render, fix it, do not quietly fall back to a list. Do not add a third UI package without asking.

### The line that must not be crossed

`logic.py` never imports Streamlit and never mentions a colour, a label or a format. It returns
facts — a start time, a refusal sentence, a number of euros — and `app.py` decides how they look.
That is what keeps the tests able to check the rules without rendering anything.

## Tests

- `tests/conftest.py` holds the shared helpers: `use_temp_data(tmp_path, monkeypatch)` copies
  `seed/*.csv` into a throwaway folder and monkeypatches `db.DATA_DIR` at it, so a test can never
  touch `data/`. Every test that writes must call it first. Builder helpers (`make_artist`,
  `make_booking`) keep the tests short.
- One test file per unit of work: `test_smoke.py` (always green — the app renders, the tables load,
  seed restores), `test_bugs.py` (one test per file in `issues/`), `test_feature_N.py` (one per
  spec).
- A test states the correct behaviour and is allowed to be red until the code catches up. **Never
  edit, delete or skip a test to make it pass.** If a test looks wrong, say so and stop.
- The six acceptance scenarios in `ASSIGNMENT.md` (A1–A6) should each end up as a test. They are
  the definition of done.
- Screens are tested with `streamlit.testing.v1.AppTest.from_file(APP_FILE)` plus
  `assert not app.exception`.

## Workflow

- One task at a time, on its own branch named after it: `feature-2-timetable`,
  `bug-001-overlap`. **Never commit to main directly.**
- Commit messages follow the starters: `Fix issue 001: <what is true now>` or
  `Feature 2: <what you built>`. Subject line only.
- **Change code only when asked** to fix one specific issue or build one specific spec. Fix that
  one thing, show the diff, explain it in two sentences. Do not fix other bugs or build other
  features you notice along the way — mention them and move on.
- After every change, run the tests for that task and paste the final output. The output is the
  proof, not a sentence.
- Confirm before creating repos, pushing, opening pull requests or merging — those are shared,
  visible actions, not local edits.

## How to answer

- Every claim about the code comes with **file and line**. Show the lines; don't paraphrase a
  function that can just be read.
- When asked "where does X happen", walk the chain: the button in `app.py` → the function in
  `logic.py` → the call in `db.py`.
- Tie behaviour back to the requirement it implements: cite `FA02`, `FA R4`, `Scenario A3` from
  `ASSIGNMENT.md` rather than inventing rules. If `ASSIGNMENT.md` does not decide something, say so
  and ask instead of guessing.
- Prefer showing how to verify something (run it, click it, read the CSV) over asserting it.
