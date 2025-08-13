import streamlit as st
from finance_quiz import start_quiz
from currency_converter import converter
from budget_gen import gen_budget
from save_invest import invest
from small_hustles import run_small_hustles
from common_scams import run_common_scams
from intro_page import run_into
from chatbot_widget import render_chatbot_overlay
# --- add near top of streamlit_app.py ---
import threading, json, time
from pathlib import Path

def start_api_server_once():
    import socket
    def port_free(port:int)->bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) != 0

    if not port_free(7861):
        return  # already running

    from fastapi import FastAPI, Request
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"], allow_credentials=True,
        allow_methods=["*"], allow_headers=["*"]
    )

    DATA_DIR = Path("/mnt/data/chat_data"); DATA_DIR.mkdir(parents=True, exist_ok=True)
    USERS = DATA_DIR/"chat_users.json"

    def load_json(p:Path, default):
        try:
            return json.loads(p.read_text())
        except Exception:
            return default

    def save_json(p:Path, data):
        p.write_text(json.dumps(data, indent=2))

    @app.post("/chatapi/register")
    async def register(payload: dict):
        uid = payload.get("uid")
        if not uid: return {"ok": False, "error": "missing uid"}
        users = load_json(USERS, {})
        users[uid] = {
            "name": payload.get("name",""),
            "country": payload.get("country",""),
            "email": payload.get("email",""),
            "updated": int(time.time()*1000)
        }
        save_json(USERS, users)
        # ensure user history file exists
        hist_path = DATA_DIR / f"chat_{uid}.json"
        if not hist_path.exists(): save_json(hist_path, {"history": []})
        return {"ok": True}

    @app.post("/chatapi/log")
    async def log(payload: dict):
        uid = payload.get("uid")
        entry = payload.get("entry")
        if not uid or not isinstance(entry, dict):
            return {"ok": False, "error": "bad payload"}
        hist_path = DATA_DIR / f"chat_{uid}.json"
        hist = load_json(hist_path, {"history": []})
        hist["history"].append(entry)
        save_json(hist_path, hist)
        return {"ok": True}

    @app.get("/chatapi/history")
    async def history(uid: str):
        hist_path = DATA_DIR / f"chat_{uid}.json"
        hist = load_json(hist_path, {"history": []})
        return hist

    def run():
        uvicorn.run(app, host="127.0.0.1", port=7861, log_level="warning")

    th = threading.Thread(target=run, daemon=True)
    th.start()

# start it once
try:
    start_api_server_once()
except Exception as e:
    # If FastAPI/uvicorn not installed, just skip; the client will work with localStorage only.
    pass


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart Finances Caribbean",
    page_icon="💰"
)

# --- SIDEBAR MENU ---
st.sidebar.image("images/eccb.png", width=100)
st.sidebar.title("Menu")
menu = st.sidebar.radio("Navigate", [
    "🏝️ Intro",
    "💱 Currency Converter",
    "🌍 Caribbean Saving & Investing",
    "📊 Budget Plan Generator",
    "🚨 Common Scams",
    "🧵 Small Hustles",
    "🧠 Financial Literacy Quiz",
    "📚 Resources"
], key="menu")

# --- STYLING ---
st.markdown("""
    <style>
        .main { background-color: #f0f8ff; }
        h1, h2 { color: #007bff; }
        .section { padding: 20px; background-color: white; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)




render_chatbot_overlay(title="ECCB Assistant", corner="right")

# --- PAGE CONTENT ---
if menu == "🏝️ Intro":
    run_into()
    


elif menu == "💱 Currency Converter":
    converter()


elif menu == "📊 Budget Plan Generator":
    gen_budget()


elif menu == "🌍 Caribbean Saving & Investing":
    invest()


elif menu == "🧵 Small Hustles":
    run_small_hustles()


elif menu == "🧠 Financial Literacy Quiz":
   start_quiz()


elif menu == "🚨 Common Scams":
    run_common_scams()


elif menu == "📚 Resources":
    st.header("📚 Regional Financial Education Resources")
    st.markdown("""
    - [Eastern Caribbean Central Bank (ECCB)](https://www.eccb-centralbank.org)
    - [Bank of Jamaica (BOJ)](https://www.boj.org.jm)
    - [Central Bank of Trinidad & Tobago](https://www.central-bank.org.tt)
    - [ECCU Financial Empowerment](https://www.eccb-centralbank.org/FinancialLiteracy)
    """)

    st.info("Feel free to submit your own financial learning resources for your territory!")


st.markdown("""
---
<center>Made by "664RugRats" for the 2025 ECCB Challenge 💡</center>
""", unsafe_allow_html=True)
