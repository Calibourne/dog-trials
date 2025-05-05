import streamlit as st
from datetime import date
from config import dog_names, num_of_trials
from config import s3_client, bucket_name
from glob import glob
import matplotlib.pyplot as plt
import io
import pandas as pd
from datetime import datetime

def get_test_templates():
    """
    Load test templates from the local directory.
    """
    test_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="templates/")
    if "Contents" not in test_files:
        raise FileNotFoundError("No test templates found in S3.")
    test_files = [obj['Key'] for obj in test_files["Contents"] if obj['Key'].endswith('.txt')]
    templates = []
    for file in test_files:
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=file)
        content = s3_object['Body'].read().decode('utf-8')
        templates.append(content.splitlines())
    return templates

def save_submission(all_trials_data, selected_date, cycle_numbers, dog_name, training_location):
    """
    Save the form submission directly to AWS S3 as CSV.
    """

    submission_data = []

    for idx, trial_cmds in enumerate(all_trials_data):
        for item in trial_cmds:
            if item["attempts"] > 0 or item["performed"] or (item.get("command") == "come" and item.get("come_method")):
                submission_data.append({
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Date": selected_date.strftime("%Y-%m-%d"),
                    "Cycle Number": ', '.join(cycle_numbers),
                    "Dog Name": dog_name,
                    "Training Location": training_location,
                    "Trial Number": idx + 1,
                    "Command": item["command"],
                    "Performed": "Yes" if item["performed"] else "No",
                    "Attempts": item["attempts"],
                    "Come Method": item.get("come_method", "")  # Safe fallback
                })

    if not submission_data:
        return None

    df = pd.DataFrame(submission_data)

    buffer = io.StringIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)

    timestamp = selected_date.strftime("%Y%m%d")
    dog_clean = dog_name.replace(" ", "_")
    s3_path = f"submissions/{timestamp}_{dog_clean}_{training_location}.csv"

    s3_client.put_object(
        Bucket=bucket_name,
        Key=s3_path,
        Body=buffer.getvalue(),
        ContentType="text/csv"
    )

    return f"s3://{bucket_name}/{s3_path}"


@st.cache_resource
def load_all_submissions():
    """Load all submissions from S3"""
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="submissions/")

    if "Contents" not in response:
        raise FileNotFoundError("No submissions found in S3.")

    all_data = []
    for obj in response["Contents"]:
        if obj['Key'].endswith('.csv'):
            s3_object = s3_client.get_object(Bucket=bucket_name, Key=obj['Key'])
            df = pd.read_csv(s3_object['Body'], encoding='utf-8-sig')
            all_data.append(df)

    if not all_data:
        raise FileNotFoundError("No valid submission files found in S3.")

    full_df = pd.concat(all_data, ignore_index=True)

    # Defensive rename
    if "Dog Name" in full_df.columns:
        full_df.rename(columns={"Dog Name": "NAME"}, inplace=True)
    if "Command" in full_df.columns:
        full_df.rename(columns={"Command": "פקודה"}, inplace=True)

    full_df['Date'] = pd.to_datetime(full_df['Date'])  # Ensure Date is datetime

    return full_df


def generate_performance_report(full_df, start_date, end_date, selected_dogs):
    """
    Generate a report based on preloaded DF, filtered by user selection.
    """

    # Apply filters
    filtered_df = full_df[
        (full_df['Date'] >= pd.to_datetime(start_date)) &
        (full_df['Date'] <= pd.to_datetime(end_date)) &
        (full_df['NAME'].isin(selected_dogs))
    ]

    if filtered_df.empty:
        raise ValueError("אין נתונים בטווח התאריכים או עבור הכלבים שנבחרו.")

    # Calculate success
    def calculate_instance_success(attempts):
        if attempts == 0:
            return 0
        else:
            return 1 / attempts

    filtered_df['Instance Success'] = filtered_df['Attempts'].apply(calculate_instance_success)

    # Group
    grouped = (
        filtered_df
        .groupby(['NAME', 'פקודה'])
        .agg(mean_success=('Instance Success', 'mean'))
        .reset_index()
    )

    grouped['Success Rate'] = (grouped['mean_success'] * 100).round(2)

    # Pivot
    pivot_table = grouped.pivot(index='NAME', columns='פקודה', values='Success Rate')
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

    # Dog selection
    dog = st.selectbox(
        "בחר כלב",
        options=["בחר", *dog_names]
    )
    # training location <=> synonymous to cycle numbers
    training_location = st.radio(
        "מיקום האימון",
        options=["in-building", "outdoor"],
        horizontal=True,
        key="training_location"
    )

    st.write("כמה שליחות (cycles) בוצעו?")
    completed_cycles = st.number_input(
        label="מספר שליחות שבוצעו",
        min_value=1,
        max_value=num_of_trials,
        step=1,
        value=num_of_trials,
        key="completed_cycles"
    )

    # Load test templates
    try:
        test_structure = get_test_templates()
    except FileNotFoundError:
        st.error("לא נמצאו תבניות אימון ב-S3. אנא טען תבניות אימון קודם.")
        st.stop()
    # Select test template
    selected_template = st.selectbox(
        "בחר תבנית אימון",
        options=["בחר", *[f"Template {i+1}" for i in range(len(test_structure))]],
        key="selected_template"
    )
    if selected_template != "בחר":
        test_structure = test_structure[int(selected_template.split()[1]) - 1]
        st.write("תבנית שנבחרה:")
        st.dataframe(test_structure)
    else:

        st.write("לא נבחרה תבנית. אין להגיש את הטופס ללא תבנית.")
        test_structure = []
    # Show instructions

    # Collect all commands + attempts + success checkbox
    all_trials_data = []

    for i in range(int(completed_cycles)):
        st.write(f"### שליחה {i+1}:")
        trial_data = []

        dynamic_structure = []
        come_method = ""

        for base_cmd in test_structure:
            dynamic_structure.append({"command": base_cmd, "read_only": False})
            if base_cmd.lower() == "come":
                come_method = st.selectbox(
                    f"Trial {i+1} - צורת הקריאה ל- Come (אופציונלי)",
                    options=["", "voice", "whistle"],
                    key=f"come_method_trial_{i}"
                )
                if come_method == "whistle":
                    dynamic_structure.append({"command": "sit", "read_only": True})  # 🛠 Insert fake sit, mark read-only

        for j, cmd_info in enumerate(dynamic_structure):
            cmd = cmd_info["command"]
            read_only = cmd_info["read_only"]

            cols = st.columns([1, 3, 2])

            if read_only:
                with cols[0]:
                    st.markdown("🟰")  # Icon to hint: "no action needed"
                with cols[1]:
                    st.markdown(f"**{cmd} (אוטומטי אחרי שריקה)**")
                with cols[2]:
                    st.markdown("-")
                # Save "performed = True", "attempts = 1" silently
                trial_data.append({
                    "command": cmd,
                    "performed": True,
                    "attempts": 1,
                    "come_method": "",  # not relevant for fake sit
                    "fake_sit": True
                })
            else:
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
                    "attempts": attempts,
                    "come_method": come_method if cmd.lower() == "come" else "",
                    "fake_sit": False
                })

        all_trials_data.append(trial_data)

    # Submit Button
    if len(test_structure) > 0:
        if st.button("שלח טופס"):
            if dog == "בחר":
                st.error("בבקשה תבחר כלב 🐶")
            else:
                saved_file = save_submission(
                    cycle_numbers=[f"{i+1}" for i in range(int(completed_cycles))],
                    training_location=training_location,
                    all_trials_data=all_trials_data,
                    selected_date=selected_date,
                    dog_name=dog
                )

                if saved_file:
                    st.success(f"הטופס נשמר בקובץ: {saved_file} 📄")
                else:
                    st.warning("אין נתונים לשמירה. אולי לא סומנו פקודות? 😕")

