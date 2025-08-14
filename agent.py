import os
import time
import requests
import pycountry
import streamlit as st

from currency_converter import currencyconverter
from common_scams import commonscams2
from budget_gen import budgeting_function
from save_invest import investing_advice
from small_hustles import get_random_side_job, generate_business_idea
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.media import Image
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.wikipedia import WikipediaTools

# ----------------------------
# OpenRouter model + key setup
# ----------------------------
API_KEY = os.getenv("OPENROUTER_API_KEY") or st.secrets.get("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "Missing OPENROUTER_API_KEY. Set it in your environment or .streamlit/secrets.toml"
    )

MODEL_ID = os.getenv("OPENROUTER_MODEL") or st.secrets.get("OPENROUTER_MODEL") or "google/gemini-2.5-flash"

# Optional profile fields (not required here, but available if you want them elsewhere)
profile = st.session_state.get("user_profile", {})
base_currency = profile.get("base_currency", "XCD")
tone = profile.get("tone", "Friendly")

# ----------------------------
# ECCU context + persona tone
# ----------------------------
ECCU_COUNTRIES = [
    "Antigua and Barbuda",
    "Dominica",
    "Grenada",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines",
    "Anguilla",
    "Montserrat",
]
_ECCU_SET = set(ECCU_COUNTRIES)

COUNTRY_TONE = {
    "Antigua and Barbuda": {
        "greeting": "Wadadli strong!",
        "example": "Let’s budget your Wadadli Day income after the big fete.",
        "slang": ["Wadadli Day", "carnival money", "boat ride lime", "fete vibes"],
    },
    "Dominica": {
        "greeting": "Wha’ vibes!",
        "example": "What would you do with $50 from selling dasheen at Roseau Market?",
        "slang": ["dasheen", "market money", "Creole fest", "lime spot"],
    },
    "Grenada": {
        "greeting": "Spice up yuh day!",
        "example": "How yuh stretching that Spicemas earnings this month?",
        "slang": ["Spicemas", "oil down", "market day", "shortknee"],
    },
    "Saint Kitts and Nevis": {
        "greeting": "Big up SKN!",
        "example": "What’s your plan for the Culturama profits?",
        "slang": ["Culturama", "Sugar Mas", "federation vibes", "beach lime"],
    },
    "Saint Lucia": {
        "greeting": "Lucian pride!",
        "example": "Let’s plan how to save some Jounen Kwéyòl earnings.",
        "slang": ["Jounen Kwéyòl", "Lucian Lime", "Gros Islet Friday", "carnival flow"],
    },
    "Saint Vincent and the Grenadines": {
        "greeting": "Vincy to de bone!",
        "example": "How yuh putting aside some Vincymas money?",
        "slang": ["Vincymas", "Vincy rum shop", "breadfruit oil down", "whine up"],
    },
    "Anguilla": {
        "greeting": "Straight outta AXA!",
        "example": "Budget that Anguilla Summer Festival hustle money.",
        "slang": ["Summer Festival", "boat race winnings", "island vibes", "beach bash"],
    },
    "Montserrat": {
        "greeting": "Emerald Isle strong!",
        "example": "What’s the plan for your St. Patrick’s Festival profits?",
        "slang": ["St. Patrick’s Festival", "volcano stories", "Irish vibes", "island lime"],
    },
}

INSTRUCTION_TEMPLATE = """
You are a helpful, youth-friendly Financial AI Agent focused on the Eastern Caribbean Currency Union (ECCU) but able to serve anyone globally.

Core capabilities (MUST use tools when applicable):
- Detect and warn about common scams
- Host interactive financial literacy quizzes (one question at a time)
- Recommend personalized side hustles
- Perform currency conversion using tools
- Create custom budget plans using tool-based inputs

Important rules:
- Always use available tools for the above tasks; do not fabricate financial facts.
- Be concise, positive, and practical. Show small, actionable steps.
- If the user is in an ECCU country, adapt tone, slang, and examples accordingly.
- If the user is not in an ECCU country, respond with a friendly, generic global tone.

Location context (from app):
- country: {country}
- region: {region}
- city: {city}
- latitude: {latitude}
- longitude: {longitude}
- is_eccu: {is_eccu}

Persona guidelines:
{persona_guidelines}

Examples to mirror when applicable:
- Dominica: "What would you do with $50 from selling dasheen?"
- Antigua and Barbuda: "Let’s budget your Wadadli Day income."

Quiz style:
- Keep it fun; give feedback after each answer; track score playfully.
- Offer next-step actions after the quiz (budgeting, side hustles, scam tips).
"""

