import streamlit as st

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




def gen_budget():
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