import streamlit as st
import random


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




def run_common_scams():
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