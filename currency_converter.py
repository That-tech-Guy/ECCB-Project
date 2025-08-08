import streamlit as st
import requests
from datetime import datetime, timezone
from typing import Dict, Tuple, List

# =========================
# CONFIG (same API + list)
# =========================
API_KEY = "759cc97900658c57b71d7b1d"  # Your API key here
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

CARIBBEAN_CURRENCIES = ["XCD", "JMD", "TTD", "BBD", "BSD", "HTG", "CUP", "DOP"]
SUPPORTED = CARIBBEAN_CURRENCIES + ["USD"]

# Common “bank site” pairs to showcase
COMMON_PAIRS = [
    ("USD", "XCD"),
    ("USD", "JMD"),
    ("USD", "TTD"),
    ("USD", "BBD"),
    ("USD", "DOP"),
    ("USD", "BSD"),  # parity
]

# =========================
# SMALL HELPERS (cached)
# =========================
@st.cache_data(ttl=60, show_spinner=False)
def _get_rates() -> Dict[str, float]:
    """Fetch latest USD-based rates; cache for 60s."""
    resp = requests.get(BASE_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("conversion_rates", {}) or {}

def _convert_amount(amount: float, base: str, target: str, rates: Dict[str, float]) -> float:
    if base == target:
        return amount
    if base == "USD":
        return amount * rates.get(target, 0.0)
    if target == "USD":
        return amount / max(rates.get(base, 0.0), 1e-12)
    # cross via USD
    usd_amt = amount / max(rates.get(base, 0.0), 1e-12)
    return usd_amt * rates.get(target, 0.0)

def _compute_deltas(prev: Dict[str, float], curr: Dict[str, float]) -> Dict[Tuple[str, str], float]:
    """% change vs previous fetch for COMMON_PAIRS."""
    out: Dict[Tuple[str, str], float] = {}
    if not prev:
        return out
    for base, target in COMMON_PAIRS:
        # previous value of 1 base in target
        if base == target:
            pv = 1.0
        elif base == "USD":
            pv = prev.get(target, 0.0)
        elif target == "USD":
            b = prev.get(base, 0.0)
            pv = (1.0 / b) if b else 0.0
        else:
            b, t = prev.get(base, 0.0), prev.get(target, 0.0)
            pv = (t / b) if (b and t) else 0.0
        cv = _convert_amount(1.0, base, target, curr)
        if pv and cv:
            out[(base, target)] = (cv - pv) / pv * 100.0
    return out

def _rate_chip(base: str, target: str, rates: Dict[str, float], deltas: Dict[Tuple[str, str], float]):
    """Render a compact chip like a banking site."""
    value = _convert_amount(1.0, base, target, rates)
    delta = deltas.get((base, target), 0.0)
    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "•"
    color = "#2e7d32" if delta > 0 else "#c62828" if delta < 0 else "#6b7280"
    delta_txt = f"{arrow} {abs(delta):.2f}%" if delta != 0 else "—"
    st.markdown(
        f"""
        <div style="
          display:flex;flex-direction:column;gap:2px;
          border:1px solid #e5e7eb;border-radius:12px;padding:10px 12px;
          box-shadow:0 2px 6px rgba(0,0,0,0.05);background:white;min-width:205px;">
          <div style="font-size:12px;color:#6b7280;">1 {base} =</div>
          <div style="font-weight:800;font-size:18px;color:#111827;">{value:,.4f} {target}</div>
          <div style="font-size:12px;color:{color};">{delta_txt} today</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# YOUR EXISTING FUNCTIONS
# =========================
def currencyconverter(base: str, target: str, amount: float) -> str:
    base = base.upper()
    target = target.upper()

    if base not in SUPPORTED:
        return f"❌ Base currency '{base}' is not supported. Use Caribbean currencies or USD."
    if target not in SUPPORTED:
        return f"❌ Target currency '{target}' is not supported. Use Caribbean currencies or USD."

    try:
        rates = _get_rates()
    except Exception as e:
        return f"❌ Failed to fetch currency rates: {str(e)}"

    # Guard missing
    if base != "USD" and base not in rates:
        return f"❌ Base currency '{base}' not found in conversion rates."
    if target != "USD" and target not in rates:
        return f"❌ Target currency '{target}' not found in conversion rates."

    converted = _convert_amount(amount, base, target, rates)
    return f"{amount:.2f} {base} = {converted:.2f} {target}"

def converter():
    st.header("💱 Currency Converter")
    st.markdown("Convert between **Caribbean currencies and USD** and see a live tracker of common pairs (rates auto-refresh ~60s).")

    # Fetch rates once for this render
    try:
        rates = _get_rates()
        if not rates:
            st.error("Could not load rates. Please try again later.")
            return
    except Exception as e:
        st.error(f"Failed to fetch currency rates: {e}")
        return

    # Deltas vs previous pull (same session)
    if "prev_rates" not in st.session_state:
        st.session_state.prev_rates = {}
    deltas = _compute_deltas(st.session_state.prev_rates, rates)
    st.session_state.prev_rates = rates

    # --- Live tracker header
    top_l, top_r = st.columns([1, 1])
    with top_l:
        st.subheader("📈 Live Tracker")
        st.caption("Bank-style quick rates for common pairs")
    with top_r:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        st.write(f"**Last updated:** {now}")

    # --- Show chips in a grid (2 rows x 3)
    rows = [COMMON_PAIRS[:3], COMMON_PAIRS[3:]]
    for row in rows:
        cols = st.columns(len(row))
        for i, (b, t) in enumerate(row):
            with cols[i]:
                _rate_chip(b, t, rates, deltas)

    st.divider()

    # --- Your original converter UI (kept same)
    currencies = SUPPORTED
    col1, col2 = st.columns(2)
    with col1:
        base_currency = st.selectbox("From Currency", currencies, index=0)
    with col2:
        target_currency = st.selectbox("To Currency", currencies, index=currencies.index("USD"))

    amount = st.number_input("Enter amount to convert", min_value=0.0, value=100.0, format="%.2f")

    if st.button("Convert"):
        result = currencyconverter(base_currency, target_currency, amount)
        st.success(result)

    # --- Optional: quick board for the chosen base (1 BASE → all)
    with st.expander("📋 Full board for your base (1 → all)"):
        base_for_board = base_currency
        data = []
        for cur in currencies:
            rate = _convert_amount(1.0, base_for_board, cur, rates)
            data.append({"Pair": f"1 {base_for_board} → {cur}", "Rate": f"{rate:,.6f}"})
        st.dataframe(data, use_container_width=True, hide_index=True)
        st.caption("Rates are indicative and refresh ~60s.")
