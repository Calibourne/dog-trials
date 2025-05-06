import datetime
from boto3 import Session
from copy import deepcopy as _copy
from datetime import datetime

import pandas as pd
from backend.utils.consts import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, AWS_BUCKET_NAME
from backend.models.submission import Submission

_session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION)

_s3_client = _session.client("s3")

record_template = {
    "Timestamp": "",
    "Date": "",
    "Dog Name": "",
    "Training Location": "",
    "Trial Number": 0,
    "Command": "",
    "Performed": "",
    "Command Type": "",
    "Come Method": "",
    "Fake Sit": False,
    "Attempts": 0,
    "Extra Entries": 0
}

def save_submission_s3(submission: Submission) -> str:
    """
    Save the submission to S3
    :param submission: The submission object to save
    """

    submission_records = []

    for trial in submission.trials:
        for cmd in trial.commands:
            record = _copy(record_template)
            record["Timestamp"] = datetime.now().isoformat()
            record["Date"] = submission.date.isoformat()
            record["Dog Name"] = submission.dog_name
            record["Training Location"] = submission.training_location
            record["Trial Number"] = trial.trial_number
            record["Command"] = cmd.command
            record["Performed"] = cmd.performed
            record["Command Type"] = cmd.command_type
            record["Come Method"] = cmd.come_method
            record["Fake Sit"] = cmd.fake_sit

        
            if cmd.command_type == "strict":
                record["Attempts"] = cmd.attempts
                record["Extra Entries"] = ""

            elif cmd.command_type == "soft":
                record["Attempts"] = ""
                record["Extra Entries"] = cmd.extra_entries

            submission_records.append(record)

    df = pd.DataFrame(submission_records)
    date_str = submission.date.strftime("%Y%m%d")
    dog_clean = submission.dog_name.replace(" ", "_")
    location = submission.training_location.replace(" ", "_")
    key = f"submissions/{date_str}_{dog_clean}_{location}.csv"

    _s3_client.put_object(
        Bucket=AWS_BUCKET_NAME,
        Key=key,
        Body=df.to_csv(index=False),
        ContentType="text/csv"
    )

    return f"s3://{AWS_BUCKET_NAME}/{key}"