import streamlit as st
import requests
from together import Together
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Initialize the Together client
client = Together(api_key=TOGETHER_API_KEY)

def fetch_crypto_info(cryptos):
    """
    Fetches detailed information about the specified cryptocurrencies from the CoinGecko API.

    Parameters:
    - cryptos (list): A list of cryptocurrency names.

    Returns:
    - dict: A dictionary containing the cryptocurrencies' price information.
    """
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={','.join(cryptos)}&order=market_cap_desc&per_page=100&page=1&sparkline=false"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Collect info for each cryptocurrency
        crypto_info_list = []
        for coin_data in data:
            crypto_info_list.append({
                "name": coin_data["name"],
                "current_price": coin_data["current_price"],
                "price_change_percentage_24h": coin_data["price_change_percentage_24h"],
                "market_cap": coin_data["market_cap"],
                "total_volume": coin_data["total_volume"],
                "circulating_supply": coin_data["circulating_supply"],
            })
        return crypto_info_list
    except Exception as e:
        return {"error": str(e)}

def get_llama_response(prompt):
    """
    Sends a prompt to the Together AI LLaMA model and retrieves the response.

    Parameters:
    - prompt (str): The user's prompt or question for the model.

    Returns:
    - str: The model's response or an error message if the request fails.
    """
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        return f"Error retrieving response: {str(e)}"

def plot_price_history(cryptos):
    """
    Fetches and plots the historical price data for the specified cryptocurrencies.

    Parameters:
    - cryptos (list): A list of cryptocurrency names.
    """
    plt.figure(figsize=(10, 5))
    
    for crypto in cryptos:
        url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart?vs_currency=usd&days=7"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            prices = data['prices']
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            plt.plot(df['timestamp'], df['price'], label=f'{crypto.capitalize()} Price')
        except Exception as e:
            st.error(f"Error fetching price history for {crypto}: {str(e)}")

    plt.title('Cryptocurrency Price History (Last 7 Days)')
    plt.xlabel('Date')
    plt.ylabel('Price in USD')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    st.pyplot(plt)

# Streamlit app title
st.title("Crypto Insight Hub")

# Prompt input for cryptocurrency query
cryptos_input = st.text_input("Enter cryptocurrencies (e.g., bitcoin, ethereum, dogecoin):", "bitcoin,ethereum")

# Parse input into a list
cryptos = [crypto.strip().lower() for crypto in cryptos_input.split(',')]

# Display cryptocurrency information
if st.button("Get Cryptocurrency Info"):
    with st.spinner("Fetching cryptocurrency info..."):
        crypto_info_list = fetch_crypto_info(cryptos)

    if isinstance(crypto_info_list, list):
        # Create a comparison table with dollar sign and color indicators
        st.subheader("Cryptocurrency Comparison:")
        comparison_df = pd.DataFrame(crypto_info_list)
        
        # Format prices with dollar sign and color indicators
        comparison_df['current_price'] = comparison_df['current_price'].apply(lambda x: f"${x:,.2f}")
        comparison_df['price_change_percentage_24h'] = comparison_df['price_change_percentage_24h'].apply(
            lambda x: f"{x:.2f}%" if x > 0 else f"{x:.2f}%"
        )
        
        # Apply color formatting for the price change percentage
        def color_price_change(val):
            color = 'green' if float(val[:-1]) > 0 else 'red'
            return f'color: {color}'

        # Highlighting the price change percentage in the DataFrame
        styled_df = comparison_df.style.applymap(color_price_change, subset=['price_change_percentage_24h'])

        st.dataframe(styled_df)

        # Plot the price history for all selected cryptocurrencies
        plot_price_history(cryptos)

        # Optional: Get additional insights from LLaMA about each cryptocurrency
        for crypto in cryptos:
            if st.button(f"Get Insights for {crypto.capitalize()} from LLaMA"):
                with st.spinner(f"Fetching insights for {crypto.capitalize()}..."):
                    insights_response = get_llama_response(f"Tell me about {crypto}.")
                
                # Display the insights from LLaMA
                st.subheader(f"Insights for {crypto.capitalize()} from LLaMA:")
                if "Error" in insights_response:
                    st.error(insights_response)
                else:
                    st.write(insights_response)
    else:
        st.error(crypto_info_list.get("error", "Could not retrieve cryptocurrency information."))
