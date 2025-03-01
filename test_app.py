import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import date  # Make sure we properly handle dates

# Load API credentials from .env file
load_dotenv()
API_USERNAME = os.getenv("API_USERNAME")
API_PASSWORD = os.getenv("API_PASSWORD")
API_URL = "https://api.theracingapi.com/v1/racecards"

# Streamlit App Title
st.title("Horse Racing Filter Program with Weight in st and lbs")

# Date Picker Widget
selected_date = st.date_input("Select a Race Date", value=date.today())  # Default to today

# Function to fetch racecards from API for a specific date
def fetch_racecards_for_date(selected_date):
    if not isinstance(selected_date, date):  # Ensure selected_date is a valid date object
        st.error("Invalid date selection. Please choose a valid date.")
        return None

    formatted_date = selected_date.strftime("%Y-%m-%d")  # Convert date to YYYY-MM-DD format
    url = f"{API_URL}?start_date={formatted_date}&end_date={formatted_date}"

    try:
        response = requests.get(url, auth=(API_USERNAME, API_PASSWORD))
        response.raise_for_status()
        data = response.json()

        if not data.get("racecards"):
            st.warning(f"No racecards found for {formatted_date}. Try a different date.")
            return None

        return data

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch racecards for {formatted_date}. Error: {e}")
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

            processed_form = [int(char) if char.isdigit() else 10 for char in form_string[-6:]]  # Last 6 races
            last_3_positions = processed_form[-3:] if len(processed_form) >= 3 else processed_form
            sum_last_3 = sum(last_3_positions)
            last_finish = processed_form[-1] if len(processed_form) >= 1 else 10
            second_last_finish = processed_form[-2] if len(processed_form) >= 2 else 10

            horses.append({
                "Horse": horse_name,
                "Race Class": race_class,
                "Race Name": race_name,
                "Form (Last 6 Races)": " ".join(map(str, processed_form)),
                "Last Finish": last_finish,
                "Second Last Finish": second_last_finish,
                "Sum Last 3 Positions": sum_last_3,
                "Current Weight (st and lbs)": current_weight_st_lbs
            })
    return horses

# Function to filter horses that finished 1st or 2nd in last two races
def filter_horses_last_two(horses):
    return [horse for horse in horses if horse["Last Finish"] in [1, 2] and horse["Second Last Finish"] in [1, 2]]

# Streamlit UI
if st.button("Fetch Racecards"):
    racecards = fetch_racecards_for_date(selected_date)

    if racecards:
        uk_handicap_races = extract_uk_handicap_races(racecards)
        if not uk_handicap_races:
            st.warning(f"No UK Handicap races found for {selected_date.strftime('%Y-%m-%d')}. Try another date.")
        else:
            st.success(f"Successfully fetched racecards for {selected_date.strftime('%Y-%m-%d')}.")

            # Extract and display all horses before filtering
            all_horses = extract_horses_and_form(uk_handicap_races)
            all_horses_df = pd.DataFrame(all_horses)
            all_horses_df.index = range(1, len(all_horses_df) + 1)  # Start indexing from 1
            st.subheader(f"All Horses from UK Handicap Races (Before Filtering) ({len(all_horses)})")
            st.dataframe(all_horses_df)

            # Apply filter and display filtered horses
            filtered_horses = filter_horses_last_two(all_horses)
            filtered_horses_df = pd.DataFrame(filtered_horses)
            filtered_horses_df.index = range(1, len(filtered_horses_df) + 1)  # Start indexing from 1
            st.subheader("Filtered Horses (1st or 2nd in Last Two Races)")
            st.dataframe(filtered_horses_df)
