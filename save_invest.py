import streamlit as st




def invest():
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