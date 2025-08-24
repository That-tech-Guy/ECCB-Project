# chatbot.py
from __future__ import annotations
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
import tempfile
import PyPDF2
import os
import requests
import base64, mimetypes
from pathlib import Path

# Import the modularized agent utilities
from agent import detect_user_location, agent as run_agent
from setup_wizard import ensure_profile_on_load, log_message, get_user_profile

# 🔒 Force profile setup if missing; update profile if it already exists
ensure_profile_on_load()
profile = get_user_profile()  # used for avatar + per-user logging (email)

load_dotenv()

# =========================
# Helpers: file processing
# =========================
def extract_pdf_text(pdf_file):
    """Extract text content from a PDF file using PyPDF2."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text_content = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text_content += (page.extract_text() or "") + "\n"
        return text_content.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def read_text_file(file):
    """Read text content from various file types."""
    try:
        content = file.read().decode('utf-8')
        return content
    except UnicodeDecodeError:
        try:
            file.seek(0)
            content = file.read().decode('latin-1')
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

# =========================
# Avatar loader (prefer PNG path; convert SVG if needed)
# =========================
def _avatar_src_from_profile(profile: dict) -> str:
    """
    Return a path for Streamlit chat avatar.
      1) Prefer PNG path (session, then profile).
      2) If only SVG exists, try convert to PNG; if that fails, return the SVG path.
      3) Last resort: emoji.
    """
    def _svg_to_png(svg_path: str) -> Optional[str]:
        try:
            import cairosvg  # optional dependency
        except Exception:
            return None
        try:
            svg_path = os.path.abspath(svg_path)
            png_path = str(Path(svg_path).with_suffix(".png"))
            with open(svg_path, "rb") as f:
                cairosvg.svg2png(bytestring=f.read(), write_to=png_path, output_width=512, output_height=512)
            return png_path if os.path.exists(png_path) else None
        except Exception:
            return None

    # 1) Session (freshly saved this run)
    paths = st.session_state.get("avatar_saved_paths") or {}
    png = paths.get("png")
    svg = paths.get("svg")
    if png and os.path.exists(png):
        return png
    if svg and os.path.exists(svg):
        # Try convert once
        png2 = _svg_to_png(svg)
        if png2 and os.path.exists(png2):
            st.session_state.setdefault("avatar_saved_paths", {})["png"] = png2
            return png2
        # Fallback: use SVG path directly
        return svg

    # 2) Persisted profile
    p_png = (profile or {}).get("avatar_png")
    if p_png and os.path.exists(p_png):
        return p_png
    p_svg = (profile or {}).get("avatar_svg")
    if p_svg and os.path.exists(p_svg):
        png2 = _svg_to_png(p_svg)
        if png2 and os.path.exists(png2):
            return png2
        return p_svg  # fallback to SVG path

    # 3) Emoji fallback
    return "👤"

# =========================
# Quick Actions menu helper
# =========================
def _show_menu():
    # reset quick actions and clear any active mode
    st.session_state["chat_quick_actions_shown"] = False
    st.session_state.pop("chat_mode", None)

# =========================
# MAIN: Chatbot UI
# =========================
def render_chatbot():
    # 🧠 Session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("🌋 SoufrièreSense AI")

    # 🌐 Prefer profile country; fallback to live detection
    profile_country = profile.get("country")
    profile_region  = "ECCU" if profile.get("is_eccu") else "Global"

    # Always define location (so run_agent(...) never sees an undefined variable)
    location = {
        "country": profile_country or "Unknown",
        "city": None,
        "is_eccu": profile.get("is_eccu", False)
    }

    if profile_country:
        badge = f"📍 {profile_country}"
    else:
        try:
            location = detect_user_location()
            loc_country = location.get("country") or "Unknown"
            loc_city = location.get("city") or ""
            badge = f"📍 {loc_city + ', ' if loc_city else ''}{loc_country}"
            profile_region = "ECCU" if location.get("is_eccu") else "Global"
        except Exception:
            badge = "📍 Unknown"

    st.caption(badge + f" · {profile_region}")


    # Inline open of the setup wizard if requested
    if st.session_state.get("open_setup_now"):
        try:
            from setup_wizard import render_setup_wizard
            # Hand control to the wizard; keep this page paused until done
            done = render_setup_wizard()
            if not done:
                st.stop()
            # Wizard signaled completion → continue with refreshed state
            st.session_state.pop("open_setup_now", None)
            st.rerun()
        except Exception:
            st.warning("Setup wizard not available on this page.")
            st.session_state.pop("open_setup_now", None)

    # ---- Top Menu button when inside a mode (secondary entry point)
    if st.session_state.get("chat_mode"):
        if st.button("☰ Menu", key="menu_btn", help="Show quick actions"):
            _show_menu()
            st.rerun()



    # Preload avatars (file path or emoji) for bubble renders
    profile_local = st.session_state.get("user_profile", {}) or profile or {}
    user_avatar_src = _avatar_src_from_profile(profile_local)
    bot_avatar_src  = "🌋"  # replace with a file path to your brand logo if desired

    # -----------------------------
    # Currency converter quick flow
    # -----------------------------
    def _currency_quick_flow():
        """Guided currency conversion with ECCU/Caribbean vs World sets,
        auto base from profile country first (then location if allowed), and strong validation."""
        st.subheader("💱 Quick Currency Converter")

        # --- Defaults & helpers ---
        p = st.session_state.get("user_profile", {}) or profile_local
        allow_loc = bool(p.get("allow_location", True))
        selected_base = (p.get("base_currency") or "XCD").upper()

        # ECCU & Caribbean list
        CARIBBEAN = ["XCD", "JMD", "TTD", "BBD", "BSD", "HTG", "CUP", "DOP"]
        COUNTRY_TO_CUR = {
            "Anguilla": "XCD", "Antigua & Barbuda": "XCD", "Dominica": "XCD", "Grenada": "XCD",
            "Montserrat": "XCD", "St. Kitts & Nevis": "XCD", "St. Lucia": "XCD", "St. Vincent & the Grenadines": "XCD",
            "Barbados": "BBD", "Trinidad & Tobago": "TTD", "Jamaica": "JMD", "Bahamas": "BSD",
            "Haiti": "HTG", "Cuba": "CUP", "Dominican Republic": "DOP",
            "United States": "USD", "United Kingdom": "GBP", "Canada": "CAD", "Eurozone": "EUR",
        }

        # Prefer profile country; fallback to live detection only if allowed and profile is empty
        try:
            ctry = (p.get("country") or "").strip()
            if (not ctry) and allow_loc:
                loc = detect_user_location()
                ctry = (loc.get("country") or "").strip()
            if ctry in COUNTRY_TO_CUR:
                selected_base = COUNTRY_TO_CUR[ctry]
        except Exception:
            pass

        # Inputs
        base = st.text_input("Base currency (ISO 4217)", value=selected_base).upper()
        set_choice = st.radio("Target currency set", ["ECCU & Caribbean", "World"], horizontal=True)

        if set_choice == "ECCU & Caribbean":
            eccu_carib = sorted(set(["XCD"] + CARIBBEAN))
            idx = eccu_carib.index("USD") if "USD" in eccu_carib else 0
            target = st.selectbox("Target currency", eccu_carib, index=idx)
        else:
            try:
                import pycountry
                world = sorted({c.alpha_3 for c in pycountry.currencies if hasattr(c, "alpha_3") and len(c.alpha_3) == 3})
            except Exception:
                world = ["USD", "GBP", "EUR", "CAD", "JMD", "TTD", "BBD", "BSD", "XCD"]
            for bad in ["XTS", "XXX"]:
                if bad in world:
                    world.remove(bad)
            default_idx = world.index("USD") if "USD" in world else 0
            target = st.selectbox("Target currency", world, index=default_idx)

        amount = st.number_input("Amount", min_value=0.0, value=100.0, step=1.0)

        def _valid_code(code: str) -> bool:
            return isinstance(code, str) and len(code) == 3 and code.isalpha()

        if st.button("Convert now"):
            b = (base or "").upper().strip()
            t = (target or "").upper().strip()

            if not _valid_code(b):
                st.error("❌ Base currency not recognized. Use a 3-letter ISO code (e.g., XCD, USD, JMD).")
                return
            if not _valid_code(t):
                st.error("❌ Target currency not recognized. Use a 3-letter ISO code (e.g., XCD, USD, JMD).")
                return

            from currency_converter import BASE_URL
            try:
                r = requests.get(BASE_URL, timeout=15)
                r.raise_for_status()
                data = r.json()
                rates = data.get("conversion_rates", {})
            except Exception as e:
                st.error(f"❌ Failed to fetch currency rates: {e}")
                return

            if b not in rates:
                st.error(f"❌ Base currency '{b}' not found in rate table.")
                return
            if t not in rates:
                st.error(f"❌ Target currency '{t}' not found in rate table.")
                return

            try:
                res = amount * (rates.get(t, 0.0) / (rates.get(b, 1e-12) or 1e-12))
            except Exception:
                st.error("❌ Conversion failed due to a numeric error.")
                return

            st.success(f"{amount:,.2f} {b} → {res:,.2f} {t}")
            st.caption("Source: ExchangeRate-API (USD-based).")

            # --- Branch: if the user converted INTO EC$ (XCD), suggest local investing ideas ---
            ECCU_CURRENCY = "XCD"
            if t == ECCU_CURRENCY:
                st.divider()
                st.subheader("📈 Investing ideas for your EC$")

                # Prefer setup wizard country; else try live location; else let user pick
                pp = st.session_state.get("user_profile", {}) or {}
                country = (pp.get("country") or "").strip()

                # normalize common short forms
                _ALIASES = {
                    "Antigua & Barbuda": "Antigua and Barbuda",
                    "St. Kitts & Nevis": "Saint Kitts and Nevis",
                    "St Kitts & Nevis": "Saint Kitts and Nevis",
                    "St. Lucia": "Saint Lucia",
                    "St Lucia": "Saint Lucia",
                    "St. Vincent & the Grenadines": "Saint Vincent and the Grenadines",
                    "St Vincent & the Grenadines": "Saint Vincent and the Grenadines",
                }
                country = _ALIASES.get(country, country)

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

                if not country or country not in ECCU_COUNTRIES:
                    # Try live location as a helpful fallback
                    try:
                        loc = detect_user_location()
                        maybe = (loc.get("country") or "").strip()
                        country = _ALIASES.get(maybe, maybe)
                    except Exception:
                        pass

                if not country or country not in ECCU_COUNTRIES:
                    country = st.selectbox("Pick your ECCU country", ECCU_COUNTRIES)

                # Heuristic age group from setup role
                role = (pp.get("role") or "").lower()
                age_group = "youth" if role == "student" else "adult"

                # Try to use your investing tool; if it doesn't return a list, fall back to local data
                recs = None
                try:
                    from save_invest import investing_advice as _invest
                    maybe = _invest(country, age_group)
                    if isinstance(maybe, (list, tuple)):
                        recs = list(maybe)
                except Exception:
                    recs = None

                if not recs:
                    # Fallback recommendations per country (short + practical)
                    RECS = {
                        "Antigua and Barbuda": {
                            "youth": [
                                "Open a youth saver/CD at a local bank; auto-save part of side-hustle income.",
                                "Join a school/college savings club or co-op; set a weekly EC$ goal.",
                                "Learn the basics with a small mutual fund or ETF via a supervised account.",
                            ],
                            "adult": [
                                "Use fixed deposits or credit-union partner plans for guaranteed returns.",
                                "Consider government T-Bills/Bonds for conservative growth.",
                                "Co-invest in tourism micro-businesses (tours, rentals) with solid cashflow.",
                            ],
                        },
                        "Dominica": {
                            "youth": [
                                "Use NBD junior accounts + set a monthly auto-transfer.",
                                "Save profits from market sales (dasheen, produce) toward a small CD.",
                                "Learn about gov’t savings bonds as a first safe instrument.",
                            ],
                            "adult": [
                                "Buy gov’t T-Bills/Bonds; ladder maturities for liquidity.",
                                "Credit union fixed-share plans for steady EC$ growth.",
                                "Eco-tourism or agro-processing micro-investments with vetted partners.",
                            ],
                        },
                        "Grenada": {
                            "youth": [
                                "Join Early Savers/Junior accounts; save seasonal income (Spicemas gigs).",
                                "Start a tiny emergency fund (EC$300–500) before investing.",
                                "Practice dollar-cost averaging into a regional index fund (small amounts).",
                            ],
                            "adult": [
                                "Use fixed deposits; compare bank vs credit-union yields.",
                                "Consider real-asset co-ownership (equipment for agro/fishing).",
                                "Explore government instruments for conservative returns.",
                            ],
                        },
                        "Saint Kitts and Nevis": {
                            "youth": [
                                "Open a Youth Saver; auto-save allowances/side gigs.",
                                "Learn via mock portfolios before buying real funds.",
                                "Participate in school/club co-op savings challenges.",
                            ],
                            "adult": [
                                "Fixed deposits & gov’t T-Bills; ladder 3/6/12-month terms.",
                                "Solar/energy co-ops for dividend-like cashflows.",
                                "Real estate/tourism shares with careful due diligence.",
                            ],
                        },
                        "Saint Lucia": {
                            "youth": [
                                "Use youth accounts; save carnival/holiday income.",
                                "Take an intro investing course; start micro-investing monthly.",
                                "Build a starter emergency fund (1–2 months expenses).",
                            ],
                            "adult": [
                                "Credit-union products + gov’t bonds for base portfolio.",
                                "Tourism-adjacent rentals or land leasing (evaluate cashflow).",
                                "Gradually add diversified funds for growth.",
                            ],
                        },
                        "Saint Vincent and the Grenadines": {
                            "youth": [
                                "Join Youth Savers; set an EC$10/day habit.",
                                "Save side-hustle/freelance income toward a 6-month CD.",
                                "Study basic ETFs before buying anything.",
                            ],
                            "adult": [
                                "Fixed-term accounts; compare rates at banks/credit unions.",
                                "Co-own small equipment for fishing or agro processing.",
                                "T-Bills/Bonds for stability; diversify gradually.",
                            ],
                        },
                        "Anguilla": {
                            "youth": [
                                "Youth saver/CD accounts; automate 10–20% of income.",
                                "Learn budgeting + set a quarterly savings challenge.",
                                "Start with a conservative fund via supervised account.",
                            ],
                            "adult": [
                                "Term deposits for safe yield; roll maturities.",
                                "Local small-business co-investment (tourism services).",
                                "Gov’t bonds or regional funds for diversification.",
                            ],
                        },
                        "Montserrat": {
                            "youth": [
                                "Join a junior savings club; auto-save from summer/part-time jobs.",
                                "Target EC$1k emergency fund before investing.",
                                "Learn investing basics; try tiny monthly index-fund buys.",
                            ],
                            "adult": [
                                "Term deposits at Bank of Montserrat; compare rates/penalties.",
                                "Participate in vetted community co-ops (housing/energy).",
                                "Use gov’t savings bonds for low-risk returns.",
                            ],
                        },
                    }
                    recs = RECS.get(country, {}).get(age_group, [])

                if recs:
                    st.write(f"**Country:** {country}  ·  **Profile:** {'Student/Youth' if age_group=='youth' else 'Adult'}")
                    for r in recs:
                        st.markdown(f"- {r}")
                    st.info("These are general ideas — match them to your risk, goals, and time horizon.")
                    if st.button("Open Investing Assistant"):
                        st.session_state["chat_quick_actions_shown"] = True
                        st.session_state["chat_mode"] = "invest"
                else:
                    st.write("Pick your ECCU country above to see investing ideas.")

        # Optional back button inside the flow
        cols = st.columns([1, 6])
        if cols[0].button("← Back"):
            _show_menu()
            st.rerun()



    # Render selected quick action flow
    mode = st.session_state.get("chat_mode")
    if mode == "currency":
        _currency_quick_flow()
    elif mode == "budget":
        from budget_gen import gen_budget
        gen_budget()
    elif mode == "hustles":
        from small_hustles import run_small_hustles
        run_small_hustles()
    elif mode == "scam":
        from common_scams import run_common_scams
        run_common_scams()
    elif mode == "invest":
        try:
            from save_invest import invest
            invest()
        except Exception:
            st.warning("Investing module is unavailable right now.")

    # 🗨️ Render history with avatars
    for msg in st.session_state.messages:
        avatar = user_avatar_src if msg["role"] == "user" else bot_avatar_src
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

      # --- Quick actions panel at the bottom (above chat input) ---
    # Initialize flags once
    if "chat_quick_actions_shown" not in st.session_state:
        st.session_state["chat_quick_actions_shown"] = False

    # If user typed "menu", _show_menu() already set the flags & did rerun.
    # Now render the panel here at the bottom:
    if not st.session_state["chat_quick_actions_shown"]:
        st.markdown("---")
        with st.container(border=True):
            st.write("Quick actions:")
            cols = st.columns(4)
            if cols[0].button("💱 Convert Currency", key="qa_currency"):
                st.session_state["chat_quick_actions_shown"] = True
                st.session_state["chat_mode"] = "currency"
                st.rerun()
            if cols[1].button("📊 Budget Plan", key="qa_budget"):
                st.session_state["chat_quick_actions_shown"] = True
                st.session_state["chat_mode"] = "budget"
                st.rerun()
            if cols[2].button("🧵 Small Hustles", key="qa_hustles"):
                st.session_state["chat_quick_actions_shown"] = True
                st.session_state["chat_mode"] = "hustles"
                st.rerun()
            if cols[3].button("🚨 Scam Check", key="qa_scam"):
                st.session_state["chat_quick_actions_shown"] = True
                st.session_state["chat_mode"] = "scam"
                st.rerun()


    # 📥 Chat input (with file upload)
    if data := st.chat_input("Ask me anything... Type 'menu' or '/setup'.", accept_file=True):

        # Extract text prompt and uploaded files from the input data
        prompt_raw = data.get("text", None) or ""
        prompt = prompt_raw.strip()

        # ---- Intercept commands (do not send to agent)
        low = prompt.lower()
        if low in {"menu", "/menu", "help", "options", "show menu"}:
            _show_menu()
            st.info("Opened the quick actions menu.")
            st.rerun()
            return
        if low in {"setup", "/setup"}:
            st.session_state["open_setup_now"] = True
            st.rerun()
            return

        uploaded_files = data.get("files", None)

        # Initialize user message
        user_message = {"role": "user", "content": prompt}

        # Process uploaded files if any
        file_content = ""
        image_files = []

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name.lower()
                file_extension = file_name.split('.')[-1] if '.' in file_name else ""

                if file_extension == "pdf":
                    pdf_text = extract_pdf_text(uploaded_file)
                    file_content += f"\n\n**PDF Content ({file_name}):**\n{pdf_text}\n"

                elif file_extension in ["txt", "md", "py", "js", "html", "css", "json", "xml", "csv"]:
                    text_content = read_text_file(uploaded_file)
                    file_content += f"\n\n**File Content ({file_name}):**\n{text_content}\n"

                elif file_extension in ["jpg", "jpeg", "png", "gif", "bmp", "webp"]:
                    image_files.append(uploaded_file)
                    user_message["image"] = uploaded_file

                else:
                    try:
                        text_content = read_text_file(uploaded_file)
                        file_content += f"\n\n**File Content ({file_name}):**\n{text_content}\n"
                    except Exception:
                        file_content += f"\n\n**Unsupported file type: {file_name}**\n"

        # Combine prompt with file content
        if file_content:
            user_message["content"] = (prompt or "") + file_content

        # Add user message to chat history
        st.session_state.messages.append(user_message)

        # ⏺️ Log the user message (per-user JSONL)
        try:
            log_message("user", user_message["content"], email=profile.get("email"))
        except Exception:
            pass

        # Display user message in chat (with avatar)
        with st.chat_message("user", avatar=user_avatar_src):
            if image_files:
                for img_file in image_files:
                    st.image(img_file, width=200)
            st.markdown(user_message["content"])

        # Generate assistant response (with avatar)
        with st.chat_message("assistant", avatar=bot_avatar_src):
            message_placeholder = st.empty()
            action_placeholder = st.empty()  # For displaying tool actions
            full_response = ""
            current_action = None

            try:
                # Handle image files for the agent
                image_path = None
                if image_files:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{image_files[0].name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(image_files[0].getvalue())
                        image_path = tmp_file.name

                # Get streaming response from the AI agent
                response_stream = run_agent(st.session_state.messages, image_path, location=location)

                # Process and display the streaming response
                for chunk in response_stream:
                    if hasattr(chunk, 'event'):
                        if chunk.event == 'RunResponseContent':
                            if hasattr(chunk, 'content') and chunk.content:
                                full_response += chunk.content
                                if current_action:
                                    action_placeholder.empty()
                                    current_action = None

                        elif chunk.event == 'ToolCallStarted':
                            tool_name = chunk.tool.tool_name if hasattr(chunk.tool, 'tool_name') else "Unknown Tool"
                            current_action = f"🔧 Calling {tool_name}..."
                            action_placeholder.info(current_action)

                        elif chunk.event == 'ToolCallCompleted':
                            if current_action:
                                action_placeholder.success("✅ Tool call completed")

                    if full_response:
                        message_placeholder.markdown(full_response + "● ")

                if image_path:
                    os.unlink(image_path)

            except Exception as e:
                full_response = f"Error: {str(e)}"
                if current_action:
                    action_placeholder.empty()

            action_placeholder.empty()
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        assistant_message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(assistant_message)

        # ⏺️ Log the assistant reply
        try:
            log_message("assistant", full_response, email=profile.get("email"))
        except Exception:
            pass
