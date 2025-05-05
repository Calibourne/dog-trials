from unittest.case import TestCase
from unittest.mock import patch
from backend.utils.s3 import get_s3_client


class TestS3Client(TestCase):
    @patch.dict(
        "os.environ",
        {
            "AWS_ACCESS_KEY_ID": "test_access_key",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "AWS_REGION": "test_region",
            "BUCKET_NAME": "test_bucket",
        })