import dotenv

dotenv.load_dotenv(".env.local")

import os
import bcrypt
import polars as pl
from prisma import Prisma
from models.rbac import Roles

db = Prisma()
db.connect()

db.user.upsert(
    where={
        "username": os.getenv("ADMIN_USERNAME"),
    },
    data={
        "create": {
            "username": os.getenv("ADMIN_USERNAME"),
            "email": os.getenv("ADMIN_EMAIL"),
            "password": bcrypt.hashpw(os.getenv("ADMIN_PASSWORD").encode(), bcrypt.gensalt()).decode(),
            "roles": Roles("admin", "user"),
        },
        "update": {},
    }
)

with open("prisma/resources.csv", "r", encoding="utf-8") as f:
    df = pl.read_csv(f)
    with db.batch_() as batcher:
        for row in df.iter_rows(named=True):
            batcher.resource.upsert(
                where={
                    "name": row["name"],
                },
                data={
                    "create": row,
                    "update": row,
                },
            )

db.disconnect()
