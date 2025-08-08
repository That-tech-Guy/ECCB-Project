import streamlit as st
import random
from finance_quiz import start_quiz
from currency_converter import converter
from budget_gen import gen_budget
from save_invest import invest


side_hustles = [
    {
        "title": "Online Tutoring\n",
        "description": "Teaching students remotely in subjects you excel at via video and digital tools.\n",
        "requirements": "Subject-matter expertise, reliable computer & internet, video conferencing tools, lesson planning, certification optional.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Graphic Design\n",
        "description": "Creating visual content such as logos, flyers, and social media assets for clients.\n",
        "requirements": "Strong design skills, mastery of tools like Adobe Creative Suite or Figma, professional portfolio, basic branding knowledge.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Dog Walking\n",
        "description": "Providing exercise and care for pets in your local area.\n",
        "requirements": "Physical fitness, empathy with animals, scheduling tools, local advertising.\n", 
        "remote": False, 
        "low_cost": True
    },
    {
        "title": "Print-on-Demand Store\n",
        "description": "Selling custom-designed products (like T-shirts or mugs) without holding inventory.\n",
        "requirements": "Design skills, e-commerce setup, finding a reliable print-on-demand service, marketing strategy.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Affiliate Marketing\n",
        "description": "Promoting products online and earning a commission for each sale made through your links.\n",
        "requirements": "Content creation ability, SEO or social media skills, website or channel, knowledge of affiliate platforms.\n", 
        "remote": False, 
        "low_cost": False
    },
    {
        "title": "Dropshipping\n",
        "description": "Selling products online where the supplier ships items directly to the customer.\n",
        "requirements": "Product research, e-commerce setup, supplier reliability, marketing, brand building.\n", 
        "remote": True, 
        "low_cost": False
    },
    {
        "title": "Build Websites\n",
        "description": "Developing websites for businesses or individuals using coding or CMS tools.\n",
        "requirements": "HTML/CSS/JS or WordPress knowledge, hosting/domain setup, portfolio or client pitch skills.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Email Marketing\n",
        "description": "Crafting and sending newsletters and campaigns to engage subscribers.\n",
        "requirements": "Copywriting skills, familiarity with platforms like MailChimp, subscriber acquisition, analytics.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Virtual Assistant\n",
        "description": "Supporting business operations remotely through tasks like email management and scheduling.\n",
        "requirements": "Organization, communication, familiarity with admin tools (e.g., Google Workspace, Trello).\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "Transcription\n",
        "description": "Converting audio into written text accurately and efficiently.\n",
        "requirements": "Fast typing (≈60 WPM), good listening skills, quality headphones, transcription software.\n", 
        "remote": False, 
        "low_cost": True
    },
    {
        "title": "Freelance Writing\n",
        "description": "Creating articles, copy, or content for clients across industries.\n",
        "requirements": "Strong writing/editing, SEO basics, portfolio or sample writing, familiarity with freelance platforms.\n", 
        "remote": False, 
        "low_cost": False
    },
    {
        "title": "Online Surveys\n",
        "description": "Filling out surveys and small tasks for reward platforms.\n",
        "requirements": "Access to reputable platforms, patience for micro-tasks, consistent effort.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "User Testing\n",
        "description": "Evaluating websites/apps by providing usability feedback.\n",
        "requirements": "Ability to articulate experience, stable internet, willingness to test diverse platforms.\n", 
        "remote": True, 
        "low_cost": False
    },
    {
        "title": "Social Media Management\n",
        "description": "Managing clients’ social profiles, creating content and planning engagement.\n",
        "requirements": "Understanding of social platforms, content creation tools, scheduling software, client communication.\n", 
        "remote": True, 
        "low_cost": True
    },
    {
        "title": "SEO Consulting\n",
        "description": "Advising businesses on how to optimize content for search engines.\n",
        "requirements": "Knowledge of SEO, analytics tools experience, keyword research capability, result-oriented mindset.\n", 
        "remote": False, 
        "low_cost": False
    }
]


def get_random_side_hustle(remote_only=False, low_cost_only=False):
    filtered = [
        hustle for hustle in side_hustles
        if (not remote_only or hustle["remote"]) and (not low_cost_only or hustle["low_cost"])
    ]
    
    if not filtered:
        return "🚫 No side hustles found with those filters!"
    
    hustle = random.choice(filtered)
    
    return (
        f"💼 Side Hustle: {hustle['title']}\n"
        f"📝 Description: {hustle.get('description', 'No description provided.')}\n"
        f"📋 Requirements: {hustle.get('requirements', 'No requirements listed.')}"
    )


industries = [
    "Health & Wellness", "Food & Beverage", "Education", "Technology",
    "Arts & Crafts", "E-commerce", "Pet Services", "Fitness", "Sustainability"
]


business_models = [
    "subscription service", "mobile app", "online store", "freelance service",
    "pop-up shop", "consulting agency", "local delivery", "coaching business",
    "custom product line"
]


target_audiences = [
    "busy professionals", "stay-at-home parents", "college students",
    "small business owners", "remote workers", "eco-conscious consumers",
    "pet owners", "artists and creatives", "seniors"
]


def generate_business_idea():
    industry = random.choice(industries)
    model = random.choice(business_models)
    audience = random.choice(target_audiences)
    return f"💡 A {industry.lower()} {model} for {audience}."



