import requests
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def _headers():
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"}

def post(endpoint: str, data: dict):
    try:
        r = requests.post(f"{BASE_URL}{endpoint}", json=data, headers=_headers(), timeout=10)
        try:
            return r.json(), r.status_code
        except Exception:
            return {"detail": f"Server error ({r.status_code}): {r.text[:200] or 'empty response'}"}, r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500

def get(endpoint: str, params: dict = None):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}", headers=_headers(), params=params or {}, timeout=15)
        try:
            return r.json(), r.status_code
        except Exception:
            return {"detail": f"Server error ({r.status_code}): {r.text[:200] or 'empty response'}"}, r.status_code
    except Exception as e:
        return {"detail": str(e)}, 500