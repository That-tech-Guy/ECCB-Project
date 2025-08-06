import streamlit as st
import requests
import random
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64



# --- SIDE HUSTLE DATA ---
side_hustles = [
    {"title": "Online Tutoring", "remote": True, "low_cost": True},
    {"title": "Graphic Design", "remote": True, "low_cost": True},
    {"title": "Dog Walking", "remote": False, "low_cost": True},
    {"title": "Print-on-Demand Store", "remote": True, "low_cost": True},
    {"title": "Tutoring (Online or Local)", "remote": True, "low_cost": True},
    {"title": "Delivery Driver", "remote": False, "low_cost": False},
    {"title": "Handyman Services", "remote": False, "low_cost": False},
    {"title": "Affiliate Marketing", "remote": True, "low_cost": True},
    {"title": "Selling Digital Products", "remote": True, "low_cost": True},
    {"title": "Personal Assistant", "remote": False, "low_cost": False},
]

def get_random_side_hustle(remote_only=False, low_cost_only=False):
    filtered = [
        hustle for hustle in side_hustles
        if (not remote_only or hustle["remote"]) and (not low_cost_only or hustle["low_cost"])
    ]
    if not filtered:
        return "🚫 No side hustles found with those filters!"
    return f"💼 {random.choice(filtered)['title']}"

# --- BUSINESS IDEA GENERATOR ---
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

def currencyconverter(base: str, target: str, amount: float) -> str:
    API_KEY = "759cc97900658c57b71d7b1d"  # Your API key here
    BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"

    CARIBBEAN_CURRENCIES = ["XCD", "JMD", "TTD", "BBD", "BSD", "HTG", "CUP", "DOP"]
    SUPPORTED = CARIBBEAN_CURRENCIES + ["USD"]

    base = base.upper()
    target = target.upper()

    if base not in SUPPORTED:
        return f"❌ Base currency '{base}' is not supported. Use Caribbean currencies or USD."
    if target not in SUPPORTED:
        return f"❌ Target currency '{target}' is not supported. Use Caribbean currencies or USD."

    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        rates = response.json().get("conversion_rates", {})
    except Exception as e:
        return f"❌ Failed to fetch currency rates: {str(e)}"

    if base != "USD" and base not in rates:
        return f"❌ Base currency '{base}' not found in conversion rates."
    if target != "USD" and target not in rates:
        return f"❌ Target currency '{target}' not found in conversion rates."

    if base == "USD":
        converted = amount * rates.get(target, 0)
    elif target == "USD":
        converted = amount / rates.get(base, 1)
    else:
        usd_amount = amount / rates.get(base, 1)
        converted = usd_amount * rates.get(target, 0)

    return f"{amount:.2f} {base} = {converted:.2f} {target}"


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Smart Finances Caribbean",
    page_icon="💰",
    layout="wide",
)

