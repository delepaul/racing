import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API credentials
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")

# Streamlit App Title
st.title("Horse Racing Filter Program with Weight in st and lbs")

# Function to convert weight from lbs to st and lbs
def convert_weight(weight_lbs):
    stones = weight_lbs // 14
    pounds = weight_lbs % 14
    return f"{stones}st {pounds}lbs"

# Function to fetch racecards
def fetch_racecards():
    url = "https://api.example.com/racecards"  # Replace with actual API URL
    response = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch racecards. Check API credentials or API availability.")
        return None

# Function to process race data
def process_race_data(data):
    processed_data = []
    for race in data.get("races", []):
        race_name = race.get("race_name", "N/A")
        race_class = race.get("race_class", "N/A")
        for horse in race.get("horses", []):
            horse_name = horse.get("name", "N/A")
            weight_lbs = horse.get("weight", 0)
            weight_st_lbs = convert_weight(weight_lbs)
            other_info = horse.get("other_info", "N/A")
            processed_data.append({
                "Horse Name": horse_name,
                "Race Weight": weight_st_lbs,
                "Race Class": race_class,
                "Other Info": other_info,
                "Race Name": race_name
            })
    return pd.DataFrame(processed_data)

# Fetch and display racecards if button is clicked
if st.button("Fetch Racecards"):
    race_data = fetch_racecards()
    if race_data:
        df = process_race_data(race_data)
        st.dataframe(df)
