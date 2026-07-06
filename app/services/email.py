import boto3

from app.core.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
)

ses = boto3.client(
    "ses",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

FROM_EMAIL = "noreply@kumudrajghimire.com.np"


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
):
    ses.send_email(
        Source=FROM_EMAIL,
        Destination={
            "ToAddresses": [to_email],
        },
        Message={
            "Subject": {
                "Data": subject,
            },
            "Body": {
                "Text": {
                    "Data": text_body,
                },
                "Html": {
                    "Data": html_body,
                },
            },
        },
    )