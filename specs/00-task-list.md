# Festival Architect — the task list

Seven tasks, in order. Each one is a slice you can show someone: it ends with a working screen or
a working rule, its own branch, and a named set of tests that go from red to green.

Every task follows the course planning sheet
(https://nova-sbe-introduction-to-programming.github.io/intro-to-programming-2026/weeks/week-05/first-feature.html):
**Why / What / Out of scope / Done when**, with concrete values in the checks.

| # | Task | Spec | Branch | Requirements | Tests that go green |
| --- | --- | --- | --- | --- | --- |
| 1 | Settings and the clock | `task-1-foundations.md` | `task-1-foundations` | FA R2, FA R4 | 3 |
| 2 | **Book an artist** (first feature) | `first-feature.md` | `feature-book-an-artist` | FA01, FA02, FA R1–R4 | 15 |
| 3 | The timetable and the budget | `task-3-timetable.md` | `feature-timetable` | FA03 | write them first |
| 4 | Move or remove a performance | `task-4-revise.md` | `feature-revise-booking` | FA04, FA R5 | 3 |
| 5 | Finalise and reopen | `task-5-finalise.md` | `feature-finalise` | FA05, FA R5 | 5 |
| 6 | The catalogue screen | `task-6-catalogue.md` | `feature-catalogue` | FA01 | write them first |
| 7 | Polish and hand-in | `task-7-polish.md` | `task-7-polish` | — | all of them |

26 tests are red today. Tasks 1, 2, 4 and 5 turn all 26 green. Tasks 3 and 6 are screen work, so
their tests do not exist yet — **write them before the code**, the same way the other 26 were
written before any rule existed.

## The order is not negotiable

Task 1 before everything, because comparing times as text is the bug this whole codebase is built
to avoid. Task 2 before 3, because there is nothing to draw until something can be booked. Task 4
before 5, because finalisation is a lock on top of editing, and you cannot lock what is not there.

## How to work a task

1. `git checkout -b <branch from the table>` — never commit to main.
2. Read the spec. Run its tests and watch them fail.
3. Build until they pass. Change no test to make it pass.
4. Run the whole suite, not just the task's tests, and paste the output.
5. Commit with the message the spec suggests, then open the next spec.
