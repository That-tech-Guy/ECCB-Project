import streamlit as st
import requests
import random



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


def budgeting_function(monthly_income, expenses_list):
    import pandas as pd
    import matplotlib.pyplot as plt
    from io import BytesIO
    import base64

    # Create DataFrame from expenses
    expenses_df = pd.DataFrame(expenses_list)
    expenses_df['Category'] = expenses_df['Category'].str.capitalize()

    # Calculate totals
    total_expenses = expenses_df['Amount'].sum()
    net_income = monthly_income - total_expenses

    # Handle insufficient income
    if net_income < 0:
        return {
            "summary": {
                "Total Income": f"${monthly_income:,.2f}",
                "Total Expenses": f"${total_expenses:,.2f}",
                "Net Income": f"-${abs(net_income):,.2f}"
            },
            "insufficient_income": True,
            "shortfall_amount": abs(net_income),
            "budget_breakdown": expenses_df.to_dict(orient='records')
        }
    
    # If income = expenses
    elif net_income == 0:
        return {
            "summary": {
                "Total Income": f"${monthly_income:,.2f}",
                "Total Expenses": f"${total_expenses:,.2f}",
                "Net Income": f"${abs(net_income):,.2f}"
            },
            "income_breakeven": True,
            "budget_breakdown": expenses_df.to_dict(orient='records')
        }

    # If income is sufficient, continue with savings and chart
    savings = 0.4 * net_income
    remaining = 0.6 * net_income

    strategy = {
        "Income": monthly_income,
        "Total Expenses": total_expenses,
        "Net Income": net_income,
        "Savings (40%)": savings,
        "Remaining (60%)": remaining
    }

    # Pie chart components
    labels = list(expenses_df['Category']) + ['Savings', 'Wants']
    sizes = list(expenses_df['Amount']) + [savings, remaining]
    colors = plt.cm.Paired.colors[:len(expenses_df)] + ('#ffcc66', '#66cc66')
    explode = [0.05] * len(expenses_df) + [0.1, 0.05]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90, textprops={'fontsize': 11, 'color': 'black'})
    ax.axis('equal')

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()

    return {
        "summary": {
            "Total Income": f"${monthly_income:,.2f}",
            "Total Expenses": f"${total_expenses:,.2f}",
            "Net Income": f"${net_income:,.2f}"
        },
        "budget_strategy": strategy,
        "chart_image_base64": chart_base64,
        "budget_breakdown": expenses_df.to_dict(orient='records'),
        "wants_vs_needs": {
            "Wants": remaining,
            "Savings": savings
        },
        "insufficient_income": False
    }


def display_budget_report(result):
    st.markdown("""
        <hr style="height:2px;border:none;color:#333;background-color:#333;" />
        """, unsafe_allow_html=True)

    st.subheader("💡 Budget Summary")
    st.write(f"**Total Income:** {result['summary']['Total Income']}")
    st.write(f"**Total Expenses:** {result['summary']['Total Expenses']}")
    st.write(f"**Net Income:** {result['summary']['Net Income']}")

    st.markdown("""
        <hr style="height:2px;border:none;color:#333;background-color:#333;" />
        """, unsafe_allow_html=True)

    # If user doesn't have enough income
    if result.get("insufficient_income"):
        st.error("🚨 Your expenses are higher than your income!")
        st.markdown(f"You're short by **${result['shortfall_amount']:,.2f}** each month.")
        st.markdown("### 💼 Explore ways to increase your income:")
        st.markdown("Check out the 🧵 Small Hustles in the menu options to: ")
        st.markdown("🔍 Find a Random Side Hustle Ideas")
        st.markdown("💡 Generate Business Ideas")

        st.markdown("""
            <hr style="height:2px;border:none;color:#333;background-color:#333;" />
            """, unsafe_allow_html=True)

        st.subheader("🧾 Expense Breakdown")
        st.dataframe(result["budget_breakdown"])
        return
    
    if result.get("income_breakeven"):
        st.error("🚨 You have no expendable income after paying your expenses!")
        st.markdown("### 💼 Explore ways to increase your income:")
        st.markdown("Check out the 🧵 Small Hustles in the menu options to: ")
        st.markdown("🔍 Find a Random Side Hustle Ideas")
        st.markdown("💡 Generate Business Ideas")

        st.markdown("""
            <hr style="height:2px;border:none;color:#333;background-color:#333;" />
            """, unsafe_allow_html=True)

        st.subheader("🧾 Expense Breakdown")
        st.dataframe(result["budget_breakdown"])
        return

    # Normal flow if income is sufficient
    st.subheader("🧮 Suggested Budget Strategy")
    st.write(f"**Savings (40% of Net Income):** ${result['budget_strategy']['Savings (40%)']}")
    st.write(f"**Remaining (60% of Net Income):** ${result['budget_strategy']['Remaining (60%)']}")
    
    st.markdown("""
        <hr style="height:2px;border:none;color:#333;background-color:#333;" />
        """, unsafe_allow_html=True)

    st.subheader("🧾 Expense Breakdown")
    st.dataframe(result["budget_breakdown"])
    
    st.markdown("""
        <hr style="height:2px;border:none;color:#333;background-color:#333;" />
        """, unsafe_allow_html=True)

    st.subheader("📊 Budget Allocation Chart")
    st.image(f"data:image/png;base64,{result['chart_image_base64']}")
    
    st.markdown("""
        <hr style="height:2px;border:none;color:#333;background-color:#333;" />
        """, unsafe_allow_html=True)

    st.subheader("💸 Needs vs Wants Breakdown")
    st.write(f"**You can spend up to:** ${result['wants_vs_needs']['Wants']:,.2f} on 'Wants'")
    st.write(f"**And make sure to save:** ${result['wants_vs_needs']['Savings']:,.2f}")


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
    page_icon="💰",
    layout="wide",
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
    col1, col2 = st.columns(2)

    # Left column (text content)
    with col1:
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

    # Right column (image)
    with col2:
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
    # Sample streamlit call for user input
    st.header("📊 Your Budget Plan Generator")
    monthly_income = st.number_input("Enter your total monthly income (XCD)", min_value=0.0, step=50.0)

    st.markdown("### Add Your Expenses")

    expense_data = []
    num_expenses = st.number_input("How many expense categories do you want to add?", min_value=1, max_value=10, step=1, value=3)

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
            display_budget_report(result)


