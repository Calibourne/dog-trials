import streamlit as st
from datetime import date
from config import dog_names, test_structure, num_of_trials

import matplotlib.pyplot as plt
import io

import pandas as pd
import os
from datetime import datetime


def save_submission(all_trials_data, selected_date, cycle_numbers, dog_name):
    """
    Save the form submission to a uniquely named CSV file.

    Args:
        all_trials_data (list): list of per-trial data with 'command', 'performed', 'attempts'
        selected_date (date): selected session date
        cycle_numbers (list): list of selected cycle numbers
        dog_name (str): name of the dog
    """

    submission_data = []

    for idx, trial_cmds in enumerate(all_trials_data):
        for item in trial_cmds:
            if item["attempts"] > 0 or item["performed"]:
                submission_data.append({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Date": selected_date,
                    "Cycle Number": ', '.join(cycle_numbers),
                    "Dog Name": dog_name,
                    "Trial Number": idx + 1,
                    "Command": item["command"],
                    "Performed": "Yes" if item["performed"] else "No",
                    "Attempts": item["attempts"]
                })

    if not submission_data:
        return None  # No useful data to save

    # Create DataFrame
    df = pd.DataFrame(submission_data)

    # Create directory
    os.makedirs("submissions", exist_ok=True)

    # Create filename
    timestamp = selected_date.strftime("%Y%m%d")
    dog_clean = dog_name.replace(" ", "_")
    filename = f"submissions/{timestamp}_{dog_clean}.csv"

    # Save
    df.to_csv(filename, index=False, encoding='utf-8-sig')

    return filename

import pandas as pd
import glob

import pandas as pd
import glob

def generate_performance_report(submissions_folder="submissions"):
    """
    Generate a performance report based on number of attempts per dog per command.

    Args:
        submissions_folder (str): folder containing submissions

    Returns:
        pd.DataFrame: pivoted performance report
    """

    # Read all submissions
    submission_files = glob.glob(f"{submissions_folder}/*.csv")

    if not submission_files:
        raise FileNotFoundError("No submission files found.")

    all_data = []
    for file in submission_files:
        df = pd.read_csv(file, encoding='utf-8-sig')
        all_data.append(df)

    # Merge
    full_df = pd.concat(all_data, ignore_index=True)

    # Defensive rename
    if "Dog Name" in full_df.columns:
        full_df.rename(columns={"Dog Name": "NAME"}, inplace=True)
    if "Command" in full_df.columns:
        full_df.rename(columns={"Command": "פקודה"}, inplace=True)

    # 🧠 REAL success rate per instance
    def calculate_instance_success(attempts):
        if attempts == 0:
            return 0
        else:
            return 1 / attempts

    full_df['Instance Success'] = full_df['Attempts'].apply(calculate_instance_success)

    # Group by Dog and Command, take the mean of instance success
    grouped = (
        full_df
        .groupby(['NAME', 'פקודה'])
        .agg(mean_success=('Instance Success', 'mean'))
        .reset_index()
    )

    # Format as percentage
    grouped['Success Rate'] = (grouped['mean_success'] * 100).round(2)

    # Pivot table
    pivot_table = grouped.pivot(index='NAME', columns='פקודה', values='Success Rate')

    # Beautify
    pivot_table = pivot_table.fillna(0).round(2).astype(str) + '%'

    return pivot_table

def generate_pdf_in_memory(report_df, title="Performance Report"):
    """
    Generate a PDF from the report DataFrame and return it as bytes, no saving to disk.

    Args:
        report_df (pd.DataFrame): the pivot table to turn into a PDF
        title (str): optional title for the report

    Returns:
        bytes: the PDF file in memory
    """

    buffer = io.BytesIO()

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(len(report_df.columns)*2, len(report_df)*0.5 + 2))
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    # Build table
    table = ax.table(
        cellText=report_df.values,
        colLabels=report_df.columns,
        rowLabels=report_df.index,
        cellLoc='center',
        loc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.2)

    # Add title
    plt.title(title + datetime.now().strftime(" - %d %B %Y"))

    # Save to memory buffer
    plt.savefig(buffer, format="pdf", bbox_inches='tight')
    plt.close()

    buffer.seek(0)
    return buffer


st.set_page_config(page_title="Dog Training Form 🐶", page_icon="🐾")
with st.expander("טופס אימון כלבים 🐕‍🦺", expanded=True):
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
            cols = st.columns([1, 3, 2])  # checkbox | command name | number input

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

            if performed and attempts == 0:
                st.warning(f"⚠️ שים לב: סימנת 'בוצע' אבל לא ציינת מספר פעמים לפקודה: {cmd}", icon="⚠️")

            trial_data.append({
                "command": cmd,
                "performed": performed,
                "attempts": attempts
            })

    all_trials_data.append(trial_data)
    st.write("### סיכום שליחה:")
    summary_data = []
    for trial in all_trials_data:
        for item in trial:
            summary_data.append({
                "Command": item["command"],
                "Performed": "Yes" if item["performed"] else "No",
                "Attempts": item["attempts"]
            })
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

    # Submit Button
    if st.button("שלח טופס"):
        if dog == "בחר":
            st.error("בבקשה תבחר כלב 🐶")
        else:
            saved_file = save_submission(
                all_trials_data=all_trials_data,
                selected_date=selected_date,
                cycle_numbers=cycle_numbers,
                dog_name=dog
            )

            if saved_file:
                st.success(f"הטופס נשמר בקובץ: {saved_file} 📄")
            else:
                st.warning("אין נתונים לשמירה. אולי לא סומנו פקודות? 😕")

if st.button("צור דו\"ח ביצועים PDF"):
    try:
        report = generate_performance_report()
        st.success("✅ דו\"ח נוצר בהצלחה!")
        st.dataframe(report)

        pdf_buffer = generate_pdf_in_memory(report)

        st.download_button(
            label="📥 הורד את הדו\"ח כקובץ PDF",
            data=pdf_buffer,
            file_name=f"performance_report_{datetime.now().strftime('- %d_%B_%Y')}.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"❌ שגיאה ביצירת הדו\"ח: {e}")
