import os
from dotenv import load_dotenv
load_dotenv()

def setting(name, default=""):
    try:
        return st.secrets.get(name, os.getenv(name, default))
    except Exception:
        return os.getenv(name, default)

# Streamlit secrets are optional; environment variables work locally.
try:
    import streamlit as st
except Exception:
    st = None

def get_setting(name, default=""):
    if st is not None:
        try:
            return st.secrets.get(name, os.getenv(name, default))
        except Exception:
            pass
    return os.getenv(name, default)
