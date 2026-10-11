# How I built Festival Architect

A one-page account of the order I worked in and why. The long version, with every detail, is in
git history at commit `842c763`.

---

## The order I worked in

1. **Put the brief in the repo.** I converted the course web page into `ASSIGNMENT.md`, so every
   later decision could cite a requirement ID instead of a browser tab.
2. **Read the two starter apps first.** `splitit` and `tiny-crm` are the same app twice, so what
   they share is the convention the course teaches. I wrote it down in `CLAUDE.md`: the
   `app.py → logic.py → db.py` layering, "everything out of a CSV is text", one task per branch,
   never edit a test to make it pass.
3. **Decided to work test-first.** The brief's acceptance criteria are already tests — scenario A4
   names €9,000 and €1,001 — so writing them as tests was transcription, not design.
4. **Wrote the tests before any rule.** 18 acceptance tests, the `db.py`/`seed.py` scaffolding, and
   a `logic.py` of stubs raising `NotImplementedError("FA02: not built yet")`, so each failure said
   what it was waiting for. **18 failed, 6 passed** — the red baseline.
5. **Moved the fixed numbers into `data/settings.csv`**, read through `db.py` like any other table.
   I split the tests rather than loosen them: the acceptance tests keep the brief's literal
   numbers, and new tests prove the rules follow the config.
6. **Chose how it should look.** Streamlit theming, `streamlit-extras`, and `streamlit-calendar`
   for the timetable. I built a throwaway preview with fake data to judge the palette — and
   replaced my first choice after seeing it.
7. **Split the build into seven task specs**, each in the course's Why / What / Out of scope /
   Done when format, ordered so nothing is blocked: time arithmetic first, because comparing times
   as text is the bug this codebase exists to avoid.

## Building it

Each task was its own branch, its own red-to-green run, its own pull request.

| Task | What it added | Suite after |
| --- | --- | --- |
| 1 Settings and the clock | `to_minutes`, the settings readers, `end_time` | 10 passed |
| 2 Book an artist | the four rules, `add_booking`, the first `app.py` | 24 passed |
| 3 Timetable and budget | `logic.timetable`, the calendar day view | 32 passed |
| 4 Move or remove | `edit_booking`, `remove_booking`, drag-to-move | 37 passed |
| 5 Finalise and reopen | the draft/final lock on every change | **45 — all green** |
| 6 One screen | the whole product on one page | 56 passed |
| 7 Polish and hand-in | README, the requirement map | 60 passed |

Task 5 is where every test I wrote in step 4, before a single rule existed, finally passed.

## What the build taught me

- **I redesigned the interface eight times**, each after opening it and disliking something. All of
  it was `app.py`; my 45 logic tests never had to care. That is what the layering buys.
- **My best decision was a question.** I asked why the app was on two screens. There was no good
  answer — I had copied the split from the starter apps, not from my brief — so I had Task 6's spec
  rewritten and the app became one page.
- **A stale import looks exactly like a bug.** I reported a `NotImplementedError` for code that was
  already written; my Streamlit process had kept the old module. Restarting fixed it.
- **Timezones hid inside a click.** `dateClick` returns UTC, so every slot I clicked would have
  been booked an hour out. Pinning the calendar to `timeZone: "UTC"` fixed it, caught by reading
  the component's source before shipping.
- **Not everything I ask for is possible.** Dragging an artist card onto the calendar cannot work —
  the component runs in a sandboxed iframe. Picking an artist up and clicking a slot is the
  stand-in, and the reason is in the spec so it does not read like something forgotten.

## Three tests I changed, and why

`CLAUDE.md` forbids editing a test to make it pass. I changed three, deciding each one deliberately:

1. **Deleted** a test whose arithmetic was impossible (a 120-minute set from 22:00 ends at 24:00),
   and which duplicated another.
2. **Pointed** the "plan starts empty" test at `seed/` instead of the live `data/`, which went red
   the moment I booked my first artist.
3. **Updated** the two-screen render test after I removed the two-screen design.

The rule I want to keep: edit a test when it describes something false or something I no longer
intend — never when it is merely in the way.

## Where it stands

Seven tasks, nine pull requests, **60 tests passing**. About 1,000 lines of Python, of which
`logic.py` is 357 and imports no Streamlit.

## Where each requirement lives

Every ID in `ASSIGNMENT.md`, the function that decides it, and the test that proves it. A
requirement I cannot point a function at is one I did not build.

| Requirement | Decided in | Proved by |
| --- | --- | --- |
| FA01 Browse artists | `app.py show_artist_card`; `logic.is_booked` | `test_catalogue.py::test_an_artist_over_the_budget_names_the_shortfall` |
| FA02 Schedule a performance | `logic.check_booking`, `logic.add_booking`, `logic.end_time` | `test_acceptance.py::test_a1_overlap_on_the_same_stage_is_rejected` |
| FA03 Review the plan | `logic.timetable`, `logic.total_fees`, `logic.remaining_budget` | `test_timetable.py::test_the_timetable_is_in_time_order_not_booking_order` |
| FA04 Revise a booking | `logic.edit_booking`, `logic.remove_booking` | `test_acceptance.py::test_a5_removing_a_booking_releases_its_slot_and_its_fee` |
| FA05 Finalise and reopen | `logic.can_finalise`, `finalise_plan`, `reopen_plan` | `test_acceptance.py::test_a6_four_valid_bookings_can_be_finalised` |
| FA R1 Artist availability | the duplicate check in `check_booking`; fees are never stored | `test_acceptance.py::test_a4_an_artist_cannot_be_booked_twice_on_any_stage` |
| FA R2 Time and stage | `logic.to_minutes` and `logic.overlaps`, whose strict `<` lets one set start as the last ends | `test_acceptance.py::test_a3_a_set_that_ends_exactly_at_the_close_is_allowed` |
| FA R3 Simultaneous performances | the stage filter: a clash is only sought on the same stage | `test_acceptance.py::test_a2_two_artists_may_play_at_the_same_time_on_different_stages` |
| FA R4 Budget | the fee check against `remaining_budget` | `test_acceptance.py::test_a4_a_booking_one_euro_over_the_budget_is_rejected` |
| FA R5 Valid edits | `booking_id` threaded into `check_booking`; `FINAL_REFUSAL` guards every change | `test_acceptance.py::test_a5_a_rejected_edit_leaves_the_original_booking_untouched` |

Two properties are not single functions: **totals are never stored** (timetable and budget are both
recomputed from `bookings.csv`, so they cannot disagree), and **a refusal writes nothing** (every
mutator checks before it touches `db`).

## What I would do again

1. Put the brief in the repo; everything cites it.
2. Write the acceptance criteria as tests before any code — they are already written as tests.
3. Make failures name what they are waiting for.
4. Keep the rules out of the screen, so redesigning costs nothing.
5. Open it and look at it. The best change came from a question, not a bug report.
