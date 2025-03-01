import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv

# Load API credentials
load_dotenv()
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_URL = "https://api.theracingapi.com/v1/racecards"

# Function to fetch full race day JSON
def fetch_race_json(date):
    formatted_date = date.strftime("%Y-%m-%d")  # Format to YYYY-MM-DD
    url = f"{API_URL}?start_date={formatted_date}&end_date={formatted_date}"
    
    try:
        response = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch racecards for {formatted_date}. Error: {e}")
        return None

# Streamlit UI for testing
st.title("Fetch Full Race Day JSON")

selected_date = st.date_input("Select Race Date")
if st.button("Fetch Race Data"):
    race_data = fetch_race_json(selected_date)
    
    if race_data:
        st.json(race_data)  # Display raw JSON in Streamlit