# ----------------------------
# Location detection (profile-first, then IP)
# ----------------------------

# Normalize common aliases -> ISO names
_ALIASES = {
    "Antigua & Barbuda": "Antigua and Barbuda",
    "St. Kitts & Nevis": "Saint Kitts and Nevis",
    "St Kitts & Nevis": "Saint Kitts and Nevis",
    "St. Lucia": "Saint Lucia",
    "St Lucia": "Saint Lucia",
    "St. Vincent & the Grenadines": "Saint Vincent and the Grenadines",
    "St Vincent & the Grenadines": "Saint Vincent and the Grenadines",
}

# Country -> preferred currency
_COUNTRY_TO_CURRENCY = {
    # ECCU block
    "Anguilla": "XCD",
    "Antigua and Barbuda": "XCD",
    "Dominica": "XCD",
    "Grenada": "XCD",
    "Montserrat": "XCD",
    "Saint Kitts and Nevis": "XCD",
    "Saint Lucia": "XCD",
    "Saint Vincent and the Grenadines": "XCD",
    # Wider Caribbean commonly used
    "Barbados": "BBD",
    "Trinidad and Tobago": "TTD",
    "Jamaica": "JMD",
    "Bahamas": "BSD",
    "Haiti": "HTG",
    "Cuba": "CUP",
    "Dominican Republic": "DOP",
    # Fallbacks
    "United States": "USD",
    "United Kingdom": "GBP",
    "Canada": "CAD",
    "France": "EUR",
}

def _normalize_country_name(name: str | None) -> str:
    if not name:
        return ""
    name = name.strip()
    return _ALIASES.get(name, name)

def _country_to_iso2(name: str) -> str | None:
    try:
        c = pycountry.countries.lookup(_normalize_country_name(name))
        return c.alpha_2
    except Exception:
        return None

def _build_location(country: str, city: str = "", lat=None, lon=None, source="profile/ip/override") -> dict:
    country_norm = _normalize_country_name(country)
    iso2 = _country_to_iso2(country_norm) if country_norm else None
    currency = _COUNTRY_TO_CURRENCY.get(country_norm)
    return {
        "country": country_norm or None,
        "country_code": iso2,
        "city": city or None,
        "latitude": lat,
        "longitude": lon,
        "currency": currency,
        "is_eccu": bool(country_norm in _ECCU_SET),
        "source": source,
        "ts": int(time.time()),
    }

def _cached_location_valid(loc: dict) -> bool:
    if not isinstance(loc, dict):
        return False
    ts = loc.get("ts") or 0
    # 24h TTL
    return (time.time() - ts) < 24 * 3600 and bool(loc.get("country"))

def _ip_provider_ipwhois() -> dict | None:
    try:
        r = requests.get("https://ipwho.is/", timeout=8)
        j = r.json()
        if not j.get("success"):
            return None
        return _build_location(
            j.get("country"),
            city=j.get("city"),
            lat=j.get("latitude"),
            lon=j.get("longitude"),
            source="ipwho.is",
        )
    except Exception:
        return None

def _ip_provider_ipapi_co() -> dict | None:
    try:
        r = requests.get("https://ipapi.co/json/", timeout=8)
        j = r.json()
        country = j.get("country_name")
        if not country:
            return None
        return _build_location(
            country,
            city=j.get("city"),
            lat=j.get("latitude") or j.get("lat"),
            lon=j.get("longitude") or j.get("lon"),
            source="ipapi.co",
        )
    except Exception:
        return None

