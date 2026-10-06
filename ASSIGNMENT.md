# Festival Architect

**NOVA SBE / Introduction to Programming · 2026/27**
Block 2 · Product 03 · Business requirements · Solo project

Turn an artist wishlist into a workable lineup.

- 2 stages · 8 artists · €10,000 budget
- Version 1.0 · 29 September 2026

---

## The opportunity

A festival organiser has a wishlist of artists but needs a lineup that can actually run. We need a planning tool that makes budget and scheduling constraints visible while allowing the organiser to experiment with the programme.

## First release

Deliver a one-day festival planner with two stages and at least eight fictional artists. The festival runs from 14:00 to 23:00 and has a €10,000 artist budget. Give each artist a name, genre, positive booking fee, and fixed positive set duration in whole minutes. Supply a catalogue that allows at least four artists to be booked within budget.

## The user journey

The organiser browses artists, selects an artist, stage, and start time, and adds a performance. They inspect the timetable and remaining budget, move or remove bookings, and return later to continue planning. When the lineup is ready, they mark the plan as final.

## Required capabilities

| ID | Capability | Description |
| --- | --- | --- |
| FA01 | Browse artists | Show each artist's genre, fee, and set duration before booking. Clearly identify artists already booked. |
| FA02 | Schedule a performance | Let the organiser select a stage and start time. Calculate the end time from the artist's duration and explain any reason a booking cannot be accepted. |
| FA03 | Review the plan | Show performances by stage in time order, including start and end times. Show total artist fees and remaining budget after every accepted change. |
| FA04 | Revise a booking | Allow changes to a performance's stage or start time and allow removal. Reject an invalid edit without losing the previous valid booking. |
| FA05 | Finalise and reopen | Allow finalisation only when at least four artists are booked and all rules pass. A final plan is read-only until the organiser explicitly reopens it as a draft. |

## Business rules

| ID | Rule | Description |
| --- | --- | --- |
| FA R1 | Artist availability | An artist may be booked at most once in the festival. Booking fees are charged once per booked artist. Removing a booking releases its full fee. |
| FA R2 | Time and stage | Each performance must start at or after 14:00 and end at or before 23:00. Performances cannot overlap on the same stage. A performance may begin exactly when the previous one ends; no setup buffer is required. |
| FA R3 | Simultaneous performances | Different artists may perform at the same time on different stages. The first release does not model audience clashes or artist travel. |
| FA R4 | Budget | Total booking fees cannot exceed €10,000. A booking that would exceed the budget is rejected. Spending exactly the full budget is allowed. |
| FA R5 | Valid edits | Evaluate edits as replacements of the original booking, not as additional bookings. Final plans cannot be edited or have bookings added or removed until reopened. |

## What the product must remember

Keep the artist catalogue and stage details. Save each booked artist, stage, and start time, together with whether the plan is draft or final. The timetable and budget totals must remain consistent with the saved bookings after reopening the app.

## Acceptance criteria

### Scenario A1 — Same stage conflict
Book an artist on Stage A from 16:00 to 17:00. A second artist from 16:30 to 17:15 on Stage A is rejected; starting at 17:00 is accepted if other constraints pass.

### Scenario A2 — Different stages
Book different artists at 16:00 on Stage A and Stage B. Both bookings are accepted if the budget and time limits permit them.

### Scenario A3 — Festival boundaries
For a 60-minute set, a start at 13:59 or 22:01 is rejected. A start at 22:00 is allowed if the stage is free and the budget permits it.

### Scenario A4 — Budget and duplicates
With €9,000 already committed, a €1,000 artist is accepted and a €1,001 artist is rejected. Trying to book an artist already in the lineup is rejected regardless of stage.

### Scenario A5 — Edit and remove
Attempt a conflicting edit and verify the original booking remains. Make a valid edit without duplicating the artist or fee. Remove a booking and verify its slot and fee are released.

### Scenario A6 — Save and finalise
Reopen the app and verify the lineup and totals persist. Finalisation with three artists is rejected; with four valid bookings it succeeds. The plan stays read-only after reopening the app until explicitly returned to draft.

## Scope boundaries

Ticket sales, real artist bookings, payments, external music services, multiple days, and audience forecasting are not required. These can inform later extensions.

Accepted changes must survive restarting the app. Rejected actions leave existing data unchanged. The core experience works with supplied content and without a paid service or live external integration.

> Read the shared overview for course expectations. These scenarios are product acceptance checks, not the exam question template.

---

Source: <https://nova-sbe-introduction-to-programming.github.io/intro-to-programming-2026/weeks/week-05/03-festival-architect-brd.html>
