import streamlit as st
from datetime import date
from config import dog_names, test_structure, num_of_trials

st.set_page_config(page_title="Dog Training Form 🐶", page_icon="🐾")

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

# Collect all commands + attempts + success checkbox
all_trials_data = []

for i in range(num_of_trials):
    st.write(f"### שליחה {i+1}:")
    trial_data = []
    for j, cmd in enumerate(test_structure):
        cols = st.columns([1, 3, 2])  # Adjusted for: checkbox | command name | number input

        with cols[0]:
            performed = st.checkbox("", key=f"trial_{i}_cmd_{j}_check")
        with cols[1]:
            st.markdown(f"**{cmd}**")
        with cols[2]:
            attempts = st.number_input(
                label="",
                min_value=0,
                step=1,
                value=0,
                key=f"trial_{i}_cmd_{j}_attempts"
            )

        trial_data.append({
            "command": cmd,
            "performed": performed,
            "attempts": attempts
        })
    all_trials_data.append(trial_data)

# Submit Button
if st.button("שלח טופס"):
    if dog == "בחר":
        st.error("בבקשה תבחר כלב 🐶")
    else:
        st.success("הטופס נשלח בהצלחה! 🚀")
        st.write("### הפרטים שהוזנו:")
        st.write(f"**תאריך:** {selected_date}")
        st.write(f"**מספר מחזור:** {', '.join(cycle_numbers) if cycle_numbers else 'ללא'}")
        st.write(f"**כלב:** {dog}")