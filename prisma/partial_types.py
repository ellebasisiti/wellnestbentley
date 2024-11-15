from prisma.models import User

User.create_partial(
    'UserPrivateView',
    include={
        "email": True,
        "username": True,
        "first_name": True,
        "last_name": True,
        "roles": True,
    }
)

User.create_partial(
    'UserPermissionsView',
    include={"email": True, "roles": True}
)
