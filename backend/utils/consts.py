from re import A
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
# Constants

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME = os.getenv("BUCKET_NAME")