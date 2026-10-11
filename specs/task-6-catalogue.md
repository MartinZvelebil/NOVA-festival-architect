# Task 6 — One screen, planned like a calendar

> Branch `feature-one-screen`. **No tests exist for this task.** Write them first, in
> `tests/test_catalogue.py`, using `streamlit.testing.v1.AppTest`.
>
> Replaces the earlier "catalogue screen" task. The catalogue was built as cards during Task 2;
> what is left is to put the whole product on one page and make booking feel like dropping a
> meeting into a calendar.

## Why

Planning a festival is one loop: see the gap, fill the gap. Today the organiser has to leave the
timetable to book anybody, which means losing sight of the gap they were trying to fill, and the
budget has to be printed twice because both screens need it. On one page the empty slot and the
artist who could fill it are visible at the same time, and the lineup stops being something you
navigate to.

## What

Completes FA01 and brings FA02, FA03, FA04 and FA05 onto a single screen.

- [ ] There is one screen. The sidebar no longer switches between screens; it carries the plan's
      status and the budget, which the whole page shares instead of printing twice.
- [ ] The page is the timetable on the left and one panel on the right. The panel shows whichever
      of these applies:
      - a performance's full detail, with **Cancel**, when a block is clicked (FA01, FA04);
      - a booking form pre-filled with that stage and time, when an empty slot is clicked (FA02);
      - the catalogue, when nothing is selected (FA01).
- [ ] **Clicking an empty slot starts a booking.** The stage and start time come from where the
      organiser clicked; they pick the artist and confirm. Clicking 15:30 on Palco Serra opens a
      form that already says Palco Serra and 15:30.
- [ ] **Clicking an artist card arms that artist.** The next empty slot clicked books them
      straight away, so a booking is two clicks: artist, then slot. An armed artist is clearly
      marked, and clicking them again disarms.
- [ ] Dragging a block to another time or stage still works and still goes through
      `logic.edit_booking` (Task 4). Set lengths cannot be dragged.
- [ ] The catalogue shows every artist with genre, fee and duration. Booked artists are greyed and
      unpickable. Artists whose fee is above the remaining budget are marked with the shortfall in
      euros, and are still shown — the catalogue never hides an artist.
- [ ] Every refusal appears beside the thing that was refused, as a sentence.
- [ ] While the plan is final, the page offers nothing that changes the lineup: no slot booking,
      no dragging, no cancel. Only **Reopen as draft** (FA05).
- [ ] The screen reads everything through `logic`. It does not open a CSV and does not recalculate
      a fee or a total of its own.

## Out of scope

- **Dragging an artist from the catalogue onto the calendar.** Checked and not possible:
  `streamlit-calendar` never creates an external `Draggable`, emits no `drop` or `eventReceive`
  callback, and runs in a sandboxed iframe that a card on the Streamlit page cannot reach into.
  Arming an artist and clicking a slot is the two-click stand-in.
- Adding, editing or deleting artists. The catalogue is supplied content, edited in `seed/`.
- Searching, sorting or filtering. Eight artists fit on a screen.
- Photos, links, or anything from an external music service.

## Done when

`uv run pytest tests/test_catalogue.py` is green, with at least these checks written first:

- **One screen.** The app renders with no screen switcher, and the timetable, the catalogue and
  the budget are all reachable without navigating.
- **An accepted booking from a slot.** Arm a €1,000 artist, click an empty 15:30 slot on
  Palco Serra: the performance appears there, the budget drops by €1,000, and the artist's card
  turns greyed.
- **A rejected booking, with nothing changed.** Arm an artist and click a slot where that stage is
  already busy: the refusal names the clash, the lineup still holds the same performances, and the
  budget is unchanged.
- **Affordability is honest.** With €9,000 committed and €1,000 left, a €1,001 artist is marked
  unaffordable and names the €1 shortfall, while the €1,000 artist is not marked.
- **A final plan offers nothing.** With the plan final, no booking form and no cancel button are
  on the page, and the calendar is not editable.
- **A restart.** Reopen the app: the same timetable, the same badges, the same budget.

Commit as `Feature: one screen, planned like a calendar`.
