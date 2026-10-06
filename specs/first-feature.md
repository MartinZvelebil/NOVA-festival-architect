# Task 2 — Book an artist onto a stage (first feature)

> Branch `feature-book-an-artist`. This is the course's "first feature" planning sheet. It is the
> one workflow the whole product is built around: everything later either shows this, undoes this,
> or locks this.

## Before writing the spec

- **Product and user.** Festival Architect. The festival organiser, planning a one-day lineup.
- **Trigger.** They pick an artist, a stage and a start time, and press **Add performance**.
- **Before.** The artist catalogue and the two stages must already exist, each artist with a fee
  and a set duration; the festival's hours and budget must be readable from the settings.
- **Rule.** Refuse when the artist is already booked (FA R1), when the set would start before
  14:00 or end after 23:00 (FA R2), when that stage is busy for any part of the set (FA R2), or
  when the fee would push total fees past €10,000 (FA R4).
- **After.** The performance is in the lineup, its fee is counted once, and the remaining budget
  drops by the fee. A refusal changes nothing at all.
- **Restart.** The lineup and the totals are exactly as they were, because every accepted booking
  was written to `data/bookings.csv` at the moment it was accepted.

## Why

The organiser can turn a wishlist into a plan that could actually run. They see what each artist
costs and how long they play, put one on a stage at a time, and get told — in a sentence they can
act on — whenever the festival's own rules will not allow it. Without this, the app is a list of
artists and nothing else.

## What

Implements FA01 (in its plain form), FA02, and the rules FA R1, FA R2, FA R3 and FA R4.

- [ ] `logic.all_bookings()` returns the lineup; `logic.get_booking(booking_id)` returns one
      booking or `None`.
- [ ] `logic.is_booked(artist_id)` says whether an artist is already somewhere in the lineup.
- [ ] `logic.total_fees()` adds up the fees of the booked artists, counting each artist once, and
      `logic.remaining_budget()` is the budget minus that total.
- [ ] `logic.check_booking(artist_id, stage_id, start_time, booking_id=None)` returns **the reason
      it refuses, as a sentence the organiser can read**, or `""` when the performance is allowed.
      It checks, in this order: the artist is not already booked (FA R1); the set starts at or
      after `opens()` and ends at or before `closes()` (FA R2); the stage is free for the whole
      set (FA R2); the fee fits the remaining budget (FA R4).
- [ ] `logic.add_booking(artist_id, stage_id, start_time)` returns the same kind of answer: `""`
      and the booking is saved, or a reason and **nothing is written**.
- [ ] A set may begin exactly when the previous one ends. No setup buffer (FA R2).
- [ ] Two artists may play at the same time on different stages (FA R3).
- [ ] `app.py` exists: a screen that lists every artist with genre, fee and duration, marks the
      ones already booked, offers the artist / stage / start-time form, and prints the refusal
      sentence when there is one. A plain list of the lineup is enough for now.

## Out of scope

- The calendar timetable and the styled budget panel — Task 3.
- Moving or removing a performance once added — Task 4.
- Finalising the plan — Task 5.
- Any check on whether the lineup is *good*: clashes of genre, headliner slots, gaps between sets.

## Done when

`uv run pytest tests/test_acceptance.py tests/test_settings.py` goes from 15 failures to 0, and
these hold by hand in the running app:

- **An accepted booking.** An artist booked on Stage 1 at 16:00 appears in the lineup, and the
  remaining budget drops by exactly that artist's fee. A 60-minute artist booked at 22:00 is
  accepted, because the set ends at 23:00 — the last allowed minute.
- **A rejected booking, with nothing changed.** With a 60-minute set already running 16:00–17:00
  on Stage 1, a second artist at 16:30 on Stage 1 is refused with a reason naming the clash, and
  the lineup still holds exactly one performance. The same artist at 17:00 is accepted.
- **Each rule refuses on its own terms.** A start at 13:59 is refused (before the gates). A
  60-minute set at 22:01 is refused (ends 23:01, after the close). With €9,000 committed, a
  €1,000 artist is accepted and a €1,001 artist is refused. An artist already in the lineup is
  refused even on the other stage, and the total fees do not move.
- **A restart.** Book two artists, stop the app, start it again: both are still there, on the same
  stages at the same times, and the remaining budget is the same number as before. Refuse a
  booking, restart, and the refused one is still absent.

Commit as `Feature: book an artist onto a stage`.
