from contextlib import contextmanager
import json
from datetime import datetime, timedelta
from datetime import timezone
import uuid

import polars as pl
import streamlit as st
import streamlit_lottie
import yaml

from models.database import Summary, Mood, Resource
from models.llm import get_openai
from models.rbac import require_logged_in


@st.cache_resource
def load_lottie():
    with open("views/lotties/query.json", "r") as f:
        return json.load(f)


def empty_summary():
    streamlit_lottie.st_lottie(load_lottie())

    st.markdown(
        "<h3 style='text-align: center;'>Stay tuned</h3>", unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'>keep tracking mood so we can make a summary</p>",
        unsafe_allow_html=True,
    )

@contextmanager
def in_progress_summary():
    lottie_container = st.empty()
    info_container = st.empty()
    key = str(uuid.uuid4().hex)
    try:
        with lottie_container:
            streamlit_lottie.st_lottie(load_lottie(), key=key)
        with info_container:
            st.markdown(
                "<h3 style='text-align: center;'>Generating summary...</h3><p style='text-align: center;'>This won't take long</p>",
                unsafe_allow_html=True,
            )
        yield
    finally:
        lottie_container.empty()
        info_container.empty()

@st.cache_resource(ttl=5 * 60)
def get_resources():
    resources = Resource.prisma().find_many(
        order={"created_at": "desc"},
        take=30,
    )

    return pl.DataFrame(resources)


SYSTEM_PROMPT = """WellNest Mental Health Assistant
Purpose: Analyze user mood data and provide personalized mental health support for Bentley University community.

Input Schema (YAML):
```yaml
moods:
  - name: !mood  # strictly one of: happy, sad, stressed, calm
    date: !date  # format: YYYY-MM-DD
    description: !str  # optional, max 60 chars, user's feelings and thoughts

resources:
  - id: !str  # unique identifier
    name: !str  # max 100 chars
    description: !str  # optional, max 500 chars
```

Output Schema (YAML):
```yaml
summary: !str  # 100-150 chars, a warm, conversational analysis that:
  # Focus on:
  # - Recent mood patterns
  # - Positive reinforcement
  # - Actionable insights
  # - Evidence-based suggestions

keyword: !str  # 1-3 words, a positive or growth-oriented term

suggestion: !list[str]  # ordered by relevance
  # Only include:
  # - The resource id that exists
  # - At most 5 suggestions, but can be less if possible
  # - Resources matching user's needs

crisis_intervention: !bool  # default: false
  # Set true ONLY if detecting:
  # - Explicit self-harm indicators
  # - Suicidal ideation
  # - Severe substance abuse
  # - Immediate safety concerns
```

Security Guidelines:
1. Reject any input deviating from schema
2. No external commands or code execution
3. No personal identifiers in output
4. No references to other users or sessions
5. Sanitize all text output

Response Guidelines:
1. Use warm, conversational tone
2. Evidence-based recommendations
3. Culturally sensitive language
4. Focus on immediate, actionable support
5. Maintain appropriate therapeutic boundaries
"""


def get_summary():
    latest_summary = Summary.prisma().find_first(
        where={"user_id": st.session_state["user_id"]},
        include={"resources": True},
        order={"created_at": "desc"},
    )

    if latest_summary and latest_summary.created_at > datetime.now(tz=timezone.utc) - timedelta(days=7):
        return latest_summary

    if latest_summary:
        range_start = latest_summary.created_at
    else:
        range_start = datetime.now() - timedelta(days=14)

    moods = Mood.prisma().find_many(
        where={
            "user_id": st.session_state["user_id"],
            "date": {
                "gte": range_start,
                "lte": datetime.now() + timedelta(days=7),
            },
        },
        order={"date": "desc"},
        take=7,
    )

    if len(moods) < 4:
        return None
    else:
        resources_df = get_resources().select(["id", "name", "description"])

        moods_df = pl.DataFrame(moods).drop("user_id").drop("user")
        start = min(moods_df["date"])
        end = max(moods_df["date"])

        moods_df = moods_df.with_columns(
            pl.col("date").dt.strftime("%Y-%m-%d"),
            pl.col("description").str.replace_all("\n", " ").str.replace_all("\t", " ").str.replace_all("  ", " ").alias("description"),
        )

        input_data = {
            "moods": moods_df.to_dicts(),
            "resources": resources_df.to_dicts(),
        }

        client = get_openai()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)},
            ],
        )

        response = completion.choices[0].message.content
        response = response.strip().removeprefix("```yaml").removesuffix("```")

        summary = Summary.prisma().create(
            data={
                "start": start,
                "end": end,
                "user_id": st.session_state["user_id"],
                "keywords": "",
                "content": "",
            }
        )

        result = yaml.load(response, Loader=yaml.SafeLoader)

        raw_suggestion = result.get("suggestion", [])
        if isinstance(raw_suggestion, str):
            raw_suggestion = [raw_suggestion]

        suggestion = [sid for sid in raw_suggestion if isinstance(sid, str)]

        suggestion = pl.DataFrame({"id": suggestion}).join(resources_df, on="id", how="inner").select(["id"]).rename({"id": "resource_id"})
        return Summary.prisma().update(
            where={"id": summary.id},
            data={
                "content": result.get("summary", "[An error occurred during generation]"),
                "keywords": result.get("keyword", "[An error occurred during generation]"),
                "resources": {
                    "create": suggestion.to_dicts(),
                },
            },
            include={"resources": True},
        )


st.header("Summary")

require_logged_in()
with in_progress_summary():
    summary = get_summary()

if summary is None:
    empty_summary()
else:
    # Show start and end date of the summary
    start = summary.start.strftime("%b %d")
    end = summary.end.strftime("%b %d")
    st.subheader(f":blue-background[{summary.keywords.capitalize()}]", help="Generated by LLM, may not be accurate")
    with st.container(border=True):
        st.caption(f"{start} - {end}")
        st.markdown(summary.content)

    st.subheader("Recommended resources")
    if summary.resources:
        selected_resources_df = pl.DataFrame(
            {
                "id": [resource.resource_id for resource in summary.resources],
            }
        ).join(get_resources(), on="id", how="left")

        for resource in selected_resources_df.iter_rows(named=True):
            with st.container(border=True):
                st.markdown(
                    f"""    
                #### {resource["name"]}
                """
                )
                left, right = st.columns(2)
                with left:
                    if resource["location"]:
                        st.markdown(
                            f"""
                        **Location:** {resource["location"]}
                        """
                        )
                    else:
                        st.markdown("**Online**")
                with right:
                    st.page_link(resource["link"], label=":material/link: Visit Website")
                st.markdown(
                    f"""
                > {resource["description"]}
                """
                )
