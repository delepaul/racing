import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Load API credentials from .env file
load_dotenv()
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_URL = "https://api.theracingapi.com/v1/racecards"

# Streamlit App Title
st.title("Horse Racing Filter Program with Weight in st and lbs")

# Function to fetch racecards from API
def fetch_racecards():
    response = requests.get(API_URL, auth=(API_USERNAME, API_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch racecards. Check API credentials or API availability.")
        return None

# Function to convert lbs to st and lbs
def convert_lbs_to_st_lbs(lbs):
    if lbs == "N/A" or lbs == "":
        return "N/A"
    try:
        lbs = int(lbs)
        stones = lbs // 14
        remaining_lbs = lbs % 14
        return f"{stones}st {remaining_lbs}lbs"
    except ValueError:
        return "N/A"

# Function to filter UK Handicap Races
def extract_uk_handicap_races(racecards):
    uk_handicap_races = []
    for race in racecards.get("racecards", []):
        if race.get("region", "").upper() == "GB" and "handicap" in race.get("race_name", "").lower():
            uk_handicap_races.append(race)
    return uk_handicap_races

# Function to extract horses, form data, and converted weight
def extract_horses_and_form(racecards):
    horses = []
    for race in racecards:
        race_name = race.get("race_name", "")
        race_class = race.get("race_class", "")

        for runner in race.get("runners", []):
            horse_name = runner.get("horse", "Unknown")
            form_string = runner.get("form", "")
            current_weight_lbs = runner.get("lbs", "N/A")
            current_weight_st_lbs = convert_lbs_to_st_lbs(current_weight_lbs)

            # Process last 6 races form
            processed_form = [int(char) if char.isdigit() else 10 for char in form_string[-6:]]

            # Get the last race position
            last_finish = processed_form[-1] if len(processed_form) >= 1 else 10

            # Sum of last 3 race positions
            last_3_positions = processed_form[-3:] if len(processed_form) >= 3 else processed_form
            sum_last_3 = sum(last_3_positions)

            horses.append({
                "Horse": horse_name,
                "Race Class": race_class,
                "Form (Last 6 Races)": " ".join(map(str, processed_form)),
                "Last Finish": last_finish,
                "Sum Last 3 Positions": sum_last_3,
                "Current Weight (st and lbs)": current_weight_st_lbs,
                "Race Name": race_name
            })
    return horses

# Function to filter horses that finished 1st or 2nd in their last race
def filter_horses_last_race(horses):
    return [horse for horse in horses if horse["Last Finish"] in [1, 2]]

# Streamlit UI
if st.button("Fetch Racecards"):
    racecards = fetch_racecards()

    if racecards:
        uk_handicap_races = extract_uk_handicap_races(racecards)
        st.success("Successfully fetched racecards.")

        # Extract and display all horses before filtering
        all_horses = extract_horses_and_form(uk_handicap_races)
        all_horses_df = pd.DataFrame(all_horses)
        all_horses_df.index = range(1, len(all_horses_df) + 1)  # Start indexing from 1
        st.subheader(f"All Horses from UK Handicap Races (Before Filtering) ({len(all_horses)})")
        st.dataframe(all_horses_df)

        # Apply filter and display filtered horses
        filtered_horses = filter_horses_last_race(all_horses)
        filtered_horses_df = pd.DataFrame(filtered_horses)
        filtered_horses_df.index = range(1, len(filtered_horses_df) + 1)  # Start indexing from 1
        st.subheader("Filtered Horses (1st or 2nd in Last Race)")
        st.dataframe(filtered_horses_df)
