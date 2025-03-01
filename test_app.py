import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_URL = "https://api.theracingapi.com/v1/racecards"

# Streamlit App Title
st.title("Horse Racing Filter Program")

# Date input widget
selected_date = st.date_input("Select a race date")

# Function to fetch racecards for a specific date
def fetch_racecards_for_date(date):
    url = f"{API_URL}?date={date}"  # Corrected API format
    try:
        response = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
        response.raise_for_status()  # Raise error if request fails
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch racecards for {date}. Error: {e}")
        return None

# Fetch racecards button
if st.button("Fetch Racecards"):
    formatted_date = selected_date.strftime("%Y-%m-%d")  # Convert to YYYY-MM-DD
    racecards = fetch_racecards_for_date(formatted_date)

    if racecards:
        st.success(f"Successfully fetched racecards for {formatted_date}.")
        st.json(racecards)  # Display raw JSON for debugging
