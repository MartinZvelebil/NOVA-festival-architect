# Task 7 — Polish and hand-in

> Branch `task-7-polish`. Nothing new is built here. This is the pass that makes the project
> readable by someone who has never seen it.

## Why

The project is graded on being understood, not only on working. A grader who clones the repo
should be able to run it with one command, see what it does, and find the rule behind any
behaviour in under a minute. Anything that makes them guess costs marks that the code already
earned.

## What

- [ ] `uv run pytest` is green from a clean clone. Every one of the 26 original tests, plus the
      ones written for Tasks 3 and 6.
- [ ] `uv run python seed.py` resets to an empty draft and the app still works afterwards.
- [ ] `README.md` says what Festival Architect is, how to run it, how to reset the data, how to
      run the tests, and carries the folder map — in the shape the course starter apps use.
- [ ] Every screen is themed: the bottle-green palette from `CLAUDE.md`, the calendar in Task 3's
      stage colours, budget numbers as metric cards. No default-blue Streamlit left anywhere.
- [ ] Every refusal in the app is a sentence an organiser would understand. No `False`, no
      exception text, no rule ID shown on screen.
- [ ] Every function has its one-line docstring, no commented-out code is left behind, and
      `logic.py` still imports nothing from Streamlit.
- [ ] Every requirement in `ASSIGNMENT.md` — FA01–FA05 and FA R1–R5 — can be pointed at a function
      in `logic.py` and a test that proves it.
- [ ] The branches are merged into main and pushed, each through its own pull request.

## Out of scope

- New features. Anything the brief lists under scope boundaries stays out: ticket sales, payments,
  real artists, multiple days, audience forecasting.
- Refactoring that makes the code shorter but harder for a beginner to read.

## Done when

- **Clean clone, one command.** Clone into an empty folder, run `uv run streamlit run app.py`, and
  the app starts with the seeded catalogue and an empty draft plan.
- **The whole suite is green** and the output is pasted into the hand-in.
- **A rejected action still changes nothing**, checked once more end to end: attempt an
  over-budget booking, a clashing move and a finalisation with three artists, then confirm
  `data/*.csv` is byte-for-byte what it was before.
- **A restart restores everything**, checked once more end to end: build a four-artist lineup,
  finalise it, stop the app, reopen it — same timetable, same budget, still final.

Commit as `Task 7: polish, docs and hand-in`.
