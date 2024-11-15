import polars as pl
import streamlit as st

from models.database import prisma, Resource
from models.rbac import require_admin

require_admin()

st.header("Resources")

SCHEMA = ["id", "name", "description", "location", "link"]


@st.fragment
def get_resources():
    resources = Resource.prisma().find_many()
    return pl.DataFrame(resources, schema=SCHEMA)


@st.fragment
def show_resources():
    global resources_df
    global edited_resources_df
    edited_resources_df = st.data_editor(
        resources_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "id": None,
            "name": st.column_config.TextColumn(
                required=True, max_chars=32, help="Name of the resource", label="Name"
            ),
            "description": st.column_config.TextColumn(
                required=True,
                max_chars=511,
                help="Description of the resource",
                label="Description",
            ),
            "location": st.column_config.TextColumn(
                required=False,
                max_chars=255,
                help="Optional location of the resource",
                label="Location",
            ),
            "link": st.column_config.LinkColumn(
                required=False, help="Optional URL of the resource", label="Link"
            ),
        },
    )


def apply_changes():
    new_resources = edited_resources_df.filter(pl.col("id").is_null())

    deleted_resources = resources_df.filter(
        ~pl.col("id").is_in(edited_resources_df["id"])
    )

    updated_resources = (
        edited_resources_df
        .filter(~pl.col("id").is_null())
        .join(
            resources_df,
            on="id",
            how="inner",
            suffix="_original"
        )
        .filter(
            (pl.col("name") != pl.col("name_original")) |
            (pl.col("description") != pl.col("description_original")) |
            (pl.col("location") != pl.col("location_original")) |
            (pl.col("link") != pl.col("link_original"))
        )
        .select(SCHEMA)
    )

    if len(new_resources) + len(updated_resources) + len(deleted_resources) == 0:
        st.warning("No changes to apply")
        return

    with st.spinner("Saving changes..."):
        with prisma.get_client().batch_() as batcher:
            for row in new_resources.iter_rows(named=True):
                del row["id"]
                batcher.resource.create(data=row)
            for row in updated_resources.iter_rows(named=True):
                idx = row["id"]
                del row["id"]
                batcher.resource.update(data=row, where={"id": idx})
            for row in deleted_resources.iter_rows(named=True):
                batcher.resource.delete(where={"id": row["id"]})

            message = f"{len(new_resources)} new resources, {len(updated_resources)} updated, {len(deleted_resources)} deleted"
            st.info(message)


@st.fragment
def import_resources():
    ACCEPTABLE_COLUMNS = ["name", "description", "location", "link"]

    st.subheader("Import resources")
    with st.container(border=True):
        st.caption("Upload a CSV file with the following schema:")
        st.caption("`name`, `description`, `location`, `link`")
        if uploaded_file := st.file_uploader("Upload CSV file", type="csv", accept_multiple_files=False):
            try:
                data = pl.read_csv(uploaded_file).select(ACCEPTABLE_COLUMNS)
                with prisma.get_client().batch_() as batcher:
                    for row in data.iter_rows(named=True):
                        batcher.resource.upsert(
                            where={"name": row["name"]},
                            data={
                                "create": row,
                                "update": row,
                            },
                        )
                st.info(f"Imported {len(data)} resources")
            except Exception:
                st.error("Error occurred during import.")


st.subheader("Manage resources")
with st.container(border=True):
    with st.spinner("Loading resources..."):
        resources_df = get_resources()
    show_resources()
    if st.button("Save"):
        apply_changes()

import_resources()
