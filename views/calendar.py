from datetime import datetime, timedelta

import streamlit as st
from streamlit_calendar import calendar

from models.database import Mood
from models.rbac import require_logged_in


def calendar_header():
    def prev_month():
        val = st.session_state["view_start"] - timedelta(days=1)
        if datetime.now() - val > timedelta(days=90):
            return
        st.session_state["view_start"] = val.replace(day=1)

    def next_month():
        val = st.session_state["view_start"] + timedelta(days=31)
        if val - datetime.now() > timedelta(days=60):
            return
        st.session_state["view_start"] = val.replace(day=1)

    view_start = st.session_state["view_start"]
    title, prev_col, next_col = st.columns([4, 1, 1], vertical_alignment="bottom")
    title.subheader(
        f"{view_start.strftime('%B')} {view_start.year}"
    )

    prev_col.button(
        "Prev",
        icon=":material/chevron_left:",
        key="calendar_prev",
        on_click=prev_month,
        disabled=False,
        use_container_width=True,
    )
    next_col.button(
        "Next",
        icon=":material/chevron_right:",
        key="calendar_next",
        on_click=next_month,
        disabled=False,
        use_container_width=True,
    )


def map_mood(mood: str) -> dict:
    match mood:
        case "Happy":
            return {"title": "Happy 😊", "backgroundColor": "#FFD733"}
        case "Calm":
            return {"title": "Calm 😌", "backgroundColor": "#9dca8e"}
        case "Sad":
            return {"title": "Sad 😔", "backgroundColor": "#5a9dc7"}
        case "Stressed":
            return {"title": "Stressed 😰", "backgroundColor": "#FF6B6B"}
        case _:
            return {"title": mood, "backgroundColor": "#A9A9A9"}


custom_css = """
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
"""


def add_mood_to_calendar(date_str: str):
    date = datetime.fromisoformat(date_str.rstrip("Z"))
    if date > datetime.now().replace(hour=0, minute=0, second=0):
        st.info("🤗 Please fill the mood after the day arrives")
        return

    if datetime.now() - date > timedelta(days=30):
        st.warning("🫡 Too far in the past, out of scope")
        return

    with st.form(key="add_mood"):
        left, right = st.columns([1, 1])
        mood = left.selectbox("Mood", ["Happy", "Calm", "Sad", "Stressed"])
        right.date_input("Date", disabled=True, value=date)
        description = st.text_area("Description", max_chars=60)

        if st.form_submit_button("Record mood"):
            Mood.prisma().upsert(
                where={
                    "user_id_date": {
                        "user_id": st.session_state["user_id"],
                        "date": date,
                    }
                },
                data={
                    "create": {
                        "user_id": st.session_state["user_id"],
                        "date": date,
                        "name": mood,
                        "description": description,
                    },
                    "update": {
                        "name": mood,
                        "description": description,
                    },
                },
            )

            st.session_state["refreshed"] = False


def load_calendar_events():
    calendar_events = []
    moods = Mood.prisma().find_many(
        where={
            "user_id": st.session_state["user_id"],
            "date": {
                "gte": st.session_state["view_start"] - timedelta(days=7),
                "lte": st.session_state["view_start"] + timedelta(days=31),
            },
        },
        order={"date": "asc"},
    )

    mood_iter = iter(moods)
    current_mood = next(mood_iter, None)
    start_date = None

    while current_mood is not None:
        next_mood = next(mood_iter, None)

        delta = 0
        if next_mood is not None and current_mood.name == next_mood.name:
            time_delta = current_mood.date - next_mood.date
            delta = time_delta.days

        if delta == -1:
            if start_date is None:
                start_date = current_mood.date.isoformat()
        else:
            span = {}
            if start_date is not None:
                span["start"] = start_date
                span["end"] = (current_mood.date + timedelta(days=1)).isoformat()
                start_date = None
            else:
                span["date"] = current_mood.date.isoformat()

            calendar_events.append({
                "title": current_mood.name,
                **span,
                **map_mood(current_mood.name),
                "allDay": True,
                "borderColor": "transparent",
                "type": "mood",
            })

        current_mood = next_mood

    return calendar_events


@st.fragment()
def calendar_body():
    events = load_calendar_events()
    with st.container(border=True):
        emotional_calendar = calendar(
            events=events,
            options={
                "timeZone": "UTC",
                "editable": False,
                "selectable": "true",
                "slotMinTime": "06:00:00",
                "slotMaxTime": "24:00:00",
                "initialView": "dayGridMonth",
                "headerToolbar": {
                    "left": "",
                    "center": "",
                    "right": "",
                },
                "initialDate": st.session_state["view_start"].isoformat(),
            },
            custom_css=custom_css,
            callbacks=["dateClick", "eventClick", "select"],
        )

    match emotional_calendar.get("callback"):
        case "dateClick":
            payload = emotional_calendar["dateClick"]
            add_mood_to_calendar(payload["date"])
        case "eventClick":
            payload = emotional_calendar["eventClick"]
        case "select":
            payload = emotional_calendar["select"]

    if "refreshed" in st.session_state and not st.session_state["refreshed"]:
        st.session_state["refreshed"] = True
        st.rerun()


@st.fragment()
def init_calendar():
    require_logged_in()

    if "view_start" not in st.session_state:
        st.session_state["view_start"] = datetime.now().replace(day=1)


init_calendar()
calendar_header()
calendar_body()
