# avatar_builder.py
from __future__ import annotations
from dataclasses import asdict
from pathlib import Path
import base64, urllib.parse, secrets, json, random
from typing import Dict, List

import numpy as np
import requests
import streamlit as st
from PIL import Image, ImageOps, ImageDraw, ImageColor

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

def _dicebear_build_url(style: str, seed: str, size: int, radius: int, bg_hex: str | None, params: Dict[str, str]) -> str:
    q = {"seed": seed, "size": str(size), "radius": str(radius)}
    if bg_hex:
        q["backgroundColor"] = bg_hex.lstrip("#")
    for k, v in params.items():
        if v and v != "none":
            q[k] = v
    return f"https://api.dicebear.com/9.x/{style}/svg?{urllib.parse.urlencode(q)}"

def _fetch_with_backoff(style: str, seed: str, size: int, radius: int, bg: str | None, params: Dict[str, str]) -> str:
    order = list(params.keys())
    attempt = params.copy()
    while True:
        url = _dicebear_build_url(style, seed, size, radius, bg, attempt)
        try:
            return _fetch_svg(url)
        except requests.HTTPError:
            if not order:
                raise
            attempt.pop(order.pop(), None)

def _apply_visibility_boost(params: Dict[str, str], force_glasses: bool, force_facial: bool, force_accessories: bool):
    # Many styles honor these *Probability fields; set to 100 to ensure visibility.
    if force_glasses and params.get("glasses") and params["glasses"] != "none":
        params["glassesProbability"] = "100"
    if force_facial and params.get("facialHair") and params["facialHair"] != "none":
        params["facialHairProbability"] = "100"
    if force_accessories and params.get("accessories") and params["accessories"] != "none":
        params["accessoriesProbability"] = "100"

# ---------- Optional libs for Photo mode & SVG->PNG ----------
_HAS_REM_BG = False
_HAS_OPENCV = False
_HAS_CAIRO = False
try:
    from rembg import remove as rembg_remove  # pip install rembg
    _HAS_REM_BG = True
except Exception:
    pass
try:
    import cv2  # pip install opencv-python-headless
    _HAS_OPENCV = True
except Exception:
    pass
try:
    import cairosvg  # pip install cairosvg
    _HAS_CAIRO = True
except Exception:
    pass

