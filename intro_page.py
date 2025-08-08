import streamlit as st
from pathlib import Path



def run_into():
    
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #007bff 0%, #00c2ff 100%); padding: 2rem; border-radius: 15px; color: white;'>
            <h1 style='font-size: 2.5rem;'>💡 Smart Finances Caribbean</h1>
            <p style='font-size: 1.1rem;'>
                Welcome to our financial education platform built for Caribbean citizens and youth.
                This tool empowers you with the knowledge to save, spend, and invest wisely in your future.
                Explore our tools to convert currency, generate budgets, learn about scams, and start smart side hustles.
            </p>
            <ul style='font-size: 1.05rem;'>
                <li>🌍 Tailored for ECCU countries</li>
                <li>📈 Boosts money skills in young adults</li>
                <li>📱 Mobile-friendly & easy to use</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True
    )





    st.markdown("""
    ---
    ### 🎯 Our Mission

    To equip every Caribbean citizen — young or old — with the knowledge and confidence to make smart, sustainable financial decisions that support personal and community growth.

    ### 🌱 Our Core Values

    - 🧠 **Education** — Make financial knowledge accessible  
    - 🤝 **Empowerment** — Enable people to control their money  
    - 🌍 **Community** — Tailored advice for each Caribbean territory  

    ---
    ### 🚀 How to Get Started

    1. **Explore Tools**  
    Use our tools like the budget planner, currency converter, and hustle ideas.

    2. **Test Your Skills**  
    Take our interactive quiz to see how financially fit you are.

    3. **Apply What You Learn**  
    Make real-life decisions with more confidence and awareness.

    ---
    ### 📍 We're Proudly Serving All ECCU Territories:
    <div style="line-height: 2; font-size: 16px;">

    <img src="https://flagcdn.com/w40/ai.png" height="20" style="vertical-align: middle;"> Anguilla<br>
    <img src="https://flagcdn.com/w40/ag.png" height="20" style="vertical-align: middle;"> Antigua & Barbuda<br>
    <img src="https://flagcdn.com/w40/dm.png" height="20" style="vertical-align: middle;"> Dominica<br>
    <img src="https://flagcdn.com/w40/gd.png" height="20" style="vertical-align: middle;"> Grenada<br>
    <img src="https://flagcdn.com/w40/ms.png" height="20" style="vertical-align: middle;"> Montserrat<br>
    <img src="https://flagcdn.com/w40/kn.png" height="20" style="vertical-align: middle;"> St. Kitts & Nevis<br>
    <img src="https://flagcdn.com/w40/lc.png" height="20" style="vertical-align: middle;"> St. Lucia<br>
    <img src="https://flagcdn.com/w40/vc.png" height="20" style="vertical-align: middle;"> St. Vincent & the Grenadines<br>

    </div>

    ---
    ### 💬 What Caribbean Youth Are Saying

    > “I had no idea how much I was overspending until I used the budget tool — game changer!”  
    > — *Daniela, Dominica*  

    > “The scam alerts opened my eyes. I almost fell for one last year!”  
    > — *Jelani, St. Vincent*  

    > “This app makes financial learning fun — finally something made for us!”  
    > — *Shanique, St. Kitts*  

    ---
    ### 📸 Caribbean Highlights
    """, unsafe_allow_html=True)


    # ---- Resolve images dir safely ----
    try:
        BASE_DIR = Path(__file__).parent
    except NameError:
        BASE_DIR = Path.cwd()

    IMAGES_DIR = (BASE_DIR / "images") if (BASE_DIR / "images").exists() else (Path.cwd() / "images")

    # Your images & captions (added St. Vincent and the Grenadines)
    files = [
        "image2.png", "image7.png",
        "image3.png", "image6.png",
        "image4.png", "image5.png",
        "image8.png"  # ✅ New image
    ]
    captions = [
        "Dominica",
        "Montserrat",
        "Grenada",
        "Antigua",
        "St. Kitts and Nevis",
        "St. Lucia",
        "St. Vincent and the Grenadines"  # ✅ New caption
    ]

    # ---- Styling (card + hover) ----
    st.markdown("""
    <style>
    .gallery-card {
    background: #fff;
    border-radius: 12px;
    padding: 10px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    transition: transform .15s ease, box-shadow .15s ease;
    }
    .gallery-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(0,0,0,0.09);
    }
    .gallery-caption {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-top: 6px;
    text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---- Display images in 3 columns ----
    cols = st.columns(3)
    for idx, fname in enumerate(files):
        path = IMAGES_DIR / fname
        with cols[idx % 3]:
            if path.exists():
                with st.container():
                    st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
                    st.image(str(path), use_container_width=True)
                    st.markdown(f'<div class="gallery-caption">{captions[idx]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning(f"Image not found: `{path}`")








    st.markdown("""
    ---
    ### Ready to Start Your Financial Journey?

    👉 Head to the **Currency Converter**, **Budget Planner**, or **Quiz** to begin!  
    Or just explore the menu on the left to find what suits your goals best.
    """, unsafe_allow_html=True)
