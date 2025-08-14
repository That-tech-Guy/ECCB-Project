# setup_wizard.py
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
from avatar_builder import avatar_editor

DATA_DIR = Path("files")
PROFILE = DATA_DIR / "user_profile.json"

DEFAULTS = {
    "setup_complete": False,
    "name": "",
    "role": "Student",            # Student | Teacher | Parent
    "home_region": "ECCU",        # ECCU | Caribbean (non-ECCU) | Global / Other
    "country": "Montserrat",
    "auto_currency": True,
    "base_currency": "XCD",
    "tone": "Friendly",           # Friendly | Professional | Youthful | Formal | Concise
    "goals": [],                  # e.g. ["Budgeting","Saving","Investing","Debt reduction"]
    "email": "",
    "allow_location": True,
    "avatar_svg": None,
    "avatar_png": None,
    "avatar_config": None,
}

ECCU_COUNTRIES = [
    "Anguilla", "Antigua & Barbuda", "Dominica", "Grenada",
    "Montserrat", "St. Kitts & Nevis", "St. Lucia", "St. Vincent & the Grenadines",
]
CARIB_NON_ECCU = ["Barbados", "Trinidad & Tobago", "Jamaica", "Bahamas", "Haiti", "Cuba", "Dominican Republic"]

COUNTRIES = ECCU_COUNTRIES + CARIB_NON_ECCU

# Country -> currency map for our region
COUNTRY_TO_CUR = {
    "Anguilla": "XCD", "Antigua & Barbuda": "XCD", "Dominica": "XCD",
    "Grenada": "XCD", "Montserrat": "XCD", "St. Kitts & Nevis": "XCD",
    "St. Lucia": "XCD", "St. Vincent & the Grenadines": "XCD",
    "Barbados": "BBD", "Trinidad & Tobago": "TTD", "Jamaica": "JMD", "Bahamas": "BSD",
    "Haiti": "HTG", "Cuba": "CUP", "Dominican Republic": "DOP",
}

# A compact world currency list (fallback if pycountry isn’t available)
COMMON_WORLD_CURRENCIES = [
    "USD","EUR","GBP","CAD","AUD","JPY","CNY","INR","BRL","ZAR","KES","NGN","SAR","AED",
    "CHF","SEK","NOK","DKK","PLN","TRY","MXN","ARS","CLP","PEN","COP","NZD","KRW","HKD","SGD",
    # Caribbean + ECCU
    "XCD","BBD","TTD","BSD","JMD","HTG","CUP","DOP",
]

GOAL_OPTIONS = ["Budgeting", "Saving", "Investing", "Debt reduction", "Business ideas", "Fraud awareness"]
TONES = ["Friendly", "Professional", "Youthful", "Formal", "Concise"]
ROLES = ["Student", "Teacher", "Parent"]

def load_profile() -> dict:
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    if PROFILE.exists():
        try:
            return {**DEFAULTS, **json.loads(PROFILE.read_text())}
        except Exception:
            return DEFAULTS.copy()
    return DEFAULTS.copy()

