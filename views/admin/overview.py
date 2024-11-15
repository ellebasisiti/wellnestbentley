from datetime import datetime, timedelta

import altair as alt
import polars as pl
import streamlit as st

from models.database import User, Event, Summary, Resource, prisma
from models.rbac import require_admin


@st.cache_data(ttl=60)
def get_overview_data():
    users = User.prisma().count()
    events = Event.prisma().count()
    summaries = Summary.prisma().count()
    resources = Resource.prisma().count()

    recent_week_filter = {
        "created_at": {
            "gt": datetime.now() - timedelta(days=7)
        }
    }

    users_delta = User.prisma().count(where=recent_week_filter)
    events_delta = Event.prisma().count(where=recent_week_filter)
    summaries_delta = Summary.prisma().count(where=recent_week_filter)
    resources_delta = Resource.prisma().count(where=recent_week_filter)

    return users, users_delta, events, events_delta, summaries, summaries_delta, resources, resources_delta


@st.fragment(run_every=60)
def overview():
    with st.spinner("Loading overview data..."):
        users, users_delta, events, events_delta, summaries, summaries_delta, resources, resources_delta = get_overview_data()

    def format_percentage(value, total):
        if total == 0:
            return ("N/A", "off")
        if value == total:
            return ("NEW",)
        return (f"{value / (total - value) * 100:.2f}%",)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Users", users, *format_percentage(users_delta, users))
    col2.metric("Events", events, *format_percentage(events_delta, events))
    col3.metric("Summaries", summaries, *format_percentage(summaries_delta, summaries))
    col4.metric("Resources", resources, *format_percentage(resources_delta, resources))
    st.caption("Changes in the last 7 days, statistics updated every minute")


@st.cache_data(ttl=60)
def get_database_stats():
    metrics = prisma.get_client().get_metrics()
    connection_data = pl.DataFrame(metrics.gauges).with_columns(
        pl.col("key").str.replace_all("[a-z]+_", "").alias("State"),
        pl.col(["description"]).alias("Description"),
        pl.col("value").alias("Count")
    )

    elapsed_data = pl.DataFrame(metrics.histograms, strict=False).unnest("value").explode("buckets").with_columns(
        pl.col("buckets").list.get(0).alias("Latency"),
        pl.col("buckets").list.get(1).alias("Count"),
        pl.col("description").alias("Description")
    ).drop("buckets").filter(pl.col("Count") > 0).sort(["key", "Latency"])
    return connection_data, elapsed_data


@st.fragment(run_every=60)
def monitoring():
    connection_data, elapsed_data = get_database_stats()
    left, right = st.columns(2)
    connections = alt.Chart(connection_data).mark_arc(
        opacity=0.7,
    ).encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="State", type="nominal", scale=alt.Scale(scheme='tableau20')),
        description=alt.Description(field="Description", type="nominal"),
        tooltip=["State", "Count", "Description"],
    ).configure(
        background="transparent",
    )
    elapsed = alt.Chart(elapsed_data).mark_area(
        clip=True,
        interpolate='monotone',
        opacity=0.7,
    ).encode(
        x=alt.X("Latency:Q").scale(type="log"),
        y=alt.Y("Count:Q", title=None),
        color=alt.Color(field="key", type="nominal", scale=alt.Scale(scheme='tableau20'), legend=None),
        tooltip=["Count", "Latency", "Description"],
    ).configure(
        background="transparent"
    )
    with left.container(border=True):
        st.markdown("**Database connections**")
        st.altair_chart(connections, use_container_width=True)
    with right.container(border=True):
        st.markdown("**Query execution time**")
        st.altair_chart(elapsed, use_container_width=True)

require_admin()

st.header("Overview")
overview()

st.subheader("Monitoring")
monitoring()
