# Task 5 — Finalise and reopen

> Branch `feature-finalise`. Do Task 4 first: finalisation is a lock placed on top of editing, and
> there is nothing to lock until editing exists.

## Why

At some point the planning stops and the lineup is announced. The organiser needs a way to say
"this is the plan" and have the app stop them changing it by accident — and a deliberate way back
to draft when something falls through. A plan that silently reverts to editable after a restart is
worse than no lock at all.

## What

Implements FA05 and the second half of FA R5.

- [ ] `logic.plan_status()` returns `"draft"` or `"final"`, read from the saved plan.
- [ ] `logic.finalise_plan()` returns `""` and marks the plan final, or the reason it refused.
- [ ] It refuses while fewer than `min_artists_to_finalise()` artists are booked — four with the
      shipped settings — and says how many are missing.
- [ ] While the plan is final, `add_booking`, `edit_booking` and `remove_booking` all refuse and
      say the plan is final. Nothing about the lineup changes.
- [ ] `logic.reopen_plan()` returns the plan to draft. Only this puts a final plan back into an
      editable state; nothing else does, and nothing does it automatically.
- [ ] The status is written to `data/plan.csv`, so a final plan is still final after a restart.
- [ ] The screen shows whether the plan is draft or final, offers **Finalise** with the reason
      when it is not yet possible, and offers **Reopen as draft** when it is final.

## Out of scope

- Who finalised it, or when. No audit trail.
- Multiple saved plans, or versions of a plan.
- Publishing, exporting or sharing the final lineup.

## Done when

`uv run pytest tests/test_acceptance.py -k a6` is green — that is 6 tests, of which the two
"on disk" ones went green back in Task 2 — and so is
`uv run pytest tests/test_settings.py -k finalisation`. Five tests change colour in this task.
These also hold:

- **An accepted finalisation.** With four valid bookings, **Finalise** succeeds,
  `plan_status()` is `"final"`, and `data/plan.csv` says `final`.
- **A rejected finalisation, with nothing changed.** With three bookings, **Finalise** is refused
  with a reason, the plan is still `"draft"`, and the three bookings are untouched.
- **The lock holds.** While final, booking a fifth artist, moving an existing one and removing one
  are all refused, and the lineup still holds exactly four performances.
- **A restart does not unlock it.** Finalise, stop the app, reopen it: the plan is still final and
  still refuses edits. Only pressing **Reopen as draft** makes it editable, after which a booking
  can be removed again.
- **The rule follows the config.** Set `min_artists_to_finalise` to `2` in `data/settings.csv`:
  a two-artist lineup can now be finalised, with no code change.

Commit as `Feature: finalise and reopen the plan`.
