"""specs/task-6-catalogue.md: the whole product on one screen (FA01-FA05).

Written before the code, so they are red until the single screen exists.
"""
import db
import logic
from conftest import APP_FILE, make_artist, save_catalogue, set_setting, use_temp_data


def open_app():
    """Start the app and return it. There is only one screen, so there is nothing to pick."""
    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(APP_FILE)
    app.run()
    return app


def labels(buttons):
    """Return the labels of a list of buttons."""
    found = []
    for button in buttons:
        found.append(button.label)
    return found


# ---------- one screen ----------

def test_there_is_no_screen_switcher(tmp_path, monkeypatch):
    """The app opens on the only screen it has: no sidebar radio to choose between screens."""
    use_temp_data(tmp_path, monkeypatch)
    app = open_app()
    assert not app.exception
    assert len(app.sidebar.radio) == 0


def test_the_timetable_and_the_catalogue_share_the_page(tmp_path, monkeypatch):
    """Both the lineup and every artist are reachable without navigating anywhere."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", duration_min="60"),
        make_artist("2", duration_min="45"),
    ])
    logic.add_booking("1", "1", "16:00")

    app = open_app()
    assert not app.exception
    shown = []
    for block in app.markdown:
        shown.append(block.value)
    assert any("Artist 2" in text for text in shown)


def test_the_budget_is_shown_once(tmp_path, monkeypatch):
    """One set of budget numbers for the whole page, not one per screen."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", fee="2000", duration_min="60")])
    logic.add_booking("1", "1", "16:00")

    app = open_app()
    values = []
    for card in app.metric:
        values.append(card.value)
    assert values.count("2000 €") == 1


# ---------- arming an artist ----------

def test_clicking_an_artist_arms_them(tmp_path, monkeypatch):
    """An artist card picks that artist up, ready to drop into a slot."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    app = open_app()
    assert "armed_artist" not in app.session_state
    [b for b in app.button if b.proto.id.endswith("arm_1")][0].click().run()
    assert app.session_state["armed_artist"] == "1"


def test_clicking_the_armed_artist_again_puts_them_down(tmp_path, monkeypatch):
    """Arming is a toggle, so a mis-click costs nothing."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    app = open_app()
    [b for b in app.button if b.proto.id.endswith("arm_1")][0].click().run()
    assert app.session_state["armed_artist"] == "1"
    [b for b in app.button if b.proto.id.endswith("arm_1")][0].click().run()
    assert "armed_artist" not in app.session_state


# ---------- clicking an empty slot ----------

def test_a_clicked_slot_names_its_stage_and_time():
    """The calendar reports where the organiser clicked; we read a stage and a start from it."""
    import app as application

    payload = {"callback": "dateClick", "dateClick": {
        "resource": {"id": "2"}, "date": "2026-06-20T15:30:00+00:00",
    }}
    assert application.clicked_slot(payload) == ("2", "15:30")


def test_anything_that_is_not_a_slot_click_books_nothing():
    """Dragging and inspecting are not slot clicks, and half a payload is not one either."""
    import app as application

    assert application.clicked_slot(None) is None
    assert application.clicked_slot({"callback": "eventClick"}) is None
    assert application.clicked_slot({"callback": "dateClick", "dateClick": {}}) is None


# ---------- the money ----------

def test_an_artist_over_the_budget_names_the_shortfall(tmp_path, monkeypatch):
    """With 1,000 left, a 1,001 artist says it is 1 euro short; a 1,000 artist says nothing."""
    import app as application

    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="9000", duration_min="60"),
        make_artist("2", fee="1000", duration_min="60"),
        make_artist("3", fee="1001", duration_min="60"),
    ])
    logic.add_booking("1", "1", "14:00")

    assert logic.remaining_budget() == 1000
    assert application.shortfall_text(logic.get_artist("3")) == "1 € over budget"
    assert application.shortfall_text(logic.get_artist("2")) == ""


# ---------- a final plan ----------

def test_a_final_plan_offers_nothing_that_changes_the_lineup(tmp_path, monkeypatch):
    """While final, no artist can be armed and the calendar is not editable."""
    import app as application

    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="1000", duration_min="60"),
        make_artist("2", fee="1000", duration_min="60"),
    ])
    set_setting("min_artists_to_finalise", 2)
    logic.add_booking("1", "1", "14:00")
    logic.add_booking("2", "1", "15:00")
    assert logic.finalise_plan() == ""

    app = open_app()
    assert not app.exception
    assert not any(button.proto.id.endswith("arm_1") for button in app.button)
    assert application.calendar_options()["editable"] is False
    assert "Reopen as draft" in labels(app.button)


# ---------- a restart ----------

def test_the_page_is_the_same_after_a_restart(tmp_path, monkeypatch):
    """Everything on the page is read from the saved tables, so reopening changes nothing."""
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([
        make_artist("1", fee="2000", duration_min="60"),
        make_artist("2", fee="1500", duration_min="45"),
    ])
    logic.add_booking("1", "1", "16:00")
    logic.add_booking("2", "2", "17:00")

    before = [logic.timetable("1"), logic.timetable("2"), logic.total_fees()]
    assert db.load_table("bookings") != []
    app = open_app()
    assert not app.exception
    assert [logic.timetable("1"), logic.timetable("2"), logic.total_fees()] == before


def test_the_metric_cards_are_styled_from_the_first_draw(tmp_path, monkeypatch):
    """The budget cards look the same before anything is clicked as they do afterwards.

    The styling is a stylesheet the page injects, so it has to be there on the very first
    draw, not only once a performance happens to be selected.
    """
    use_temp_data(tmp_path, monkeypatch)
    save_catalogue([make_artist("1", duration_min="60")])

    app = open_app()
    styles = []
    for block in app.get("html"):
        if "metric-container" in block.body:
            styles.append(block.body)
    assert len(styles) == 1