with st.expander("היסטוריית הגשות", expanded=False):
    # Load all data
    try:
        full_df = load_all_submissions()

        # Extract available dogs
        available_dogs = sorted(full_df['NAME'].unique())

        # 🐶 Dog Multi-select
        selected_dogs = st.multiselect(
            "בחר כלבים להיסטוריה:",
            options=available_dogs,
            default=available_dogs  # Default: select all
        )

        # 🗓 Date Range
        st.write("בחר טווח תאריכים:")
        min_date = full_df['Date'].min().date()
        max_date = full_df['Date'].max().date()
        start_date = st.date_input("מתאריך", min_value=min_date, max_value=max_date, value=min_date, key="history_start_date")
        end_date = st.date_input("עד תאריך", min_value=min_date, max_value=max_date, value=max_date, key="history_end_date")

        if selected_dogs:
            tabs = st.tabs([f"היסטוריה עבור {dog}" for dog in selected_dogs])
            for tab, dog in zip(tabs, selected_dogs):
                with tab:
                    dog_df = full_df[
                    (full_df['NAME'] == dog) &
                    (full_df['Date'] >= pd.to_datetime(start_date)) &
                    (full_df['Date'] <= pd.to_datetime(end_date))
                    ]
                    if not dog_df.empty:
                       dog_df = dog_df.drop(columns=["Cycle Number", "Timestamp", "NAME"])
                       dog_df['Date'] = pd.to_datetime(dog_df['Date']).dt.strftime('%d/%m/%Y')
                       st.dataframe(dog_df)
                    else:
                        st.warning(f"אין נתונים להיסטוריה עבור {dog} בטווח התאריכים שנבחר.")
        else:
            st.warning("לא נבחרו כלבים להיסטוריה.")

    except FileNotFoundError:
        st.warning("לא נמצאו קבצי הגשה ב-S3. אנא הגש טופס אימון קודם.")

with st.expander("דו\"ח ביצועים", expanded=False):
    # Load all data
    try:
        full_df = load_all_submissions()

        # Extract available dogs
        available_dogs = sorted(full_df['NAME'].unique())

        # Extract min/max dates
        min_date = full_df['Date'].min().date()
        max_date = full_df['Date'].max().date()

        # 🐶 Dog Multi-select
        selected_dogs = st.multiselect(
            "בחר כלבים לדו\"ח:",
            options=available_dogs,
            default=available_dogs  # Default: select all
        )

        # 🗓 Date Range
        st.write("בחר טווח תאריכים:")
        start_date = st.date_input("מתאריך", min_value=min_date, max_value=max_date, value=min_date)
        end_date = st.date_input("עד תאריך", min_value=min_date, max_value=max_date, value=max_date)

        if st.button("צור דו\"ח ביצועים"):
            try:
                report = generate_performance_report(
                    full_df=full_df,
                    start_date=start_date,
                    end_date=end_date,
                    selected_dogs=selected_dogs
                )
                if report.empty:
                    st.warning("אין נתונים לדו\"ח עבור הכלבים שנבחרו בטווח התאריכים שנבחר.")

                pdf_buffer = generate_pdf_in_memory(report)

                st.download_button(
                    label="📥 הורד את הדו\"ח",
                    data=pdf_buffer,
                    file_name=f"performance_report_{datetime.now().strftime('- %d_%B_%Y')}.pdf",
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"❌ שגיאה ביצירת הדו\"ח: {e}")
    except:
        st.warning("לא נמצאו קבצי הגשה ב-S3. אנא הגש טופס אימון קודם.")