def commonscams2(show_one=True):
    """
    Returns one or all common scams found in the Caribbean.

    Args:
        show_one (bool): If True, return one random scam. If False, return all scams.

    Returns:
        dict or list: A single scam (dict) or a list of scams (list of dicts)
    """
    common_scams = [
        {"title": "Taxi Overcharging & Fake Taxis", "description": "Drivers quote inflated prices, refuse to use meters, or aren't licensed at all."},
        {"title": "Fake Tour Operators & Excursion Scams", "description": "Scammers pose as guides or sell tours that never happen."},
        {"title": "Street Hustler / Friendly Local Scam", "description": "A 'friendly' offers help or a tour, then demands money or tips."},
        {"title": "Credit Card Skimming", "description": "ATM or card readers are rigged to steal your data."},
        {"title": "Pickpocketing & Distraction Thefts", "description": "Someone distracts you, another steals your belongings."},
        {"title": "Timeshare/Vacation Club Scams", "description": "You're lured with free gifts but pressured into shady, expensive deals."},
        {"title": "Romance Scams (Online or In-Person)", "description": "Fake relationships built to extract money from victims."},
        {"title": "Fake Goods (Cigars, Jewelry, Designer Items)", "description": "Vendors sell counterfeits as authentic, especially Cuban cigars or gold jewelry."},
        {"title": "Rental Damage Scams (Jet Skis, Cars, Scooters)", "description": "You’re blamed for damage that already existed and charged unfairly."},
        {"title": "Lottery, Inheritance & Advance Fee Scams", "description": "You’re told you won something, but must pay to claim it."}
    ]

    if show_one:
        return random.choice(common_scams)
    else:
        return common_scams



# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart Finances Caribbean",
    page_icon="💰"
)


# --- SIDEBAR MENU ---
st.sidebar.image("images/eccb.png", width=100)
st.sidebar.title("Menu")
menu = st.sidebar.radio("Navigate", [
    "🏝️ Intro",
    "💱 Currency Converter",
    "🌍 Caribbean Saving & Investing",
    "📊 Budget Plan Generator",
    "🚨 Common Scams",
    "🧵 Small Hustles",
    "🧠 Financial Literacy Quiz",
    "📚 Resources"
], key="menu")

# --- STYLING ---
st.markdown("""
    <style>
        .main { background-color: #f0f8ff; }
        h1, h2 { color: #007bff; }
        .section { padding: 20px; background-color: white; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)


# --- PAGE CONTENT ---
if menu == "🏝️ Intro":

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


    st.image("images/image1.png", caption="Finance in the Caribbean",  width=200)


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


    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://images.unsplash.com/photo-1579202673506-ca3ce28943ef", caption="Saving Smart")
    with col2:
        st.image("https://images.unsplash.com/photo-1556740738-b6a63e27c4df", caption="Budgeting on the Go")
    with col3:
        st.image("https://images.unsplash.com/photo-1580910051071-3c3f1a7f9d0e", caption="Side Hustles in Action")

    st.markdown("""
    ---
    ### Ready to Start Your Financial Journey?

    👉 Head to the **Currency Converter**, **Budget Planner**, or **Quiz** to begin!  
    Or just explore the menu on the left to find what suits your goals best.
    """, unsafe_allow_html=True)


elif menu == "💱 Currency Converter":
    converter()


elif menu == "📊 Budget Plan Generator":
    gen_budget()


elif menu == "🌍 Caribbean Saving & Investing":
    invest()


elif menu == "🧵 Small Hustles":
    st.header("🧵 Smart Hustle Suggestions")
    st.markdown("Explore random side hustles or generate small business ideas tailored to your situation.")

    st.subheader("💼 Find a Random Side Hustle")

    col1, col2 = st.columns(2)
    with col1:
        remote_only = st.checkbox("💻 Remote Only", value=True)
    with col2:
        low_cost_only = st.checkbox("💸 Low Startup Cost", value=True)

    if st.button("🎲 Suggest a Side Hustle"):
        suggestion = get_random_side_hustle(remote_only=remote_only, low_cost_only=low_cost_only)
        st.success(suggestion.replace("\n", "\n"))



    st.markdown("---")

    st.subheader("🚀 Generate a Business Idea")
    if st.button("🎯 Give Me a Business Idea"):
        idea = generate_business_idea()
        st.info(idea)

    st.markdown("---")
    st.markdown("""
        👇 Use these ideas to:
        - Start a weekend hustle
        - Launch an online business
        - Earn extra income while in school
    """)


elif menu == "🧠 Financial Literacy Quiz":
   start_quiz()


elif menu == "🚨 Common Scams":
    st.header("🚨 Common Scams in the Caribbean")
    st.markdown("Be alert when traveling or living in the Caribbean. Here are some common scams to watch out for:")

    show_random = st.toggle("🎲 Show One Random Scam", value=True)

    scams = commonscams2(show_one=show_random)
    
    if show_random:
        st.subheader(f"🧠 {scams['title']}")
        st.write(scams["description"])
    else:
        for scam in scams:
            with st.expander(f"🧠 {scam['title']}"):
                st.write(scam["description"])

    st.markdown("""
    ---
    ✅ **Tips to Stay Safe:**
    - Avoid sharing personal or financial info with strangers
    - Use official taxi stands and verified booking apps
    - Be cautious of offers that seem too good to be true
    - Watch your belongings in crowded areas
    """)


elif menu == "📚 Resources":
    st.header("📚 Regional Financial Education Resources")
    st.markdown("""
    - [Eastern Caribbean Central Bank (ECCB)](https://www.eccb-centralbank.org)
    - [Bank of Jamaica (BOJ)](https://www.boj.org.jm)
    - [Central Bank of Trinidad & Tobago](https://www.central-bank.org.tt)
    - [ECCU Financial Empowerment](https://www.eccb-centralbank.org/FinancialLiteracy)
    """)

    st.info("Feel free to submit your own financial learning resources for your territory!")

# --- OPTIONAL FOOTER ---
# --- OPTIONAL FOOTER ---
st.markdown("""
---
<center>Made by "664RugRats" for the 2025 ECCB Challenge 💡</center>
""", unsafe_allow_html=True)
