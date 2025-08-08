import streamlit as st
import random
import time
import json
from pathlib import Path

# =========================
#   TIMING (TOTAL = 15s)
# =========================
ANSWER_TIME = 10   # seconds to choose
REVEAL_TIME = 5    # seconds to view answer
TOTAL_TIME = ANSWER_TIME + REVEAL_TIME

def start_quiz():

    FILES_DIR = Path("files")
    QUESTIONS_PATH = FILES_DIR / "questions.json"
    SCORES_PATH = FILES_DIR / "scores.json"
    FILES_DIR.mkdir(parents=True, exist_ok=True)

    # =========================
    #         HELPERS
    # =========================
    @st.cache_data(show_spinner=False)
    def load_questions(path: Path = QUESTIONS_PATH):
        """Load and validate questions JSON."""
        if not path.exists():
            st.error(f"Questions file not found: {path}")
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            st.error(f"Failed to parse {path}: {e}")
            return []

        valid = []
        for i, q in enumerate(data):
            if not isinstance(q, dict):
                st.warning(f"Skipping item {i}: not an object")
                continue
            question = q.get("question")
            options = q.get("options")
            answer = q.get("answer")
            if not question or not isinstance(question, str):
                st.warning(f"Skipping item {i}: missing/invalid 'question'")
                continue
            if not options or not isinstance(options, list) or not all(isinstance(o, str) for o in options):
                st.warning(f"Skipping item {i}: missing/invalid 'options'")
                continue
            if len(options) < 2 or len(options) > 8:
                st.warning(f"Skipping item {i}: options must be between 2 and 8")
                continue
            if not answer or answer not in options:
                st.warning(f"Skipping item {i}: 'answer' missing or not in options")
                continue
            valid.append({
                "question": question.strip(),
                "options": [o.strip() for o in options],
                "answer": answer.strip(),
                **{k: v for k, v in q.items() if k not in ("question", "options", "answer")}
            })
        if not valid:
            st.error("No valid questions found in the JSON file.")
        return valid

    def load_scores():
        """Load scores list from file (no cache)."""
        if not SCORES_PATH.exists():
            return []
        try:
            return json.loads(SCORES_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []

    def save_score(entry: dict):
        """Append a score entry and persist to file."""
        scores = load_scores()
        scores.append(entry)
        SCORES_PATH.write_text(json.dumps(scores, indent=2), encoding="utf-8")

    # =========================
    #         DATA
    # =========================
    questions = load_questions()

    # ECCB Member States
    eccb_countries = [
        "Anguilla", "Antigua and Barbuda", "Dominica", "Grenada",
        "Montserrat", "St. Kitts and Nevis", "St. Lucia",
        "St. Vincent and the Grenadines", "Other"
    ]

    # Avatar catalog (emoji groups)
    AVATAR_CATALOG = {
        "Island Vibes": ["🌴", "🏝️", "🌊", "🍍", "⚓️"],
        "Sea Life": ["🐠", "🐢", "🦈", "🦞", "🐬"],
        "Birds": ["🦜", "🦩", "🦉"],
        "Fun": ["🎵", "🎯", "🎮", "🎓", "💡"],
    }

    # Difficulty (category) map
    difficulty_map = {
        "Easy Peasy (5)": 5,
        "Warm-up (10)": 10,
        "Steady Climb (20)": 20,
        "Marathon (30)": 30,
        "Pro League (40)": 40,
        "Hardcore Expert (50)": 50
    }

    # =========================
    #     AVATAR PICKER UI
    # =========================
    def avatar_picker():
        if "picked_avatar" not in st.session_state:
            st.session_state.picked_avatar = None

        st.subheader("Choose your avatar")
        tabs = st.tabs(["🧩 Emoji avatars", "✨ Special emoji", "🖼️ Upload image"])

        with tabs[0]:
            colA, colB = st.columns([1, 2])
            with colA:
                category = st.selectbox("Category", list(AVATAR_CATALOG.keys()), key="av_cat")
            emojis = AVATAR_CATALOG[category]
            choice = st.radio("Pick one", emojis, horizontal=True, key="av_choice")
            with colB:
                st.markdown(f"<div style='font-size:72px; line-height:1; text-align:center;'>{choice}</div>",
                            unsafe_allow_html=True)
            st.session_state.picked_avatar = {"kind": "emoji", "emoji": choice, "image_bytes": None}

        with tabs[1]:
            custom_emoji = st.text_input("Type any emoji (e.g., 🐳, 😎, 🚀)", key="av_custom")
            if custom_emoji.strip():
                st.markdown(f"<div style='font-size:72px; line-height:1; text-align:center;'>{custom_emoji}</div>",
                            unsafe_allow_html=True)
                st.session_state.picked_avatar = {"kind": "emoji", "emoji": custom_emoji.strip(), "image_bytes": None}

        with tabs[2]:
            img = st.file_uploader("Upload a square PNG/JPG (suggested ~256×256)", type=["png", "jpg", "jpeg"], key="av_upload")
            if img is not None:
                img_bytes = img.read()
                st.image(img_bytes, width=120)
                st.session_state.picked_avatar = {"kind": "image", "emoji": None, "image_bytes": img_bytes}

        return st.session_state.picked_avatar

    # =========================
    #     STYLISH PODIUM
    # =========================
    def render_podium(category_scores):
        top3 = category_scores[:3]
        while len(top3) < 3:
            top3.append(None)

        slots = {
            "second": top3[1] if len(top3) > 1 else None,
            "first":  top3[0] if len(top3) > 0 else None,
            "third":  top3[2] if len(top3) > 2 else None,
        }

        card_css = """
            <style>
            .podium-card {
                width: 100%; max-width: 320px; margin: 0 auto; position: relative;
                background: radial-gradient(140% 120% at 50% 0%, #ffffff 20%, #f7fbff 100%);
                border-radius: 16px; padding: 18px 12px 14px; text-align: center;
                box-shadow: 0 14px 26px rgba(13,110,253,0.06);
                border: 2px solid transparent; background-clip: padding-box;
            }
            .podium-card::before {
                content: ""; position: absolute; inset: -2px; border-radius: 18px; z-index: -1;
                background: linear-gradient(120deg, #7ab8ff, #ffd26a, #e7b6ff, #7ab8ff);
                background-size: 300% 300%; animation: borderflow 6s ease infinite;
            }
            @keyframes borderflow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
            .medal { font-size: 46px; line-height: 1; }
            .crown { font-size: 24px; position: absolute; top: -12px; left: 50%;
                     transform: translateX(-50%) rotate(-10deg);
                     filter: drop-shadow(0 2px 2px rgba(0,0,0,0.15)); }
            .avatar-emoji { font-size: 44px; line-height: 1.1; margin: 6px 0 2px; }
            .name { font-weight: 800; font-size: 18px; color: #1d2a44; margin-top: 4px; letter-spacing: .2px; }
            .country { color: #5a6782; font-size: 13px; margin-top: 2px; }
            .scorepill {
                display: inline-block; margin-top: 10px; padding: 6px 12px; font-weight: 900;
                background: #eef6ff; color: #0d6efd; border-radius: 999px; border: 1px solid #dbeaff;
                box-shadow: inset 0 0 0 2px rgba(255,255,255,0.7);
            }
            .pedestal { height: 10px; margin-top: 10px; border-radius: 10px 10px 0 0;
                        background: linear-gradient(180deg,#dfeaff,#b9d3ff);
                        box-shadow: inset 0 -6px 12px rgba(13,110,253,.12);
                        border: 1px solid #cfe0ff; max-width: 320px; margin-left: auto; margin-right: auto; }
            .floaty { animation: floaty 1.8s ease-in-out infinite alternate; }
            @keyframes floaty { from { transform: translateY(-2%);} to { transform: translateY(0%);} }
            </style>
        """
        st.markdown(card_css, unsafe_allow_html=True)

        cL, c2, c1, c3, cR = st.columns([1, 3, 4, 3, 1])

        def render_slot(col, slot_name, data, y_offset_px, pedestal_h):
            with col:
                if data is None:
                    st.markdown(
                        f"""
                        <div style="margin-top:{y_offset_px}px;">
                        <div class="podium-card">
                            <div class="medal">—</div>
                            <div class="avatar-emoji">🧠</div>
                            <div class="name">Waiting...</div>
                            <div class="country">&nbsp;</div>
                            <div class="scorepill">0 / 0</div>
                        </div>
                        <div class="pedestal" style="height:{pedestal_h}px;"></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    return

                medal = "🥇" if slot_name == "first" else "🥈" if slot_name == "second" else "🥉"
                crown = "👑" if slot_name == "first" else ""
                avatar = data.get("avatar", "🧠")
                name = data.get("username", "Player")
                country = data.get("country", "—")
                sc = data.get("score", 0)
                tot = data.get("total", 0)
                floaty = " floaty" if slot_name == "first" else ""

                st.markdown(
                    f"""
                    <div style="margin-top:{y_offset_px}px;">
                    <div class="podium-card{floaty}">
                        <div class="crown">{crown}</div>
                        <div class="medal">{medal}</div>
                        <div class="avatar-emoji">{avatar}</div>
                        <div class="name">{name}</div>
                        <div class="country">{country}</div>
                        <div class="scorepill">{sc} / {tot}</div>
                    </div>
                    <div class="pedestal" style="height:{pedestal_h}px;"></div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        render_slot(c2, "second", slots["second"], y_offset_px=30, pedestal_h=38)
        render_slot(c1, "first",  slots["first"],  y_offset_px=0,  pedestal_h=56)
        render_slot(c3, "third",  slots["third"],  y_offset_px=40, pedestal_h=30)
        st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

    # =========================
    #     SESSION STATE INIT
    # =========================
    ss = st.session_state
    ss.setdefault("setup_done", False)
    ss.setdefault("question_index", 0)
    ss.setdefault("selected_option", None)
    ss.setdefault("quiz_questions", [])
    ss.setdefault("last_run_time", None)
    ss.setdefault("score", 0)
    ss.setdefault("scored_flags", {})  # {q_index: bool}
    ss.setdefault("category", None)     # difficulty label
    ss.setdefault("score_saved", False) # prevent double save

    # =========================
    #       PRE-QUIZ SETUP
    # =========================
    if not ss.setup_done:
        st.title("🧠 Financial Education Quiz - Setup")
        st.markdown("Welcome! Please enter your details before starting the quiz.")

        username = st.text_input("Enter your username:")
        country = st.selectbox("Select your country:", eccb_countries)
        picked = avatar_picker()

        difficulty_choice = st.selectbox("Select difficulty:", list(difficulty_map.keys()))
        requested_num = difficulty_map[difficulty_choice]

        max_available = len(questions)
        if max_available == 0:
            st.stop()
        num_questions = min(requested_num, max_available)
        if num_questions < requested_num:
            st.warning(f"Only {max_available} questions available. Using {num_questions}.")

        if st.button("🚀 Start Quiz"):
            if username.strip() == "":
                st.warning("Please enter a username before starting.")
            elif picked is None:
                st.warning("Please choose an avatar before starting.")
            else:
                ss.username = username.strip()
                ss.country = country
                ss.avatar_kind = picked["kind"]
                ss.avatar_emoji = picked["emoji"]
                ss.avatar_image_bytes = picked["image_bytes"]
                ss.category = difficulty_choice
                ss.setup_done = True

                ss.quiz_questions = random.sample(questions, num_questions)
                ss.question_index = 0
                ss.last_run_time = time.time()
                ss.selected_option = None
                ss.score = 0
                ss.scored_flags = {}
                ss.score_saved = False

                st.rerun()
        st.stop()

    # =========================
    #       QUIZ LOGIC
    # =========================
    # End-of-quiz guard
    if ss.question_index >= len(ss.quiz_questions):
        if not ss.score_saved:
            save_score({
                "username": ss.username,
                "country": ss.country,
                "avatar": ss.avatar_emoji if ss.get("avatar_kind") == "emoji" else "🧠",
                "category": ss.category,
                "score": ss.score,
                "total": len(ss.quiz_questions)
            })
            ss.score_saved = True

        st.balloons()
        st.markdown(f"## 🎉 Quiz Complete, {ss.username} from {ss.country}!")
        st.markdown(f"### 🏆 Your Score: **{ss.score} / {len(ss.quiz_questions)}**")
        st.progress(ss.score / max(1, len(ss.quiz_questions)))

        with st.spinner("Crunching the results..."):
            time.sleep(1.0)

        st.subheader(f"🏅 Leaderboard — {ss.category}")
        scores = load_scores()
        category_scores = [s for s in scores if s.get("category") == ss.category]
        category_scores.sort(
            key=lambda x: (
                x.get("score", 0) / max(1, x.get("total", 1)),
                x.get("score", 0),
                x.get("total", 0),
                x.get("username", "")
            ),
            reverse=True
        )

        placement = None
        for idx, s in enumerate(category_scores):
            if (
                s.get("username") == ss.username
                and s.get("country") == ss.country
                and s.get("score") == ss.score
                and s.get("total") == len(ss.quiz_questions)
                and s.get("category") == ss.category
            ):
                placement = idx + 1
                break

        if placement == 1:
            st.toast("🥇 You placed 1st — Champion!", icon="🎉")
        elif placement == 2:
            st.toast("🥈 You placed 2nd — Excellent!", icon="💪")
        elif placement == 3:
            st.toast("🥉 You placed 3rd — Great job!", icon="⭐")
        else:
            st.toast(f"You placed #{placement or '—'} — keep climbing!", icon="👍")

        render_podium(category_scores)

        if placement:
            place_emoji = "🏆" if placement == 1 else "🥈" if placement == 2 else "🥉" if placement == 3 else "🎯"
            st.success(f"{place_emoji} **Your placement:** #{placement} in **{ss.category}**")

        st.markdown("### Top 10")
        st.markdown("""
            <style>
            .lb-row { display: grid; grid-template-columns: 48px 1fr 140px 120px; gap: 8px;
                      align-items: center; padding: 10px 12px; border-bottom: 1px solid #eef1f6; }
            .lb-row:nth-child(odd) { background: #fafcff; }
            .lb-rank { font-weight: 800; text-align: center; padding: 8px; border-radius: 10px; background: #f2f6ff; color: #224; }
            .lb-name { font-weight: 700; }
            .lb-country { color: #556; font-size: 13px; }
            .lb-score { text-align: right; font-weight: 800; color: #0d6efd; }
            .lb-pct { text-align: right; color: #445; }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class='lb-row' style='font-size:13px; font-weight:800; color:#334; background:#f6f9ff; border-top: 1px solid #e8eef8;'>
                <div>#</div>
                <div>Player</div>
                <div style='text-align:right;'>Score</div>
                <div style='text-align:right;'>Accuracy</div>
            </div>
        """, unsafe_allow_html=True)

        top10 = category_scores[:10]
        for i, s in enumerate(top10, start=1):
            pct = 0
            if s.get("total", 0) > 0:
                pct = int(round(100 * s["score"] / s["total"]))
            avatar = s.get("avatar", "🧠")
            st.markdown(f"""
                <div class='lb-row'>
                    <div class='lb-rank'>{i}</div>
                    <div>
                        <div class='lb-name'>{avatar} {s.get('username','Player')}</div>
                        <div class='lb-country'>{s.get('country','—')}</div>
                    </div>
                    <div class='lb-score'>{s.get('score',0)} / {s.get('total',0)}</div>
                    <div class='lb-pct'>{pct}%</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            .play-again-btn > button {
                background: linear-gradient(90deg, #ff7b00, #ff006a); color: white !important;
                font-size: 18px; font-weight: bold; border-radius: 12px; border: none;
                padding: 0.6em 1.2em; box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                transition: all 0.3s ease;
            }
            .play-again-btn > button:hover {
                transform: scale(1.05); box-shadow: 0 6px 18px rgba(0,0,0,0.25);
                background: linear-gradient(90deg, #ff006a, #ff7b00);
            }
            </style>
        """, unsafe_allow_html=True)

        if st.container():
            play_again = st.container()
            with play_again:
                if st.button("🔄 Play Again", key="play_again", help="Restart the quiz", type="primary"):
                    ss.setup_done = False
                    ss.question_index = 0
                    ss.selected_option = None
                    ss.quiz_questions = []
                    ss.last_run_time = None
                    ss.score = 0
                    ss.scored_flags = {}
                    ss.category = None
                    ss.score_saved = False
                    ss.username = ""
                    ss.country = ""
                    ss.avatar_kind = None
                    ss.avatar_emoji = None
                    ss.avatar_image_bytes = None
                    st.rerun()

        st.stop()

    # Current question
    q = ss.quiz_questions[ss.question_index]

    # --- Styles ---
    st.markdown("""
        <style>
            .big-question { font-size: 28px; font-weight: bold; color: #007bff; }
            .headerbar { font-size: 16px; padding: 8px 12px; background: #f7fbff; border: 1px solid #e3f2ff; border-radius: 10px; margin-bottom: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<div class='headerbar'>", unsafe_allow_html=True)
    col_avatar, col_meta = st.columns([1, 6])
    with col_avatar:
        if ss.get("avatar_kind") == "image" and ss.get("avatar_image_bytes"):
            st.image(ss.avatar_image_bytes, width=42)
        else:
            emoji = ss.get("avatar_emoji", "🧠")
            st.markdown(f"<div style='font-size:38px; line-height:1;'>{emoji}</div>", unsafe_allow_html=True)
    with col_meta:
        st.markdown(
            f"<b>{ss.username}</b> — {ss.country}<br>"
            f"Question {ss.question_index + 1} of {len(ss.quiz_questions)} | "
            f"Score: <b>{ss.score}</b> | Mode: <b>{ss.category}</b>",
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    # Placeholders
    question_placeholder = st.empty()
    options_placeholder = st.empty()
    answer_placeholder = st.empty()
    progress_placeholder = st.empty()
    info_placeholder = st.empty()

    elapsed = time.time() - ss.last_run_time

    # === PHASE 1: Question & Buttons (0–ANSWER_TIME) ===
    if elapsed < ANSWER_TIME:
        question_placeholder.markdown(f"<div class='big-question'>🧠 {q['question']}</div>", unsafe_allow_html=True)
        info_placeholder.info(f"⏳ Choose an option or wait. Showing answer in {ANSWER_TIME} seconds...")
        progress_placeholder.progress(min(elapsed / ANSWER_TIME, 1.0))

        with options_placeholder.container():
            cols = st.columns(2)
            for i, option in enumerate(q["options"]):
                if cols[i % 2].button(option, key=f"opt_{ss.question_index}_{i}"):
                    ss.selected_option = option
                    # jump straight to reveal phase
                    ss.last_run_time = time.time() - ANSWER_TIME - 0.01
                    st.rerun()

        time.sleep(0.12)
        st.rerun()

    # === PHASE 2: Reveal Answers (ANSWER_TIME–TOTAL_TIME) ===
    elif elapsed < TOTAL_TIME:
        question_placeholder.markdown(f"<div class='big-question'>🧠 {q['question']}</div>", unsafe_allow_html=True)
        options_placeholder.empty()  # hide buttons during reveal

        qkey = ss.question_index
        if not ss.scored_flags.get(qkey, False):
            if ss.selected_option == q["answer"]:
                ss.score += 1
            ss.scored_flags[qkey] = True

        with answer_placeholder.container():
            for option in q["options"]:
                if option == q["answer"]:
                    label = f"✅ {option}"
                    if ss.selected_option == option:
                        label += " — Your choice"
                    st.success(label)
                else:
                    label = f"❌ {option}"
                    if ss.selected_option == option:
                        label += " — Your choice"
                    st.error(label)

        progress_placeholder.progress(min((elapsed - ANSWER_TIME) / REVEAL_TIME, 1.0))
        info_placeholder.info(f"➡️ Next question in {REVEAL_TIME} seconds...")

        time.sleep(0.12)
        st.rerun()

    # === PHASE 3: Advance (>= TOTAL_TIME) ===
    else:
        question_placeholder.empty()
        options_placeholder.empty()
        answer_placeholder.empty()
        progress_placeholder.empty()
        info_placeholder.empty()

        ss.question_index += 1
        ss.last_run_time = time.time()
        ss.selected_option = None

        st.rerun()

