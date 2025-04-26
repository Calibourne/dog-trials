import streamlit as st
from datetime import date
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Dog Training Form 🐶", page_icon="🐾")

# Load environment variables
load_dotenv()

dog_names = os.getenv("DOG_NAMES").split(",")
test_structure = os.getenv("TEST_STRUCTURE").split(",")
num_of_trials = int(os.getenv("NUM_OF_TRIALS"))

st.title("טופס אימון כלבים 🐕‍🦺")

# Date input
selected_date = st.date_input("תאריך", value=date.today())

# Cycle Number - multiple checkbox style
st.write("מספר מחזור:")
cycle_numbers = []
for num in ["1", "2"]:
    if st.checkbox(num, key=f"cycle_{num}"):
        cycle_numbers.append(num)

# Dog selection
dog = st.selectbox(
    "בחר כלב",
    options=["בחר", *dog_names]
)

# Collect all commands for all trials
all_trials_selected_commands = []

for i in range(num_of_trials):
    st.header(f"שליחה {i+1}:")
    trial_selected_commands = []
    for j, cmd in enumerate(test_structure):
        # Make key unique per trial
        if st.checkbox(cmd, key=f"trial_{i}_cmd_{j}"):
            trial_selected_commands.append(cmd)
    all_trials_selected_commands.append(trial_selected_commands)

# Submit Button
if st.button("שלח טופס"):
    if dog == "בחר":
        st.error("בבקשה תבחר כלב 🐶")
    if not cycle_numbers:
        st.error("בבקשה תבחר מספר מחזור")
    else:
        st.success("הטופס נשלח בהצלחה! 🚀")