def _ip_provider_ipinfo() -> dict | None:
    try:
        r = requests.get("https://ipinfo.io/json", timeout=8)
        j = r.json()
        cc = j.get("country")  # e.g., "US"
        city = j.get("city")
        lat, lon = (None, None)
        loc = j.get("loc")
        if isinstance(loc, str) and "," in loc:
            try:
                lat, lon = [float(x) for x in loc.split(",", 1)]
            except Exception:
                pass
        country = None
        if cc:
            try:
                country = pycountry.countries.lookup(cc).name
            except Exception:
                pass
        if not country:
            return None
        return _build_location(country, city=city, lat=lat, lon=lon, source="ipinfo.io")
    except Exception:
        return None

def detect_user_location(force_refresh: bool = False) -> dict:
    """Prefer the wizard profile; otherwise try multiple IP providers. Cached with 24h TTL."""
    # Manual override for demos
    forced = st.secrets.get("FORCE_COUNTRY") if hasattr(st, "secrets") else None
    if forced:
        loc = _build_location(forced, source="secret.FORCE_COUNTRY")
        st.session_state["user_location"] = loc
        return loc

    # Cached value
    if not force_refresh:
        cached = st.session_state.get("user_location")
        if _cached_location_valid(cached):
            return cached

    # Wizard profile (most reliable)
    prof = st.session_state.get("user_profile") or {}
    prof_country = _normalize_country_name(prof.get("country"))
    if prof_country:
        loc = _build_location(prof_country, source="profile")
        st.session_state["user_location"] = loc
        return loc

    # IP fallbacks (server-sided, may be hosting region)
    for provider in (_ip_provider_ipwhois, _ip_provider_ipapi_co, _ip_provider_ipinfo):
        loc = provider()
        if loc:
            st.session_state["user_location"] = loc
            return loc

    # Nothing found; return empty location
    loc = _build_location(country="", city="", source="none")
    st.session_state["user_location"] = loc
    return loc

# ----------------------------
# Persona + instructions
# ----------------------------
def build_persona_guidelines(location: dict) -> str:
    country = location.get("country") or ""
    if location.get("is_eccu"):
        if country in COUNTRY_TONE:
            tone = COUNTRY_TONE[country]
            return (
                f"- Start with a localized greeting (e.g., '{tone['greeting']}').\n"
                f"- Use culturally relevant examples (e.g., {tone['example']}).\n"
                f"- Light slang allowed: {', '.join(tone['slang'])}. Keep it respectful and clear.\n"
                f"- Use EC$ (XCD) where currency appears; convert with tools if needed."
            )
        else:
            return (
                "- Use a warm ECCU tone with light island slang where natural.\n"
                "- Use examples around carnival gigs, market day sales, tourism tips.\n"
                "- Prefer EC$ (XCD) and show small-step savings and investing."
            )
    return (
        "- Use a neutral global tone.\n"
        "- Avoid local slang.\n"
        "- Use the user's local currency if known, otherwise USD; convert with tools."
    )

def build_instructions(location: dict) -> str:
    persona = build_persona_guidelines(location)
    profile = st.session_state.get("user_profile", {}) or {}
    tone_pref = profile.get("tone", "Friendly")
    goals = profile.get("goals", [])
    goals_str = ", ".join(goals) if goals else "general financial literacy"

    template = INSTRUCTION_TEMPLATE + f"""
User preferences:
- Preferred tone: {tone_pref}
- Primary goals: {goals_str}

When writing, mirror the preferred tone and favor suggestions that advance the user's stated goals.
"""
    return template.format(
        country=location.get("country"),
        region=location.get("region"),
        city=location.get("city"),
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        is_eccu=location.get("is_eccu"),
        persona_guidelines=persona,
    )


# ----------------------------
# Agent runner
# ----------------------------
def agent(message, image=None, location=None):
    instructions = build_instructions(location or {})
    _agent = Agent(
        name="💼 Financial AI Agent",
        model=OpenRouter(id=MODEL_ID, api_key=API_KEY, max_tokens=8000),
        tools=[
            DuckDuckGoTools(),
            YFinanceTools(historical_prices=True),
            GoogleSearchTools(),
            HackerNewsTools(),
            WikipediaTools(),
            currencyconverter,
            commonscams2,
            budgeting_function,
            investing_advice,
            get_random_side_job,
            generate_business_idea
        ],
        tool_choice="auto",
        instructions=instructions,
        add_history_to_messages=True,
    )

    if image:
        image = [Image(filepath=image)]

    return _agent.run(message=message, images=image, stream=True)
