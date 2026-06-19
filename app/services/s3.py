import boto3
import uuid
from app.core.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME

s3_client = boto3.client("s3", region_name = AWS_REGION, aws_access_key_id = AWS_ACCESS_KEY_ID, aws_secret_access_key = AWS_SECRET_ACCESS_KEY)

def generate_upload_url(listing_id: str, content_type: str):
    file_key = (f"listings/{listing_id}/"f"{uuid.uuid4()}")

    upload_url = s3_client.generate_presigned_url(
        ClientMethod = "put_object",
        Params = {
            "Bucket": S3_BUCKET_NAME,
            "Key": file_key,
            "ContentType": content_type
        },
        ExpiresIn = 300
    )

    return {
        "upload_url": upload_url,
        "file_key": file_key
    }
