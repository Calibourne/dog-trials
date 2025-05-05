from boto3 import Session
from backend.utils.consts import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

_session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_REGION)

_s3_client = _session.client("s3")

def get_s3_client():
    """
    Returns the S3 client.
    """
    return _s3_client