elif menu == "🌍 Caribbean Saving & Investing":
    st.header("🌍 Saving & Investing in the ECCU")
    st.markdown("""
        Learn the best ways to save and invest your money depending on where you live in the Eastern Caribbean. 
        Select your country below to see tailored recommendations for:
        - 🧒 **Youth (Ages 13–25)**
        - 👵 **Adults & Seniors (26+)**
    """)
    # Flag URLs
    flag_urls = {
        "Anguilla": "https://flagcdn.com/w320/ai.png",
        "Antigua & Barbuda": "https://flagcdn.com/w320/ag.png",
        "Dominica": "https://flagcdn.com/w320/dm.png",
        "Grenada": "https://flagcdn.com/w320/gd.png",
        "Montserrat": "https://flagcdn.com/w320/ms.png",
        "St. Kitts & Nevis": "https://flagcdn.com/w320/kn.png",
        "St. Lucia": "https://flagcdn.com/w320/lc.png",
        "St. Vincent & the Grenadines": "https://flagcdn.com/w320/vc.png"
    }

    # Country selection
    country = st.selectbox("Choose your country", list(flag_urls.keys()))

    # Show flag image
    st.image(flag_urls[country], width=200)

    # Subheader with country name
    st.subheader(country)

    if country == "Anguilla":
        st.markdown("""
        **🧒 For Youth:**
        - Open a Youth Saver Account at [National Commercial Bank of Anguilla (NCBA)](https://www.ncbal.com) — offers zero fees and competitive interest.
        - Use prepaid debit cards to manage spending and build early budgeting habits.
        - Invest in small mobile vending or online digital services.

        **👵 For Adults:**
        - Consider fixed deposits or property co-investment with [National Commercial Bank of Anguilla (NCBA)](https://www.ncbal.com).
        - Join Anguilla’s [Credit Union](https://www.libertyccu.com/) for access to saving clubs and low-interest community loans.
        - Use [Republic Bank’s Online Investment Platform](https://republictt.com/) to access bonds or mutual funds.
        """)

    elif country == "Antigua & Barbuda":
        st.markdown("""
        **🧒 For Youth:**
        - Join the **Youth Saver Program** at [Eastern Caribbean Amalgamated Bank (ECAB)](https://www.ecabank.com/home/).
        - Learn investment basics through [Antigua Commercial Bank’s Juniour Savings Plan](https://ag.acbonline.com/personal/junior-savings/).
        - Save weekly from small side hustles (e.g., selling juice, online gigs).

        **👵 For Adults:**
        - Invest in [Government Bonds](https://www.ecseonline.com/gov-anu/).
        - Explore [real estate opportunities](https://www.rightmove.co.uk/overseas-property-for-sale/Antigua-and-Barbuda.html) as tourism expands.
        - Join rotating saving groups (“sou-sou”) with contracts via trusted credit unions.
        """)

    elif country == "Dominica":
        st.markdown("""
        **🧒 For Youth:**
        - Open a Wise Start Savings account with [National Bank of Dominica (NBD)](https://nbdominica.com/wisestart/).
        - Join **Junior Investment Clubs** hosted by local schools or youth orgs.
        - Start agro-based side hustles (hot pepper sauce, small farming).

        **👵 For Adults:**
        - Use NBD's **Certificate of Deposits (CDs)** or Savings Plans.
        - Invest in **green economy** opportunities (solar energy, eco-tourism).
        - Explore **land or family lot ownership** via government land programs.
        """)

    elif country == "Grenada":
        st.markdown("""
        **🧒 For Youth:**
        - Use [Grenada Co-operative Bank's](https://www.grenadaco-opbank.com/) **Early Savers Club**.
        - Learn about stocks through ECCB’s **Investment Bootcamps for Youth**.
        - Save income from craft-making or digital freelancing.

        **👵 For Adults:**
        - Utilize **GCB’s fixed deposit options** with high yield rates.
        - Invest in agriculture (nutmeg, cocoa) or eco-tourism.
        - Use [Republic Bank’s](https://republictt.com/) financial planning services**.
        """)

    elif country == "Montserrat":
        st.markdown("""
        **🧒 For Youth:**
        - Join the **Junior Savings Club** with [Bank of Montserrat](https://bankofmontserrat.ms/).
        - Save from summer jobs or small tech services (e.g., tutoring).
        - Attend ECCB’s youth financial literacy events.

        **👵 For Adults:**
        - Open a **term deposit account** at the [Bank of Montserrat](https://bankofmontserrat.ms/).
        - Explore **government-backed investment funds**.
        - Partner with locals for **housing co-investment projects**.
        """)

    elif country == "St. Kitts & Nevis":
        st.markdown("""
        **🧒 For Youth:**
        - Sign up for the **Youth Future Saver** program at [St. Kitts-Nevis-Anguilla National Bank](https://www.sknanb.com/).
        - Save carnival and holiday income.
        - Join youth-led co-op savings clubs through school.

        **👵 For Adults:**
        - Buy into **real estate or tourism shares**.
        - Use government’s **Citizenship-by-Investment** returns wisely.
        - Invest in **solar farms** or local energy co-ops.
        """)

    elif country == "St. Lucia":
        st.markdown("""
        **🧒 For Youth:**
        - Save in [First National Bank St. Lucia’s](https://1stnationalbankonline.com/) **Youth Account**.
        - Learn investing basics via the **SLU Stock Exchange training series**.
        - Try digital marketing or product reselling as low-risk income streams.

        **👵 For Adults:**
        - Explore savings + loans at [St. Lucia Credit Co-op](https://slucculeague.org/).
        - Invest in tourism-side land leasing or apartment sharing.
        - Buy [government](https://www.govt.lc/) **issued Treasury Bills or Bonds**.
        """)

    elif country == "St. Vincent & the Grenadines":
        st.markdown("""
        **🧒 For Youth:**
        - Join the [Bank of SVG](https://www.bosvg.com/) **Youth Savers Club**.
        - Save income from weekend jobs or digital freelancing.
        - Learn business skills through school-based mini enterprise programs.

        **👵 For Adults:**
        - Use [Bank of SVG’s](https://www.bosvg.com/) **fixed-term accounts** or [credit union](https://www.kingstowncreditunion.com/) saving circles.
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
    import streamlit as st
    import warnings
    from agno.agent import Agent
    from agno.models.openrouter import OpenRouter
    from agno.tools.duckduckgo import DuckDuckGoTools

    # Setup warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module='ipywidgets')
    warnings.filterwarnings("ignore", category=RuntimeWarning, module='duckduckgo_search')
    warnings.filterwarnings("ignore", category=ResourceWarning, module='zmq')

    # OpenRouter setup
    API_KEY = "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"
    openrouter_model = OpenRouter(
        id="google/gemini-2.5-flash-lite",
        api_key=API_KEY
    )

    # Create agent
    agent = Agent(
        model=openrouter_model,
        tools=[DuckDuckGoTools()],
        instructions="""
            You're a financial budgeting assistant. You assist users by giving them 10 multiple-choice questions, one at a time.
            After each answer, explain the correct answer before giving the next question. Then tally their total and tell them.
            Always be friendly. If they say no, end with a warm goodbye.
        """,
        add_history_to_messages=False
    )

    # Initialize session state
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.agent_reply = ""
        st.session_state.chat_history = []

    # Define function to run the agent with persistent history
    def run_agent_with_history(user_input):
        response = agent.run(user_input, messages=st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": response.content})
        return response.content

    # UI layout
    st.title("🧠 Financial Literacy Quiz Assistant")
    st.markdown("Welcome! This assistant will quiz you on budgeting, saving, and smart money habits in the Caribbean.")

    # Quiz logic
    if not st.session_state.quiz_started:
        st.markdown("Click the button below when you're ready.")
        if st.button("🚀 Start Quiz"):
            st.session_state.quiz_started = True
            st.session_state.agent_reply = run_agent_with_history("YES I want to start the quiz")
            st.rerun()
        else:
            st.markdown("👆 Press **Start Quiz** to begin.")
    else:
        st.markdown(f"🤖 {st.session_state.agent_reply}")

        # Use a form to ensure input and submit happen together
        with st.form("quiz_form", clear_on_submit=True):
            user_input = st.text_input("Your answer (or type 'exit' to stop):")
            submitted = st.form_submit_button("Submit Answer")

            if submitted:
                if user_input.strip().lower() in ['exit', 'e']:
                    st.markdown("👋 Thanks for participating in the quiz. Come back soon!")
                    st.session_state.quiz_started = False
                    st.session_state.chat_history = []
                    st.session_state.agent_reply = ""
                elif user_input.strip():
                    reply = run_agent_with_history(user_input.strip())
                    st.session_state.agent_reply = reply
                    st.rerun()




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
