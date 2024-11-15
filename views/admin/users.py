import streamlit as st

from models.database import UserPermissionsView
from models.rbac import require_admin, ROLES


@st.fragment()
def render_user(user: UserPermissionsView):
    with st.container(border=True):
        st.markdown(f"**Email:** `{user.email}`")
        new_roles = st.multiselect("Roles", options=ROLES, default=user.roles)
        if new_roles != user.roles:
            button = st.button("Update")
            if button:
                UserPermissionsView.prisma().update(where={"email": user.email}, data={"roles": new_roles})
                user.roles = new_roles
                st.rerun()


require_admin()
st.header("Users")
with st.form("Permissions"):
    st.subheader("Permissions")
    st.text("Search users by email to grant roles")
    email = st.text_input("Email", key="email", max_chars=255, placeholder="Leave blank to search all users")
    search_button = st.form_submit_button("Search")
if search_button:
    with st.spinner("Searching for users..."):
        users = UserPermissionsView.prisma().find_many(
            where={"email": {"contains": email}},
            order={"email": "asc"},
            take=20
        )
    with st.container(border=True):
        st.subheader(f"Found {len(users)} users")
        for user in users:
            render_user(user)

