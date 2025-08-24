# avatar_builder.py
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
import base64, urllib.parse, json, random, re, uuid, time

import requests
import streamlit as st

# ---------- Storage ----------
AVATAR_DIR = Path("files/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Per-session / per-user helpers ----------
def _sanitize_email(email: str) -> str:
    email = (email or "").strip().lower().replace("@", "_at_").replace(".", "_")
    return re.sub(r"[^a-z0-9_]+", "", email) or "guest"

def _session_uid() -> str:
    if "session_uid" not in st.session_state:
        st.session_state["session_uid"] = str(uuid.uuid4())
    return st.session_state["session_uid"]

def _user_key(email_hint: Optional[str]) -> str:
    """Stable per user if email provided; else per-session UUID."""
    if email_hint and isinstance(email_hint, str) and email_hint.strip():
        return _sanitize_email(email_hint)
    return f"guest_{_session_uid()}"

def avatar_path_for_current_user(email_hint: Optional[str] = None) -> Path:
    return AVATAR_DIR / f"{_user_key(email_hint)}_avatar.svg"

def avatar_png_path_for_current_user(email_hint: Optional[str] = None) -> Path:
    return AVATAR_DIR / f"{_user_key(email_hint)}_avatar.png"

def avatar_exists_for_current_user(email_hint: Optional[str] = None) -> bool:
    return avatar_path_for_current_user(email_hint).exists()

# ---------- Cache helpers ----------
@st.cache_data(show_spinner=False, ttl=900)
def _fetch_svg(url: str) -> str:
    r = requests.get(url, timeout=20, headers={"User-Agent": "ECCB-Avatar/1.0"})
    r.raise_for_status()
    return r.text

@st.cache_data(show_spinner=False, ttl=3600)
def _load_schema(style: str) -> dict | None:
    try:
        url = f"https://api.dicebear.com/9.x/{style}/schema.json"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None

def _schema_enum(schema: dict, key: str) -> List[str] | None:
    try:
        prop = (schema or {}).get("properties", {}).get(key, {})
        if "items" in prop and "enum" in prop["items"]:
            return prop["items"]["enum"]
        if "enum" in prop:
            return prop["enum"]
    except Exception:
        pass
    return None

# ---------- DiceBear fetch (radius fixed at 0, size fixed at 512) ----------
def _dicebear_build_url(style: str, seed: str, params: Dict[str, str]) -> str:
    q = {"seed": seed, "size": "512", "radius": "0"}  # fixed values
    for k, v in params.items():
        if v and v != "none":
            q[k] = v
    return f"https://api.dicebear.com/9.x/{style}/svg?{urllib.parse.urlencode(q)}"

def _fetch_with_backoff(style: str, seed: str, params: Dict[str, str]) -> str:
    order = list(params.keys())
    attempt = params.copy()
    delay = 0.5
    last = None
    for _ in range(3 + len(order)):
        try:
            url = _dicebear_build_url(style, seed, attempt)
            return _fetch_svg(url)
        except Exception as e:
            last = e
            if order:
                attempt.pop(order.pop(), None)
            time.sleep(delay)
            delay *= 1.6
    raise last or RuntimeError("DiceBear unavailable")

# ---------- UI ----------
HUMAN_STYLES = [
    "adventurer",
    "personas",
]

OPTION_VALUES = {
    "hairColor": ["000000","2B2A33","5D4633","7B5B3A","A67C52"],
    "skinColor": ["F1CCB5","E8C3A1","D4A67E","BE8C63","A67453","8B5E3C","6D4A32"],
}

def dicebear_ui(email_hint: Optional[str]) -> dict | None:
    st.write("**Generate a human-style avatar** (DiceBear).")

    style = st.selectbox("Style", HUMAN_STYLES, index=0)

    # derive a stable seed silently (NO seed input; NO size/radius sliders)
    seed = _user_key(email_hint)

    schema = _load_schema(style)
    ADV_KEYS = ["hair","hairColor","eyes","eyebrows","mouth","glasses","facialHair","skinColor","clothes","top","accessories","body","nose"]
    params: Dict[str, str] = {}

    # Randomize appearance ONLY (keep this)
    if st.button("🎲 Randomize appearance"):
        if schema:
            for k in ADV_KEYS:
                enum_vals = _schema_enum(schema, k)
                if enum_vals:
                    st.session_state[f"db_{k}_{style}"] = random.choice([""] + enum_vals)
                elif k in ("hairColor","skinColor"):
                    st.session_state[f"db_{k}_{style}"] = random.choice(OPTION_VALUES[k])
        st.rerun()

    with st.expander("Advanced appearance", expanded=False):
        if not schema:
            st.caption("Advanced options hidden (couldn't load schema). Saving still works with defaults.")
        lock_glasses = st.checkbox("Always show glasses if selected", value=True)
        lock_facial  = st.checkbox("Always show facial hair if selected", value=False)
        lock_access  = st.checkbox("Always show accessories if selected", value=False)

        for k in ADV_KEYS:
            enum_vals = _schema_enum(schema, k) if schema else None
            if enum_vals:
                params[k] = st.selectbox(k, [""] + enum_vals, index=0, key=f"db_{k}_{style}")
            elif k in ("hairColor","skinColor"):
                params[k] = st.text_input(k, value=("000000" if k == "hairColor" else "E8C3A1"), key=f"db_{k}_{style}")
        if lock_glasses and params.get("glasses") and params["glasses"] != "none":
            params["glassesProbability"] = "100"
        if lock_facial and params.get("facialHair") and params["facialHair"] != "none":
            params["facialHairProbability"] = "100"
        if lock_access and params.get("accessories") and params["accessories"] != "none":
            params["accessoriesProbability"] = "100"

    # Preview
    try:
        svg_preview = _fetch_with_backoff(style, seed, params)
        b64 = base64.b64encode(svg_preview.encode("utf-8")).decode()
        st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" width="256">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Preview failed: {e}")

    # Save
    if st.button("💾 Save avatar", type="primary"):
        try:
            svg = _fetch_with_backoff(style, seed, params)
            svg_path = avatar_path_for_current_user(email_hint)
            svg_path.write_text(svg, encoding="utf-8")

            png_path = None
            try:
                import cairosvg
                png_path = str(avatar_png_path_for_current_user(email_hint))
                cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=png_path,
                                 output_width=512, output_height=512)
            except Exception:
                pass

            cfg = {
                "mode": "dicebear",
                "style": style,
                "seed": seed,
                "radius": 0,
                "size": 512,
                "params": params,
            }
            st.session_state["avatar_saved_paths"] = {"svg": str(svg_path), "png": png_path}
            st.session_state["avatar_config"] = cfg
            st.success("Avatar saved!")
            return {"svg_path": str(svg_path), "png_path": png_path, "config": cfg}
        except Exception as e:
            st.error(f"Could not save avatar: {e}")
    return None

def avatar_editor(email: Optional[str] = None) -> dict | None:
    st.subheader("Choose your avatar")
    return dicebear_ui(email_hint=email)
