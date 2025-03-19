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

# Load CSV files without setting an index
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        # Rename "Horse Name" to "Horse" to match the script usage
        df.rename(columns={"Horse Name": "Horse"}, inplace=True)

        df["Horse"] = df["Horse"].str.lower().str.strip()  # Normalize horse names

        # Convert to dictionary with horse name as key, keeping only the first occurrence
        return df.groupby("Horse").first().to_dict(orient="index")
    
    except Exception as e:
        st.error(f"Error loading CSV {file_path}: {e}")
        return {}

# Load total runs data from CSVs
csv_total_runs = load_csv("all_horses.csv")  # This CSV contains Total Runs

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

# Function to fetch racecards from API
def fetch_racecards():
    response = requests.get(API_URL, auth=(API_USERNAME, API_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch racecards. Check API credentials or API availability.")
        return None

# Function to filter UK Handicap Races
def extract_uk_handicap_races(racecards):
    return [race for race in racecards.get("racecards", []) if race.get("region", "").upper() == "GB" and "handicap" in race.get("race_name", "").lower()]

# Function to extract horse data
def extract_horses_and_form(racecards):
    horses = []
    for race in racecards:
        race_name = race.get("race_name", "")
        race_class = race.get("race_class", "")

        for runner in race.get("runners", []):
            horse_name = runner.get("horse", "Unknown").lower().strip()
            form_string = runner.get("form", "")
            current_weight_lbs = runner.get("lbs", "N/A")
            current_weight_st_lbs = convert_lbs_to_st_lbs(current_weight_lbs)

            processed_form = [int(char) if char.isdigit() else 10 for char in form_string[-6:]]  # Last 6 races
            last_3_positions = processed_form[-3:] if len(processed_form) >= 3 else processed_form
            sum_last_3 = sum(last_3_positions)
            last_finish = processed_form[-1] if len(processed_form) >= 1 else 10

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

# Function to add total runs from CSV
def add_total_runs(horses):
    for horse in horses:
        horse_name = horse["Horse"]
        horse["Total Runs"] = csv_total_runs.get(horse_name, {}).get("Total Runs", "N/A")
    return horses

# Function to filter horses based on total runs
def filter_by_total_runs(horses, max_runs):
    return [horse for horse in horses if isinstance(horse["Total Runs"], (int, float)) and horse["Total Runs"] <= max_runs]

# Streamlit UI
st.title("Horse Racing Filter Program with Weight in st and lbs")

if st.button("Fetch Racecards"):
    racecards = fetch_racecards()

    if racecards:
        uk_handicap_races = extract_uk_handicap_races(racecards)
        st.success("Successfully fetched racecards.")

        # Extract and display all horses before filtering
        all_horses = extract_horses_and_form(uk_handicap_races)
        all_horses_df = pd.DataFrame(all_horses)
        all_horses_df.index = range(1, len(all_horses_df) + 1)
        st.subheader(f"All Horses from UK Handicap Races (Before Filtering) ({len(all_horses)})")
        st.dataframe(all_horses_df)

        # Apply 1st/2nd place filter
        filtered_horses = filter_horses_last_race(all_horses)
        filtered_horses = add_total_runs(filtered_horses)  # Add total runs info
        filtered_horses_df = pd.DataFrame(filtered_horses)
        filtered_horses_df.index = range(1, len(filtered_horses_df) + 1)
        st.subheader(f"Filtered Horses (1st or 2nd in Last Race) ({len(filtered_horses)})")
        st.dataframe(filtered_horses_df)

        # Filter horses with 12 or fewer total runs
        horses_12_or_less = filter_by_total_runs(filtered_horses, 12)
        horses_12_or_less_df = pd.DataFrame(horses_12_or_less)
        horses_12_or_less_df.index = range(1, len(horses_12_or_less_df) + 1)
        st.subheader(f"Horses with 12 or Fewer Runs ({len(horses_12_or_less)})")
        st.dataframe(horses_12_or_less_df)

        # Filter horses with 26 or fewer total runs
        horses_26_or_less = filter_by_total_runs(filtered_horses, 26)
        horses_26_or_less_df = pd.DataFrame(horses_26_or_less)
        horses_26_or_less_df.index = range(1, len(horses_26_or_less_df) + 1)
        st.subheader(f"Horses with 26 or Fewer Runs ({len(horses_26_or_less)})")
        st.dataframe(horses_26_or_less_df)
