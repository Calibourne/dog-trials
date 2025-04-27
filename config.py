from requests import session
from dotenv import load_dotenv
import os
from boto3 import Session
load_dotenv()

dog_names = os.getenv("DOG_NAMES").split(",")
test_structure = os.getenv("TEST_STRUCTURE").split(",")
num_of_trials = int(os.getenv("NUM_OF_TRIALS"))

session = Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)
s3_client = session.client("s3")
bucket_name = os.getenv("BUCKET_NAME")