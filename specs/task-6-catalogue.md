# Task 6 — The catalogue screen

> Branch `feature-catalogue`. **No tests exist for this task.** Write them first, in
> `tests/test_catalogue.py`, using `streamlit.testing.v1.AppTest`.

## Why

Task 2 gave the organiser a list of artists good enough to book from. This makes it a screen they
can actually choose with: what each artist plays, what they cost, how long they are on stage, and
which ones are already in the lineup — so they stop trying to book someone twice and can see at a
glance what still fits in the money that is left.

## What

Completes FA01.

- [ ] Every artist is shown with name, genre, fee and set duration, before any booking happens.
- [ ] Artists already in the lineup are clearly marked — a `streamlit-extras` badge — and cannot
      be picked in the booking form.
- [ ] Artists whose fee is more than the remaining budget are marked as unaffordable, with the
      shortfall in euros. They are still visible; the catalogue never hides an artist.
- [ ] The remaining budget is on this screen too, so the organiser does not have to switch screens
      to know what they can afford.
- [ ] The screen reads everything through `logic`. It does not open a CSV and it does not
      recalculate a fee or a total of its own.

## Out of scope

- Searching, sorting or filtering the catalogue. Eight artists fit on a screen.
- Adding, editing or deleting artists — the catalogue is supplied content, edited in `seed/`.
- Photos, links or anything from an external music service: the brief excludes them.

## Done when

`uv run pytest tests/test_catalogue.py` is green, with at least these checks written first:

- **Everything is shown.** The screen renders without an exception and shows all eight artists,
  each with its genre, its fee and its duration in minutes.
- **A booked artist is marked.** Book one artist: that artist now carries the booked badge, the
  other seven do not, and the booked one is absent from the booking form's choices.
- **Affordability is honest.** With €9,000 committed and €1,000 left, a €1,001 artist is marked
  unaffordable and names the €1 shortfall, while the €1,000 artist is not marked.
- **A rejected booking changes nothing here.** Attempt the €1,001 booking: it is refused, and the
  catalogue still shows the same badges and the same remaining budget as before.
- **A restart.** Reopen the app: the same artists carry the booked badge and the remaining budget
  reads the same.

Commit as `Feature: the artist catalogue screen`.
