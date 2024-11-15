import streamlit as st

from models.auth import load_authenticator, wipe_cookie
from models.authentication_models import UpdateError
from models.database import UserPrivateView, prisma
from models.rbac import require_logged_in, _is_admin


@st.fragment()
def user_details():
    user = UserPrivateView.prisma().find_first(
        where={"username": st.session_state["username"]},
    )

    with st.expander("Details", icon=":material/badge:"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Email**")
            st.markdown(f"[{user.email}](mailto:{user.email})")

            st.markdown("**Username**")
            st.markdown(f"`{user.username}`")

        with col2:
            st.markdown("**First Name**")
            st.markdown(f"`{user.first_name or '-'}`")

            st.markdown("**Last Name**")
            st.markdown(f"`{user.last_name or '-'}`")

        st.markdown("### Roles")
        roles_html = " ".join([f"`{role}`" for role in user.roles])
        st.markdown(roles_html)


@st.fragment()
def update_details():
    try:
        if authenticator.update_user_details(st.session_state["username"]):
            st.success('Entries updated successfully')
            st.rerun()
    except UpdateError as e:
        st.error(e)


@st.fragment()
def reset_password():
    try:
        if authenticator.reset_password(st.session_state["username"]):
            st.success('Password reset successfully')
            st.rerun()
    except Exception as e:
        st.error(e)

@st.dialog("Delete Account")
def delete_account_dialog():
    if _is_admin():
        st.error("User with admin role cannot delete their own account")
        st.caption("Please ask another admin drop your permissions to proceed")
        return

    st.error("This action is irreversible and will delete your account and all your data")
    if st.button("Delete Anyways", type="primary"):
        with st.status("Deleting account..."):
            st.write("Scanning for activities...")
            with prisma.get_client().batch_() as batcher:
                batcher.user.delete(where={"id": st.session_state["user_id"]})
                st.write("Deleting all activities...")
            st.snow()

        wipe_cookie(authenticator)
        authenticator.logout(location="unrendered")
        st.success("Account deleted successfully, please refresh the page")


@st.fragment()
def delete_account():
    with st.expander("Danger Zone", icon=":material/delete:"):
        st.subheader(":red[Delete Account]")
        st.caption("This action is irreversible and will delete your account and all your data")
        if st.button("Delete Account", type="primary"):
            delete_account_dialog()
            
st.header("Profile")
with st.spinner("Loading profile..."):
    require_logged_in()
    authenticator = load_authenticator()

    user_details()
    update_details()
    reset_password()
    delete_account()
