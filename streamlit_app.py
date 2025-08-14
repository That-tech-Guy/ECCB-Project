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
    page_icon="💰"
)

# --- SIDEBAR MENU ---
st.sidebar.image("images/eccb.png", width=100)
st.sidebar.title("Menu")
menu = st.sidebar.radio("Navigate", [
    "🏝️ Intro",
    "🤖 AI Chat Bot",
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
if menu == "🏝️ Intro":
    run_into()
    

elif menu == "🤖 AI Chat Bot":
    # First-run guard
    profile = get_user_profile()
    if not profile.get("setup_complete") and not st.session_state.get("bot_setup_done"):
        done = render_setup_wizard()
        if not done:
            st.stop()  # show only the wizard on first visit

    # Optional: make profile available to the chat
    st.session_state["user_profile"] = get_user_profile()
    render_chatbot()


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