AVATAR_DIR = Path("files/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Generic helpers ----------
def _save_png(img: Image.Image, base_name: str) -> str:
    p = AVATAR_DIR / f"{base_name}.png"
    img.save(p, format="PNG")
    return str(p)

def _resize_to_square(img: Image.Image, size: int) -> Image.Image:
    return ImageOps.fit(img, (size, size), method=Image.LANCZOS)

def _rgba(hex_color: str) -> tuple[int, int, int, int]:
    try:
        r, g, b = ImageColor.getrgb(hex_color)
        return (r, g, b, 255)
    except Exception:
        return (241, 245, 249, 255)

def _ring_mask(size: int, inner_ratio=0.98, ring_px=6):
    mask_inner = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask_inner)
    r = int(size * inner_ratio)
    m = (size - r) // 2
    d.ellipse((m, m, m + r, m + r), fill=255)
    ring = None
    if ring_px:
        ring = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(ring)
        d2.ellipse(
            (ring_px // 2, ring_px // 2, size - 1 - ring_px // 2, size - 1 - ring_px // 2),
            outline=(255, 255, 255, 210),
            width=ring_px,
        )
    return mask_inner, ring

# ---------- PHOTO MODE ----------
def _detect_face_bbox(img: Image.Image) -> tuple[int, int, int, int] | None:
    if not _HAS_OPENCV:
        return None
    cv = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        return None
    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
    return tuple(map(int, faces[0]))

def _remove_background(img: Image.Image) -> Image.Image:
    if not _HAS_REM_BG:
        return img.convert("RGBA")
    try:
        arr = rembg_remove(np.array(img))
        return Image.fromarray(arr).convert("RGBA")
    except Exception:
        return img.convert("RGBA")

def _compose_photo_avatar(
    src_img: Image.Image,
    bg_color: str = "#F1F5F9",
    size: int = 512,
    zoom: float = 1.3,
    y_offset: int = 0,
    x_offset: int = 0,
    ring: bool = True,
) -> Image.Image:
    cut = _remove_background(src_img)
    bbox = _detect_face_bbox(src_img)
    if bbox:
        x, y, w, h = bbox
        cx, cy = x + w // 2, y + int(h * 0.55)
        r = int(max(w, h) * zoom)
        left, top = max(cx - r, 0), max(cy - r, 0)
        right, bottom = min(cx + r, src_img.width), min(cy + r, src_img.height)
        cut = cut.crop((left, top, right, bottom))
    else:
        s = min(src_img.width, src_img.height)
        left, top = (src_img.width - s) // 2, (src_img.height - s) // 2
        cut = cut.crop((left, top, left + s, top + s))

    if x_offset or y_offset:
        pad = max(abs(x_offset), abs(y_offset)) + 10
        tmp = Image.new("RGBA", (cut.width + pad * 2, cut.height + pad * 2), (0, 0, 0, 0))
        tmp.paste(cut, (pad + x_offset, pad + y_offset))
        cut = tmp

    cut = _resize_to_square(cut, size)
    inner_mask, ring_img = _ring_mask(size, inner_ratio=0.98, ring_px=6 if ring else 0)

    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(bg)
    d.ellipse((0, 0, size - 1, size - 1), fill=_rgba(bg_color))

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(bg)
    subject = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    subject.paste(cut, (0, 0), mask=inner_mask)
    canvas.alpha_composite(subject)
    if ring_img:
        canvas.alpha_composite(ring_img)
    return canvas

def photo_avatar_ui(email_hint: str | None) -> dict | None:
    st.write("**Upload a selfie or portrait** (background removed, face centered).")
    uploaded = st.file_uploader("Upload PNG/JPG", type=["png", "jpg", "jpeg"])
    if not uploaded:
        st.info("Tip: a clear, front-facing portrait works best.")
        return None

    try:
        src = Image.open(uploaded).convert("RGB")
    except Exception as e:
        st.error(f"Could not open image: {e}")
        return None

    c1, c2 = st.columns([1, 1])
    with c1:
        bg_color = st.color_picker("Background", "#FFF7CC")
        zoom = st.slider("Zoom", 1.0, 2.0, 1.3, 0.01)
        y_off = st.slider("Vertical offset", -200, 200, 0)
        x_off = st.slider("Horizontal offset", -200, 200, 0)
        ring = st.toggle("Show white ring", True)

    with c2:
        canvas = _compose_photo_avatar(src, bg_color=bg_color, zoom=zoom, y_offset=y_off, x_offset=x_off, ring=ring)
        st.image(canvas, caption="Preview", width=256)
        save_name = (email_hint or "user").replace("@", "_at_").replace(".", "_")
        if st.button("💾 Save avatar", type="primary", use_container_width=True):
            png_path = _save_png(canvas, base_name=f"{save_name}_avatar")
            st.session_state["avatar_saved_paths"] = {"png": png_path, "svg": None}
            st.success("Avatar saved!")
            return {"png_path": png_path, "svg_path": None, "config": {"mode": "photo", "bg": bg_color}}

    return None

# ---------- DICEBEAR (free) ----------
HUMAN_STYLES = {
    "adventurer":          {"supports": ["hair","eyes","eyebrows","mouth","glasses","skinColor","hairColor","accessories"]},
    "adventurer-neutral":  {"supports": ["hair","eyes","eyebrows","mouth","glasses","skinColor","hairColor","accessories"]},
    "avataaars-neutral":   {"supports": ["top","hairColor","eyes","eyebrows","mouth","facialHair","glasses","skinColor","clothes"]},
    "lorelei":             {"supports": ["hair","hairColor","eyes","mouth","glasses","skinColor","accessories"]},
    "notionists-neutral":  {"supports": ["hair","eyes","mouth","glasses","skinColor","clothes"]},
    "personas":            {"supports": ["hair","hairColor","eyes","mouth","glasses","skinColor","clothes"]},
    "open-peeps":          {"supports": ["hair","facialHair","glasses","body","skinColor"]},
}

OPTION_VALUES = {
    "hair":        ["short","long","curly","afro","bun","fade","mohawk","buzz"],
    "hairColor":   ["000000","2B2A33","5D4633","7B5B3A","A67C52"],
    "eyes":        ["round","oval","smile","wink","sleepy"],
    "eyebrows":    ["soft","straight","arched"],
    "mouth":       ["smile","neutral","open","grin","laugh"],
    "facialHair":  ["none","stubble","medium","beard","mustache"],
    "glasses":     ["none","round","square"],
    "skinColor":   ["F1CCB5","E8C3A1","D4A67E","BE8C63","A67453","8B5E3C","6D4A32"],
    "clothes":     ["tshirt","hoodie","shirt","blazer"],
    "top":         ["shortHair","longHair","hat","hijab","turban","noHair"],
    "accessories": ["none","earrings","earring","necklace","mask"],
    "body":        ["person","breasts"],
}

def dicebear_ui(email_hint: str | None) -> dict | None:
    st.write("**Generate a human-style avatar** (DiceBear, free).")
    STYLE_LIST = ["adventurer", "adventurer-neutral", "personas", "notionists-neutral", "avataaars-neutral"]

    c0, c1, c2, c3 = st.columns(4)
    with c0:
        style = st.selectbox("Style", STYLE_LIST, index=0)
    seed_key = f"db_seed_{style}"
    seed_default = st.session_state.get(seed_key, (email_hint or "guest"))
    with c1:
        seed = st.text_input("Seed (same seed → same avatar)", value=seed_default, key=seed_key)
    with c2:
        size = st.slider("Export size", 128, 1024, 512, 32)
    with c3:
        radius = st.slider("Corner radius", 0, 50, 50)

    bg = st.color_picker("Background", "#F1F5F9")

    schema = _load_schema(style)
    ADV_KEYS = ["hair","hairColor","eyes","eyebrows","mouth","glasses","facialHair","skinColor","clothes","top","accessories","body","nose"]
    params: Dict[str, str] = {}

    # Randomize seed & appearance
    r1, r2 = st.columns([1, 2])
    with r1:
        if st.button("🎲 Randomize seed"):
            st.session_state[seed_key] = secrets.token_hex(4)
            st.rerun()
    with r2:
        if st.button("🎲 Randomize appearance"):
            # flip each supported control to a random valid choice (if schema available)
            if schema:
                for k in ADV_KEYS:
                    enum_vals = _schema_enum(schema, k)
                    if enum_vals:
                        st.session_state[f"db_{k}_{style}"] = random.choice([""] + enum_vals)
                    elif k in ("hairColor","skinColor"):
                        # simple palette roll
                        st.session_state[f"db_{k}_{style}"] = random.choice(OPTION_VALUES[k])
            st.rerun()

    with st.expander("Advanced appearance", expanded=True if schema else False):
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
            else:
                continue

        _apply_visibility_boost(params, lock_glasses, lock_facial, lock_access)

    # Server-side preview (CSP-safe) with graceful backoff
    try:
        svg_preview = _fetch_with_backoff(style, st.session_state[seed_key], 256, radius, bg, params)
        b64 = base64.b64encode(svg_preview.encode("utf-8")).decode()
        st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" width="256">', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Preview failed. Falling back to defaults.\n{e}")
        try:
            svg_preview = _fetch_with_backoff(style, st.session_state[seed_key], 256, radius, bg, {})
            b64 = base64.b64encode(svg_preview.encode("utf-8")).decode()
            st.markdown(f'<img src="data:image/svg+xml;base64,{b64}" width="256">', unsafe_allow_html=True)
        except Exception:
            st.warning("Could not load any DiceBear preview in this environment.")

    # Save
    base = (email_hint or "user").replace("@", "_at_").replace(".", "_")
    if st.button("💾 Save avatar", type="primary"):
        try:
            svg = _fetch_with_backoff(style, st.session_state[seed_key], size, radius, bg, params)
            svg_path = AVATAR_DIR / f"{base}_avatar.svg"
            svg_path.write_text(svg, encoding="utf-8")

            png_path = None
            if _HAS_CAIRO:
                out_png = AVATAR_DIR / f"{base}_avatar.png"
                cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(out_png),
                                 output_width=size, output_height=size)
                png_path = str(out_png)

            st.session_state["avatar_saved_paths"] = {"svg": str(svg_path), "png": png_path}
            st.success("Avatar saved!")
            return {
                "svg_path": str(svg_path),
                "png_path": png_path,
                "config": {
                    "mode": "dicebear",
                    "style": style,
                    "seed": st.session_state[seed_key],
                    "bg": bg,
                    "radius": radius,
                    "params": params,
                },
            }
        except Exception as e:
            st.error(f"Could not save avatar: {e}")
    return None

# ---------- Public entry point for wizard ----------
def avatar_editor(email: str | None = None) -> dict | None:
    st.subheader("Choose your avatar")
    mode = st.radio("Mode", ["Photo (most realistic)", "DiceBear (free)"], horizontal=True)

    if mode == "Photo (most realistic)":
        if not _HAS_REM_BG or not _HAS_OPENCV:
            st.warning("Install `rembg` and `opencv-python-headless` for best results (background removal & auto-centering).")
        return photo_avatar_ui(email_hint=email)
    else:
        return dicebear_ui(email_hint=email)
