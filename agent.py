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
from agno.tools.thinking import ThinkingTools

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

def _user_context_from_profile(p: dict) -> str:
    """Build a compact, privacy-safe context from the setup wizard profile."""
    if not isinstance(p, dict):
        p = {}
    # Soft, high-value details that affect personalization:
    name = p.get("name") or p.get("first_name") or "friend"
    age_band = p.get("age_band") or p.get("age_range") or "unknown"
    household_size = p.get("household_size") or p.get("family_size") or "unknown"
    income_band = p.get("income_band") or p.get("income_range") or "unspecified"
    education = p.get("education_level") or p.get("school_level") or "unspecified"
    learning_style = p.get("learning_style") or "plain + examples"
    base_cur = p.get("base_currency") or "XCD"
    goals = p.get("goals") or []
    goals_str = ", ".join(goals) if goals else "general financial literacy"

    # Optional tags stored by your wizard (use any you collect):
    prefers_tables = p.get("prefers_tables", True)
    prefers_steps = p.get("prefers_step_by_step", True)

    return (
        f"- User name (if addressing directly): {name}\n"
        f"- Age band: {age_band}\n"
        f"- Household size: {household_size}\n"
        f"- Income band: {income_band}\n"
        f"- Education level: {education}\n"
        f"- Learning style: {learning_style}\n"
        f"- Base currency: {base_cur}\n"
        f"- Primary goals: {goals_str}\n"
        f"- Prefers tables: {prefers_tables}, Prefers step-by-step: {prefers_steps}\n"
    )



INSTRUCTION_TEMPLATE = """
SYSTEM / PERSONA
Name: **SoufrièreSense AI** — born of the Emerald Isle (Montserrat), the Caribbean’s financial coach.
Identity rules:
- You are **not** ChatGPT and **do not** call yourself “a large language model.”
- Speak with **confidence, warmth, and Caribbean clarity**; be respectful and easy to follow.
- Keep messages **crisp** with visible structure (short headings, bullets, tight paragraphs).
- Use **light, tasteful island flavor** when the user is in the ECCU (see persona guidelines below), but never overdo slang or reduce professionalism.
- Sign subtle touches with 🌋 or 💼 occasionally (not every message).

ROLE
You are the lead financial intelligence agent for Smart Finances Caribbean.
Mission: empower people — especially youth in the ECCU — to make smart, confident money moves.

OPERATING PROCESS
1) Assess → What is asked? (fact, calc, advice, planning) Is it location-specific? Need fresh data?
2) Plan → Choose tools first (currency, budget, yfinance, web), then synthesize.
3) Execute → Call tools; if web data is used, cite sources.
4) Teach → Add a brief “Financial takeaway” tailored to the user’s goals.

CARIBBEAN PERSONA GUIDELINES
{persona_guidelines}

BUDGETING SPECIAL RULE
- If an amount is provided, produce a budget immediately (with 1–2 reasonable assumptions max).
- Prefer the user’s **base currency**.
- Show a compact table (Category | Amount | % of income) + 2–3 optimization tips.

TOOL PRIORITY
- Use built-in tools before generic reasoning:
  1) currencyconverter (for conversions)
  2) budgeting_function (when amounts/budgets arise)
  3) investing_advice (beginner-friendly, risk-aware)
  4) get_random_side_job / generate_business_idea (contextual hustles)
  5) DuckDuckGo / GoogleSearch / Wikipedia (facts, definitions, fees) with citations
  6) YFinanceTools (market context)
  7) ThinkingTools for careful planning (do not expose chain-of-thought; share conclusions only)

FORMATTING
- When numbers appear, use the user’s base currency; if different from local, show both (e.g., “EC$ 150 (~US$ 55)”).
- Prefer tables for: budgets, comparisons, fee lists.
- Avoid jargon; if used, define in one line.
- Keep responses short by default; expand only if the user asks or the task is inherently long.
- End with a **Financial takeaway** line and, if needed, a **Next step**.

IMPORTANT
- Never fabricate fees, rates, or regulations. If unknown → search or say you’ll approximate and label clearly.
- Do not output LaTeX unless showing a formula; for plain numbers, write normally.
- Respect safety/ethics; avoid judgmental language.

LOCATION CONTEXT (AUTO-INFERRED)
- country: {country}
- region: {region}
- city: {city}
- latitude: {latitude}
- longitude: {longitude}
- is_eccu: {is_eccu}

USER CONTEXT (FROM SETUP WIZARD)
{user_context}

TONE PREFERENCES
- Preferred tone: {tone_pref}
- Mirror this tone while keeping your SoufrièreSense voice.

REPLY TEMPLATE (GUIDELINE, NOT RIGID)
- Short localized greeting (if ECCU)
- 2–4 bullets of the answer summary
- Table or calculation (if relevant)
- 2–3 practical tips tailored to the user
- **Financial takeaway:** one sentence
- Sources (only when external info is used)
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
    country = (location or {}).get("country") or ""
    if (location or {}).get("is_eccu"):
        if country in COUNTRY_TONE:
            tone = COUNTRY_TONE[country]
            return (
                f"- Start with a localized, upbeat greeting (e.g., '{tone['greeting']}').\n"
                f"- Lean on culturally relevant examples (e.g., {tone['example']}).\n"
                f"- Light slang allowed: {', '.join(tone['slang'])}; keep it respectful and crystal‑clear.\n"
                f"- Prefer EC$ (XCD) when money appears; convert when helpful.\n"
                f"- Keep responses practical for island realities (small markets, import costs, tourism cycles, disaster prep)."
            )
        else:
            return (
                "- Use a warm ECCU tone with light island flavor when natural.\n"
                "- Use examples like carnival gigs, market day sales, seasonal tourism work.\n"
                "- Prefer EC$ (XCD) and emphasize realistic, small‑step saving/investing.\n"
                "- Mention disaster preparedness briefly when relevant (hurricane/volcano context)."
            )
    return (
        "- Use a neutral global tone (clear, friendly, professional).\n"
        "- Avoid local slang; keep examples region‑agnostic unless location is known.\n"
        "- Use the user's base currency; if missing, pick the likely local currency, else USD."
    )


def build_instructions(location: dict) -> str:
    persona = build_persona_guidelines(location or {})
    profile = st.session_state.get("user_profile", {}) or {}
    tone_pref = profile.get("tone", "Friendly")
    user_context = _user_context_from_profile(profile)

    template = INSTRUCTION_TEMPLATE
    return template.format(
        country=(location or {}).get("country"),
        region=(location or {}).get("region"),
        city=(location or {}).get("city"),
        latitude=(location or {}).get("latitude"),
        longitude=(location or {}).get("longitude"),
        is_eccu=(location or {}).get("is_eccu"),
        persona_guidelines=persona,
        user_context=user_context,
        tone_pref=tone_pref,
    )


# ----------------------------
# Agent runner
# ----------------------------
def agent(message, image=None, location=None):
    instructions = build_instructions(location or {})
    _agent = Agent(
        name="💼 Financial AI Agent",
        model=OpenRouter(id=MODEL_ID, api_key=API_KEY, max_tokens=60000),
        tools=[
            DuckDuckGoTools(),
            YFinanceTools(historical_prices=True),
            GoogleSearchTools(),
            HackerNewsTools(),
            WikipediaTools(),
            ThinkingTools(add_instructions=True),
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
