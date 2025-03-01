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
st.title("Fetch Full Race Day JSON")

# Function to fetch and display raw JSON
def fetch_race_data():
    response = requests.get(API_URL, auth=(API_USERNAME, API_PASSWORD))
    
    if response.status_code == 200:
        race_data = response.json()
        st.write("### Raw JSON Data from API:")
        st.json(race_data)  # Display JSON in Streamlit
    else:
        st.error(f"Failed to fetch race data. Error: {response.status_code} - {response.text}")

# Button to Fetch Race Data
if st.button("Fetch Race Data"):
    fetch_race_data()