# --- SIDEBAR MENU ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/ECCB_Logo.png/240px-ECCB_Logo.png", width=150)
st.sidebar.title("ECCB Project Menu")
menu = st.sidebar.radio("Navigate", [
    "🏝️ Intro",
    "💱 Currency Converter",
    "🌍 Caribbean Saving & Investing",
    "📊 Budget Plan Generator",
    "🚨 Common Scams",
    "🧵 Small Hustles",
    "🧠 Financial Literacy Quiz",
    "📚 Resources"
])

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
    st.markdown("""
        <div style='background: linear-gradient(135deg, #007bff 0%, #00c2ff 100%); padding: 3rem; border-radius: 15px; color: white;'>
            <div style='display: flex; flex-wrap: wrap; align-items: center; justify-content: center;'>
                <div style='flex: 1; min-width: 300px; padding: 10px;'>
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
                <div style='flex: 1; min-width: 300px; text-align: center; padding: 10px;'>
                    <img src='https://images.unsplash.com/photo-1605902711622-cfb43c44367b' style='max-width: 100%; border-radius: 12px;' alt='Finance in Caribbean'>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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

    - 🇦🇮 Anguilla  
    - 🇦🇬 Antigua & Barbuda  
    - 🇩🇲 Dominica  
    - 🇬🇩 Grenada  
    - 🇲🇸 Montserrat  
    - 🇰🇳 St. Kitts & Nevis  
    - 🇱🇨 St. Lucia  
    - 🇻🇨 St. Vincent & the Grenadines  
    
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
    st.header("💱 Currency Converter")
    st.markdown("Convert between **Caribbean currencies and USD** using up-to-date exchange rates.")

    currencies = ["XCD", "JMD", "TTD", "BBD", "BSD", "HTG", "CUP", "DOP", "USD"]

    col1, col2 = st.columns(2)
    with col1:
        base_currency = st.selectbox("From Currency", currencies, index=0)
    with col2:
        target_currency = st.selectbox("To Currency", currencies, index=8)

    amount = st.number_input("Enter amount to convert", min_value=0.0, format="%.2f")

    if st.button("Convert"):
        result = currencyconverter(base_currency, target_currency, amount)
        st.success(result)


elif menu == "📊 Budget Plan Generator":
    st.header("📊 Budget Plan Generator")
    st.markdown("""
        Input your **monthly income** and list your expenses by category.  
        We'll show you your net income, savings strategy, and a budget breakdown chart.
    """)

    monthly_income = st.number_input("💰 Enter your total monthly income (USD)", min_value=0.0, step=50.0)

    st.markdown("### 🧾 Add Your Expenses")
    expense_data = []
    expense_container = st.container()

    with expense_container:
        num_expenses = st.number_input("How many expense categories do you want to enter?", min_value=1, max_value=15, step=1, value=3)

        for i in range(int(num_expenses)):
            col1, col2 = st.columns([2, 1])
            with col1:
                category = st.text_input(f"Category {i + 1}", key=f"cat_{i}")
            with col2:
                amount = st.number_input(f"Amount for {category or f'Item {i + 1}'}", min_value=0.0, key=f"amt_{i}")

            if category:
                expense_data.append({"Category": category, "Amount": amount})

    if st.button("📈 Generate Budget Report"):
        if monthly_income == 0 or not expense_data:
            st.warning("Please provide both income and valid expense entries.")
        else:
            result = budgeting_function(monthly_income, expense_data)

            st.subheader("💡 Budget Summary")
            for key, value in result["summary"].items():
                st.write(f"**{key}:** {value}")

            st.subheader("🧮 Suggested Strategy (60/40 Rule on Net Income)")
            for key, value in result["budget_strategy"].items():
                st.write(f"**{key}:** ${value:,.2f}")

            st.subheader("📊 Expense Breakdown")
            st.dataframe(result["expense_breakdown"])

            st.subheader("📉 Budget Chart")
            st.image(f"data:image/png;base64,{result['chart_image_base64']}")


elif menu == "🌍 Caribbean Saving & Investing":
    st.header("🌍 Saving & Investing in the ECCU")
    st.markdown("""
        Learn the best ways to save and invest your money depending on where you live in the Eastern Caribbean. 
        Select your country below to see tailored recommendations for:
        - 🧒 **Youth (Ages 13–25)**
        - 👵 **Adults & Seniors (26+)**
    """)

    country = st.selectbox("Choose your country", [
        "🇦🇮 Anguilla",
        "🇦🇬 Antigua & Barbuda",
        "🇩🇲 Dominica",
        "🇬🇩 Grenada",
        "🇲🇸 Montserrat",
        "🇰🇳 St. Kitts & Nevis",
        "🇱🇨 St. Lucia",
        "🇻🇨 St. Vincent & the Grenadines"
    ])

    if country == "🇦🇮 Anguilla":
        st.subheader("🇦🇮 Anguilla")
        st.markdown("""
        **🧒 For Youth:**
        - Open a Youth Saver Account at **National Commercial Bank of Anguilla (NCBA)** — offers zero fees and competitive interest.
        - Use prepaid debit cards to manage spending and build early budgeting habits.
        - Invest in small mobile vending or online digital services.

        **👵 For Adults:**
        - Consider fixed deposits or property co-investment with **NCBA**.
        - Join Anguilla’s **Credit Unions** for access to saving clubs and low-interest community loans.
        - Use **Republic Bank’s Online Investment Platform** to access bonds or mutual funds.
        """)

    elif country == "🇦🇬 Antigua & Barbuda":
        st.subheader("🇦🇬 Antigua & Barbuda")
        st.markdown("""
        **🧒 For Youth:**
        - Join the **Youth Saver Program** at **Eastern Caribbean Amalgamated Bank (ECAB)**.
        - Learn investment basics through **Antigua Commercial Bank’s Teen Money Matters** campaign.
        - Save weekly from small side hustles (e.g., selling juice, online gigs).

        **👵 For Adults:**
        - Invest in **Government Bonds** through ECAB or Community First Co-op Credit Union.
        - Explore **real estate opportunities** as tourism expands.
        - Join rotating saving groups (“sou-sou”) with contracts via trusted credit unions.
        """)

    elif country == "🇩🇲 Dominica":
        st.subheader("🇩🇲 Dominica")
        st.markdown("""
        **🧒 For Youth:**
        - Open a Junior Savings account with **National Bank of Dominica (NBD)**.
        - Join **Junior Investment Clubs** hosted by local schools or youth orgs.
        - Start agro-based side hustles (hot pepper sauce, small farming).

        **👵 For Adults:**
        - Use NBD's **Certificate of Deposits (CDs)** or Savings Plans.
        - Invest in **green economy** opportunities (solar energy, eco-tourism).
        - Explore **land or family lot ownership** via government land programs.
        """)

    elif country == "🇬🇩 Grenada":
        st.subheader("🇬🇩 Grenada")
        st.markdown("""
        **🧒 For Youth:**
        - Use **Grenada Co-operative Bank's Early Savers Club**.
        - Learn about stocks through ECCB’s **Investment Bootcamps for Youth**.
        - Save income from craft-making or digital freelancing.

        **👵 For Adults:**
        - Utilize **GCB’s fixed deposit options** with high yield rates.
        - Invest in agriculture (nutmeg, cocoa) or eco-tourism.
        - Use **Republic Bank’s financial planning services**.
        """)

    elif country == "🇲🇸 Montserrat":
        st.subheader("🇲🇸 Montserrat")
        st.markdown("""
        **🧒 For Youth:**
        - Join the **Junior Savings Club** with **Bank of Montserrat**.
        - Save from summer jobs or small tech services (e.g., tutoring).
        - Attend ECCB’s youth financial literacy events.

        **👵 For Adults:**
        - Open a **term deposit account** at the Bank of Montserrat.
        - Explore **government-backed investment funds**.
        - Partner with locals for **housing co-investment projects**.
        """)

    elif country == "🇰🇳 St. Kitts & Nevis":
        st.subheader("🇰🇳 St. Kitts & Nevis")
        st.markdown("""
        **🧒 For Youth:**
        - Sign up for the **Youth Future Saver** program at **St. Kitts-Nevis-Anguilla National Bank**.
        - Save carnival and holiday income.
        - Join youth-led co-op savings clubs through school.

        **👵 For Adults:**
        - Buy into **real estate or tourism shares**.
        - Use government’s **Citizenship-by-Investment** returns wisely.
        - Invest in **solar farms** or local energy co-ops.
        """)

    elif country == "🇱🇨 St. Lucia":
        st.subheader("🇱🇨 St. Lucia")
        st.markdown("""
        **🧒 For Youth:**
        - Save in **First National Bank St. Lucia’s Youth Account**.
        - Learn investing basics via the **SLU Stock Exchange training series**.
        - Try digital marketing or product reselling as low-risk income streams.

        **👵 For Adults:**
        - Explore savings + loans at **St. Lucia Credit Co-op**.
        - Invest in tourism-side land leasing or apartment sharing.
        - Buy **government-issued Treasury Bills or Bonds**.
        """)

    elif country == "🇻🇨 St. Vincent & the Grenadines":
        st.subheader("🇻🇨 St. Vincent & the Grenadines")
        st.markdown("""
        **🧒 For Youth:**
        - Join the **Bank of SVG Youth Savers Club**.
        - Save income from weekend jobs or digital freelancing.
        - Learn business skills through school-based mini enterprise programs.

        **👵 For Adults:**
        - Use **Bank of SVG’s fixed-term accounts** or credit union saving circles.
        - Invest in **fishing or agro-processing equipment**.
        - Co-own land or rental properties with family.
        """)


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
        st.success(suggestion)

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
    st.header("🧠 Test Your Knowledge")
    st.markdown("Take a quiz to assess what you know about smart saving, investing, spending, and avoiding fraud.")
    # --- INSERT STREAMLIT FUNCTION ---
    st.markdown("*[Your financial literacy quiz function goes here]*")


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
