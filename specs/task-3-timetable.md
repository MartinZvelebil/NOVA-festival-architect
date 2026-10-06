# Task 3 — The timetable and the budget

> Branch `feature-timetable`. **No tests exist for this task.** Write them first, in
> `tests/test_timetable.py`, before you touch `logic.timetable`.

## Why

A list of bookings is not a plan. The organiser needs to see the day: two stages side by side,
14:00 at the top, 23:00 at the bottom, and the gaps where nothing is playing. That picture is how
they notice that Stage 2 is empty all afternoon, which no list makes obvious. Next to it, the
money: what the lineup costs and what is left.

## What

Implements FA03.

- [ ] `logic.timetable(stage_id)` returns that stage's performances **in time order**, each one a
      dict carrying at least the artist's name, the start time and the end time. An empty stage
      returns an empty list.
- [ ] The order is by time, not by the order things were booked and not alphabetically. Booking
      18:00 first and 15:00 second still lists 15:00 first.
- [ ] The timetable screen draws both stages as a `streamlit-calendar` day view: one column per
      stage, the day running from `opens()` to `closes()`, one block per performance showing the
      artist and the times. Stage 1 is riso red, Stage 2 is bulb amber (see `CLAUDE.md`).
- [ ] The budget is shown as `streamlit-extras` metric cards: total fees and remaining budget,
      both recalculated after every accepted change.
- [ ] Both numbers are computed from the saved bookings every time. No running total is stored
      anywhere, so the timetable and the budget can never disagree.

## Out of scope

- Dragging a block to move it — the calendar can do it, but editing is Task 4 and must go through
  `logic.edit_booking` so the rules still apply.
- Printing or exporting the timetable.
- Anything per-genre or per-audience: the brief excludes audience modelling.

## Done when

`uv run pytest tests/test_timetable.py` is green, with at least these checks written first:

- **Time order, not booking order.** Book an artist at 18:00, then one at 15:00, both on Stage 1.
  `timetable("1")` returns the 15:00 one first. Each entry's end time is its start plus the
  artist's duration — a 45-minute set booked at 15:00 ends at `"15:45"`.
- **Stages are separate.** With one artist on each stage at 16:00, `timetable("1")` and
  `timetable("2")` each hold exactly one performance, and an unused stage returns `[]`.
- **The money follows the lineup.** With a €2,000 and a €1,500 artist booked, the cards read
  €3,500 spent and €6,500 left. A refused booking leaves both numbers untouched.
- **A restart.** Stop and reopen the app: the calendar draws the same blocks on the same stages,
  and the two cards show the same numbers as before.

Commit as `Feature: timetable and budget panel`.
