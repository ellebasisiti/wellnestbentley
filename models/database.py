import subprocess
import streamlit as st
import os
import sys

def generate_prisma_client():
    """Generates the Prisma Client and loads it
    """
    print("Generating Prisma client")
    
    if sys.platform == "linux":
        path_var = os.environ["PATH"].split(":")
        if "/bin" not in path_var:
            path_var.insert(0, "/bin")
            os.environ["PATH"] = ":".join(path_var)
            print(f"/bin added to PATH")

            proc = subprocess.Popen(["sh", "-c", "echo ok"], stdout=subprocess.PIPE)
            proc.wait()
            if proc.returncode != 0:
                print(f"sh -c echo ok returned {proc.returncode}")
                raise Exception(f"Internal error")

    proc = subprocess.Popen(["prisma", "generate"])
    proc.wait()
    if proc.returncode != 0:
        if os.path.exists("/home/app/.npm/_logs/"):
            for file in os.listdir("/home/app/.npm/_logs/"):
                print(f"Contents of {file}:")
                with open(f"/home/app/.npm/_logs/{file}", "r") as f:
                    print(f.read())
        raise Exception(f"Failed to execute command: prisma generate")
    print("Prisma client generated")


try:
    import prisma
    # noinspection PyUnresolvedReferences
    from prisma import Prisma
except:
    from prisma_cleanup import cleanup

    cleanup()
    import importlib

    importlib.invalidate_caches()
    generate_prisma_client()
    importlib.reload(prisma)

import prisma
# noinspection PyUnresolvedReferences
from prisma.models import *
# noinspection PyUnresolvedReferences
from prisma.partials import *


@st.cache_resource(show_spinner=False, validate=lambda x: x == True)
def init_database_connection():
    try:
        prisma.get_client()
        return True
    except:
        pass

    retry = 0
    db = prisma.Prisma(auto_register=True)

    while retry < 3:
        try:
            db.connect()
            return True
        except:
            retry += 1
            print(f"Error connecting to database, retrying...")
            db.disconnect()

    return False
