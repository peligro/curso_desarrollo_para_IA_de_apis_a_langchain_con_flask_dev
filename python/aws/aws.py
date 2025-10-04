import boto3
from dotenv import load_dotenv
load_dotenv()
import os


def get_conection():
    if os.getenv('ENVIRONMENT')=="local":
        s3_client = boto3.client(
            "s3",
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            endpoint_url=os.getenv('AWS_SECRET_ACCESS_URL')
        )
    else:
        s3_client = boto3.client(
            "s3",
            region_name=os.getenv('AWS_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
    return s3_client