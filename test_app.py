import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

# Function to fetch racecards from API
def fetch_racecards():
    url = "https://api.yourapiendpoint.com/racecards"  # Replace with actual API URL
    try:
        response = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch racecards. Error: {e}")
        return None

# Function to process and format race data
def process_race_data(race_data):
    processed_data = []
    for race in race_data.get("races", []):
        race_name = race.get("race_name", "N/A")
        race_class = race.get("race_class", "N/A")
        for horse in race.get("horses", []):
            horse_name = horse.get("name", "N/A")
            weight = horse.get("weight", "N/A")
            # Format: Horse Name (Weight) | Race Class | Other Info | Race Name
            processed_data.append({
                "Horse (Weight)": f"{horse_name} ({weight})",
                "Race Class": race_class,
                "Other Info": horse.get("other_info", "N/A"),
                "Race Name": race_name
            })
    return pd.DataFrame(processed_data)

# Streamlit App
st.title("Horse Racing Filter Program with Weight in st and lbs")

if st.button("Fetch Racecards"):
    race_data = fetch_racecards()
    if race_data:
        df = process_race_data(race_data)
        st.dataframe(df)
    else:
        st.error("Failed to load racecards.")
