import streamlit as st
import json
import random
from pathlib import Path
from typing import List, Dict, Any, Optional

# ---------------------------------
# Paths (matches your structure)
# ---------------------------------
FILES_DIR = Path("files")
SIDE_HUSTLES_JSON = FILES_DIR / "side_huslte_options.json"  # <- your filename

# ---------------------------------
# Seeds for business idea generator
# ---------------------------------
INDUSTRIES = [
    "Health & Wellness", "Food & Beverage", "Education", "Technology",
    "Arts & Crafts", "E-commerce", "Pet Services", "Fitness", "Sustainability"
]
BUSINESS_MODELS = [
    "subscription service", "mobile app", "online store", "freelance service",
    "pop-up shop", "consulting agency", "local delivery", "coaching business",
    "custom product line"
]
TARGET_AUDIENCES = [
    "busy professionals", "stay-at-home parents", "college students",
    "small business owners", "remote workers", "eco-conscious consumers",
    "pet owners", "artists and creatives", "seniors"
]

# ---------------------------------
# Loaders
# ---------------------------------
@st.cache_data(show_spinner=False)
def load_side_hustles(path: Path = SIDE_HUSTLES_JSON) -> List[Dict[str, Any]]:
    """Load and validate side hustles from JSON file."""
    if not path.exists():
        st.error(f"Side hustle JSON not found at: {path}")
        return []

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        st.error(f"Failed to parse JSON at {path}: {e}")
        return []

    valid: List[Dict[str, Any]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            st.warning(f"Skipping item #{i}: not an object")
            continue

        title = (item.get("title") or "").strip()
        description = (item.get("description") or "").strip()
        requirements = (item.get("requirements") or "").strip()
        remote = item.get("remote", False)
        low_cost = item.get("low_cost", False)

        # basic validation
        if not title:
            st.warning(f"Skipping item #{i}: missing title")
            continue
        if not isinstance(remote, bool) or not isinstance(low_cost, bool):
            st.warning(f"Skipping item #{i}: 'remote'/'low_cost' must be booleans (true/false)")
            continue

        valid.append({
            "title": title,
            "description": description,
            "requirements": requirements,
            "remote": bool(remote),
            "low_cost": bool(low_cost),
        })

    if not valid:
        st.error("No valid side hustles found in JSON.")
    return valid

# ---------------------------------
# Core logic
# ---------------------------------
def get_random_side_hustle(hustles: List[Dict[str, Any]], remote_only=False, low_cost_only=False) -> Optional[Dict[str, Any]]:
    filtered = [
        h for h in hustles
        if (not remote_only or h["remote"]) and (not low_cost_only or h["low_cost"])
    ]
    if not filtered:
        return None
    return random.choice(filtered)

def generate_business_idea() -> str:
    industry = random.choice(INDUSTRIES)
    model = random.choice(BUSINESS_MODELS)
    audience = random.choice(TARGET_AUDIENCES)
    return f"💡 A {industry.lower()} {model} for {audience}."

# ---------------------------------
# UI wrapper
# ---------------------------------
def run_small_hustles():
    st.header("🧵 Smart Hustle Suggestions")
    st.markdown("Explore random side hustles or generate small business ideas tailored to your situation.")

    side_hustles = load_side_hustles()

    st.subheader("💼 Find a Random Side Hustle")
    col1, col2 = st.columns(2)
    with col1:
        remote_only = st.checkbox("💻 Remote Only", value=True)
    with col2:
        low_cost_only = st.checkbox("💸 Low Startup Cost", value=True)

    if st.button("🎲 Suggest a Side Hustle"):
        pick = get_random_side_hustle(side_hustles, remote_only=remote_only, low_cost_only=low_cost_only)
        if not pick:
            st.error("🚫 No side hustles found with those filters!")
        else:
            st.success(
                f"**💼 Side Hustle:** {pick['title']}\n\n"
                f"**📝 Description:** {pick.get('description','—')}\n\n"
                f"**📋 Requirements:** {pick.get('requirements','—')}"
            )

    st.markdown("---")
    st.subheader("🚀 Generate a Business Idea")
    if st.button("🎯 Give Me a Business Idea"):
        st.info(generate_business_idea())

    st.markdown("""
        ---
        👇 Use these ideas to:
        - Start a weekend hustle
        - Launch an online business
        - Earn extra income while in school
    """)

