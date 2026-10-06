# Task 4 — Move or remove a performance

> Branch `feature-revise-booking`.

## Why

Planning is rearranging. The organiser books an artist at 16:00, then realises the headliner needs
that slot, and has to move the first one without losing it. The dangerous part is that a move is
not a new booking: if the app treats it as one, the artist is suddenly booked twice and charged
twice. An edit has to be evaluated as a *replacement* of what is already there.

## What

Implements FA04 and FA R5.

- [ ] `logic.edit_booking(booking_id, stage_id, start_time)` moves an existing performance to
      another stage, another start time, or both. It returns `""` when accepted, or the reason it
      refused.
- [ ] An edit is checked as a replacement: the booking being moved is ignored when looking for
      clashes, so moving a set five minutes later does not clash with itself.
- [ ] A refused edit changes nothing. The performance stays on the stage and at the time it was.
- [ ] An accepted edit never duplicates the artist and never charges the fee twice. The number of
      bookings and the total fees are the same before and after.
- [ ] `logic.remove_booking(booking_id)` takes a performance out: its slot becomes free for
      another artist, its full fee returns to the budget, and the artist can be booked again.
- [ ] The screen offers both: pick a performance, change its stage or start time, or delete it.
      A refusal is shown as a sentence, next to the booking that did not move.

## Out of scope

- Undo, or a history of changes.
- Moving two performances in one action, or swapping two artists' slots.
- Editing which artist a performance is for — remove it and book the other one.

## Done when

`uv run pytest tests/test_acceptance.py -k a5` is green (3 tests), and these hold in the app:

- **An accepted move.** Two artists on Stage 1, at 16:00 (60 min) and 17:00 (45 min). Move the
  second to Stage 2 at 16:30: accepted. It is now on Stage 2 at 16:30, there are still exactly 2
  performances, and the total fees are unchanged — €3,500 for a €2,000 and a €1,500 artist.
- **A rejected move, with nothing changed.** From that same start, move the 17:00 set to 16:30 on
  Stage 1: refused, because the 16:00 set runs until 17:00. The booking is still on Stage 1 at
  17:00, and there are still 2 performances.
- **A removal releases both.** Remove the 16:00 set: the total fees drop by exactly its fee, the
  remaining budget returns to the full €10,000 when it was the only booking, that artist can be
  booked again, and another artist can now take Stage 1 at 16:00.
- **A restart.** Make a move and a removal, stop the app, reopen it: the moved set is on its new
  stage and time, the removed one is gone, and the budget matches.

Commit as `Feature: move and remove a performance`.
