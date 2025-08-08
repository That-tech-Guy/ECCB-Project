import streamlit as st
import requests


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


def converter():
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