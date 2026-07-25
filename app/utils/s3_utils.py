import os
from datetime import datetime
from uuid import uuid4

try:
    import boto3
except ImportError:  # pragma: no cover
    boto3 = None


def upload_file_to_s3(file_storage, folder="uploads"):
    """Upload a file-like object to S3 and return a public URL."""
    if boto3 is None:
        raise RuntimeError("boto3 is not installed")

    bucket = os.getenv("AWS_S3_BUCKET")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket or not access_key or not secret_key:
        raise RuntimeError("S3 credentials are not configured")

    filename = file_storage.filename or "file"
    extension = os.path.splitext(filename)[1]
    key = f"{folder}/{datetime.utcnow().strftime('%Y/%m/%d')}/{uuid4().hex}{extension}"

    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    file_storage.stream.seek(0)
    s3.upload_fileobj(file_storage, bucket, key, ExtraArgs={"ContentType": file_storage.content_type or "application/octet-stream"})

    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def delete_file_from_s3(file_url):
    """Delete a file from S3 using its public URL."""
    if not file_url or boto3 is None:
        return False

    bucket = os.getenv("AWS_S3_BUCKET")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket or not access_key or not secret_key:
        return False

    key = file_url.split(f"{bucket}.s3.{region}.amazonaws.com/", 1)[1]
    s3 = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    s3.delete_object(Bucket=bucket, Key=key)
    return True
