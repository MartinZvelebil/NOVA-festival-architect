# How this project was built

A record of the steps taken on Festival Architect before a single business rule was written, and
why each step came before the next. Written for my own hand-in notes, and so the order is
reproducible on the next project.

---

## Step 1 — Turn the brief into something I own

The requirements were a web page on the course site. I converted the whole page into
`ASSIGNMENT.md` inside the repo: the opportunity, the first release, the user journey, the five
capabilities (FA01–FA05), the five business rules (FA R1–R5), what must be remembered, the six
acceptance scenarios (A1–A6) and the scope boundaries, with a link back to the source.

**Why first.** Everything after this cites requirement IDs. A brief that lives in a browser tab
cannot be cited, cannot be diffed, and is not in the repo the grader clones.

## Step 2 — Study the two starter apps and write the rules down

Before writing my own code I read `splitit` and `tiny-crm` end to end — their `AGENTS.md`,
`README.md`, `db.py`, `logic.py`, `app.py`, their tests, specs and issues. They are the same app
twice, so whatever they share is the convention the course is teaching.

I distilled that into `CLAUDE.md`: the `app.py → logic.py → db.py` layering, "everything out of a
CSV is text", `data/` live versus `seed/` pristine, beginner-level Python (plain loops, a
docstring per function, no classes), one task per branch, never commit to main, never edit a test
to make it pass, and cite file and line when explaining code.

**Why.** The AI will imitate whatever it finds. Pointing it at conventions that already exist
beats inventing my own, and it keeps my project recognisable as the same family as the starters.

## Step 3 — Decide to work test-first

The acceptance criteria in the brief already read like tests — A1 names 16:30 and 17:00, A4 names
€9,000 and €1,001. The starters ship tests that are red on purpose and whose specs say "green
without changing the tests". So the criteria became the test suite, written before any rule.

**Why.** The rules interlock — the duplicate check, the overlap check, the budget check and the
"an edit is a replacement" rule all touch the same function. Without tests, fixing one silently
breaks another.

## Step 4 — Write the tests and the scaffolding they need

Branch `tests-acceptance-criteria`.

- `db.py` and `seed.py`, copied in shape from the starters: a `COLUMNS` dict, `DATA_DIR` built
  from `__file__`, `load_table` / `save_table` / `append_row` / `next_id`. No festival rules in
  them at all.
- `seed/*.csv` and `data/*.csv`: eight fictional artists with genre, fee and duration, two stages,
  an empty lineup, a draft plan.
- `tests/conftest.py`: `use_temp_data` copies the seed into a throwaway folder and monkeypatches
  `db.DATA_DIR`, so no test can ever touch `data/`. Plus builders `make_artist`, `make_stage`,
  `save_catalogue`.
- `tests/test_acceptance.py`: the six scenarios as 18 tests, using the brief's own numbers.
- `tests/test_smoke.py`: the catalogue promises, which pass immediately.
- `logic.py`: every function the tests call, as a signature whose body raises
  `NotImplementedError("FA02: not built yet")`.

**Result: 18 failed, 6 passed** — and each failure names the requirement it is waiting for, rather
than collapsing into one import error.

**One decision worth recording.** Every function that changes the plan returns *the reason it
refused*, as plain text, with `""` meaning accepted. That is FA02's "explain any reason a booking
cannot be accepted" falling straight out of the return value, and it avoids exceptions, which the
starter apps never use.

## Step 5 — Move the fixed numbers into a config file

The opening time, closing time, budget and minimum-lineup-size started as constants in `logic.py`.
I moved them into `data/settings.csv`, read through `db.py` like any other table — not a new
mechanism, so it inherits seeding, resetting and test isolation for free.

The tests were split rather than loosened: `test_acceptance.py` keeps asserting the brief's literal
numbers against the shipped settings, and a new `test_settings.py` proves the rules actually follow
the config — set the budget to 3,000 and a 3,001 artist is refused; close at 20:00 and a set
running past it is refused.

**Result: 26 failed, 7 passed.**

## Step 6 — Choose how it should look

Streamlit is not React, so a component library like shadcn/ui was never an option. I picked
Streamlit theming for the palette, `streamlit-extras` for polish, and `streamlit-calendar` for the
timetable — a festival day across two stages *is* a calendar day view, so that one component does
real work. Both packages were installed and import-checked against Streamlit 1.62 before being
pinned in `pyproject.toml`.

The palette went through two rounds. The first, taken from a photo of a bar, was a dark bottle
green with a riso red. To judge it I built a **throwaway preview** in the scratchpad — fake lineup,
hard-coded, outside the repo — rendering the calendar and the metric cards in the real colours.
Seeing it beat imagining it: the second palette, "earthy and serene" (warm sand, soil, olive,
timber brown), is the one that stayed. The preview was deleted afterwards.

The rules went into `CLAUDE.md`: colours live in `.streamlit/config.toml` and never in `app.py`,
the calendar is for the timetable only, extras is for polish only, and `logic.py` never imports
Streamlit or mentions a colour.

## Step 7 — Split the build into tasks

Using the course planning sheet (Why / What / Out of scope / Done when, with at least three checks:
an accepted action, a rejected action with unchanged data, and a restart), the work became seven
specs in `specs/`, indexed by `specs/00-task-list.md`:

| # | Task | Tests it turns green |
| --- | --- | --- |
| 1 | Settings and the clock | 3 |
| 2 | Book an artist (`first-feature.md`) | 15 |
| 3 | Timetable and budget | write them first |
| 4 | Move or remove a performance | 3 |
| 5 | Finalise and reopen | 5 |
| 6 | Catalogue screen | write them first |
| 7 | Polish and hand-in | all |

The counts were checked with `pytest --collect-only`, not estimated: 3 + 15 + 3 + 5 = the 26 red
tests exactly.

**Granularity rule.** A task is a slice you can demo, sized to one sitting. That is why "book an
artist" is one task and not four — splitting the budget check off would leave a feature that
knowingly does the wrong thing. And why the timetable is its own task despite adding no rules: the
calendar is real work.

**The order is load-bearing.** Task 1 first, because comparing times as text is the exact bug this
codebase is shaped to avoid. Task 2 before 3, because there is nothing to draw until something can
be booked. Task 4 before 5, because finalisation is a lock on top of editing.

---

## Where it stands

26 tests red on purpose, 7 green, no `app.py` yet, no rule implemented yet. The next move is Task 1.

## What I would tell someone starting the same project

1. **Put the brief in the repo first.** Everything else cites it.
2. **Read the starter apps before writing anything.** The conventions are already decided.
3. **Write the acceptance criteria as tests before any code.** They are already written as tests —
   with real numbers in them — you are only transcribing.
4. **Make failures say what they are waiting for.** Stubs that raise a named error beat an import
   error that fails everything identically.
5. **Look at the design before committing to it.** A throwaway preview with fake data costs
   minutes and saved a palette I would have disliked three tasks later.
6. **Plan the order, and write down why it is the order.** The reason is the part you forget.