def save_profile(p: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    PROFILE.write_text(json.dumps(p, indent=2))
    # keep session in sync for immediate use in chat
    st.session_state["user_profile"] = p

def _world_currency_list():
    """Return a sorted world currency list; try pycountry, else fallback."""
    try:
        import pycountry  # type: ignore
        world = sorted({c.alpha_3 for c in pycountry.currencies if hasattr(c, "alpha_3") and len(c.alpha_3) == 3})
        for bad in ("XTS","XXX"):
            if bad in world:
                world.remove(bad)
        return world
    except Exception:
        return sorted(set(COMMON_WORLD_CURRENCIES))

def render_setup_wizard() -> bool:
    st.title("👋 Quick Setup")

    p = load_profile()
    st.write("Let’s personalize the assistant. Not in the Caribbean? No problem — choose **Global / Other** below.")

    # ── Step 1 — Region, Who & Where
    with st.container(border=True):
        st.subheader("Your basics")
        c0, c1, c2 = st.columns([1.2, 1, 1])
        with c0:
            p["home_region"] = st.selectbox(
                "Where should the assistant assume you are?",
                ["ECCU", "Caribbean (non-ECCU)", "Global / Other"],
                index=["ECCU","Caribbean (non-ECCU)","Global / Other"].index(p.get("home_region","ECCU"))
            )
        with c1:
            p["name"] = st.text_input("Name (optional)", value=p["name"])
            p["role"] = st.selectbox("I am a…", ROLES, index=ROLES.index(p["role"]))
        with c2:
            if p["home_region"] == "ECCU":
                p["country"] = st.selectbox("Country", ECCU_COUNTRIES, index=max(0, ECCU_COUNTRIES.index(p["country"]) if p["country"] in ECCU_COUNTRIES else 0))
            elif p["home_region"] == "Caribbean (non-ECCU)":
                default_idx = CARIB_NON_ECCU.index(p["country"]) if p["country"] in CARIB_NON_ECCU else 0
                p["country"] = st.selectbox("Country", CARIB_NON_ECCU, index=default_idx)
            else:
                # Global — freeform country
                p["country"] = st.text_input("Country (any)", value=p["country"])

    # ── Step 2 — Currency behaviour
    with st.container(border=True):
        st.subheader("Currency preferences")
        p["auto_currency"] = st.toggle("Auto-set base currency from my country/region", value=p["auto_currency"])

        if p["auto_currency"]:
            # ECCU/Caribbean: look up from table; Global: leave as-is unless we can infer
            suggested = COUNTRY_TO_CUR.get(p["country"])
            if not suggested and p["home_region"] == "ECCU":
                suggested = "XCD"
            if suggested:
                p["base_currency"] = suggested
                st.info(f"Base currency will be set to **{p['base_currency']}**. You can change this later.")
            else:
                st.caption("No default found for your country. You can pick a currency below if you prefer.")
        else:
            world = _world_currency_list()
            # Preselect current base if present
            idx = world.index(p["base_currency"]) if p["base_currency"] in world else (world.index("USD") if "USD" in world else 0)
            p["base_currency"] = st.selectbox("Base currency (ISO 4217, e.g., XCD, USD…)", world, index=idx)

        # Small hint for ECCU
        if p["home_region"] == "ECCU" and p["base_currency"] != "XCD":
            st.caption("Tip: ECCU’s currency is **XCD**. You can still use another base if you prefer.")

    # ── Step 3 — Tone & Goals
    with st.container(border=True):
        st.subheader("Tone & goals")
        # Keep your previous tone but widen choices
        tone_default = p.get("tone") if p.get("tone") in TONES else "Friendly"
        p["tone"] = st.selectbox("Assistant tone", TONES, index=TONES.index(tone_default))
        p["goals"] = st.multiselect(
            "What should we focus on?",
            GOAL_OPTIONS,
            default=p["goals"] or ["Budgeting","Saving"]
        )
        st.caption("Your tone & goals will guide the assistant's responses across the app.")

    # ── Step 3.5 — Avatar
    with st.container(border=True):
        st.subheader("Your avatar")
        st.write("Create a custom avatar to use across the app.")
        saved = avatar_editor(email=p.get("email") or "guest")
        if saved:
            p["avatar_svg"] = saved.get("svg_path")
            p["avatar_png"] = saved.get("png_path")
            p["avatar_config"] = saved.get("config")
            st.success("Avatar ready! It will be used in chat and navigation.")

    # ── Step 4 — Permissions & Email
    with st.container(border=True):
        st.subheader("Permissions & contact")
        p["allow_location"] = st.toggle(
            "Allow location hints (for ECCU slang, local examples, etc.)",
            value=p["allow_location"]
        )
        # Email REQUIRED on save (but you may skip the wizard entirely)
        p["email"] = st.text_input("Email (required to save)", value=p["email"], help="Used for receipts/notes & account recovery")

    # ── Finalize
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Skip for now"):
            st.session_state["bot_setup_done"] = True
            return True

    with c2:
        if st.button("Save & Start Chat"):
            # Basic email validation
            email_ok = bool(p["email"]) and ("@" in p["email"]) and ("." in p["email"].split("@")[-1])
            if not email_ok:
                st.error("Please enter a valid email to continue (or choose **Skip for now**).")
                return False

            # Mark ECCU membership for downstream logic
            p["is_eccu"] = p["home_region"] == "ECCU" or p["country"] in ECCU_COUNTRIES

            p["setup_complete"] = True
            save_profile(p)
            st.session_state["bot_setup_done"] = True
            st.success("Saved! Opening chat…")
            return True

    with c3:
        if st.button("Reset"):
            save_profile(DEFAULTS.copy())
            st.toast("Reset complete.", icon="↩️")

    return False

def get_user_profile() -> dict:
    # Unified accessor; prefer session cache
    if "user_profile" in st.session_state:
        return st.session_state["user_profile"]
    p = load_profile()
    st.session_state["user_profile"] = p
    return p
