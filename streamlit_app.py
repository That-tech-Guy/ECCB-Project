import streamlit as st
from finance_quiz import start_quiz
from currency_converter import converter
from budget_gen import gen_budget
from save_invest import invest
from small_hustles import run_small_hustles
from common_scams import run_common_scams
from intro_page import run_into
from chatbot import render_chatbot
from setup_wizard import render_setup_wizard, get_user_profile

# --- add near top of streamlit_app.py ---
import os, threading, json, time, socket, requests
from pathlib import Path






# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart Finances Caribbean",
    page_icon="🌋"
)

# --- SIDEBAR MENU ---
st.sidebar.image("images/eccb.png", width=100)
st.sidebar.title("Menu")
menu = st.sidebar.radio("Navigate", [
    "🌋 SoufrièreSense AI",
    "🏝️ About Us",
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




# --- PAGE CONTENT ---

    

if menu == "🌋 SoufrièreSense AI":
    # Unique session guard
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = {"setup_complete": False}

    profile = st.session_state["user_profile"]

    if not profile.get("setup_complete"):
        done = render_setup_wizard()
        if not done:
            st.stop()  # force wizard on each new session
    else:
        render_chatbot()


elif menu == "🏝️ About Us":
    run_into()


elif menu == "🧠 Financial Literacy Quiz":
   start_quiz()

elif menu == "📚 Resources":
    st.header("📚 Regional Financial Education Resources")
    st.markdown("""
    - [Eastern Caribbean Central Bank (ECCB)](https://www.eccb-centralbank.org)
    - [Bank of Jamaica (BOJ)](https://www.boj.org.jm)
    - [Central Bank of Trinidad & Tobago](https://www.central-bank.org.tt)
    - [ECCU Financial Empowerment](https://www.eccb-centralbank.org/FinancialLiteracy)
    """)

    st.info("Feel free to submit your own financial learning resources for your territory!")

if menu == "🤖 AI Chat Bot":
    st.markdown("")

else:
    st.markdown("""
    ---
    <center>Made by "664RugRats" for the 2025 ECCB Challenge 💡</center>
    """, unsafe_allow_html=True)
