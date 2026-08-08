import os
from datetime import datetime
from uuid import uuid4

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    ClientError = Exception

# Allowed MIME types and their extensions
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
}

ALLOWED_TYPES = {**ALLOWED_IMAGE_TYPES, **ALLOWED_VIDEO_TYPES}

# Max sizes
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


def _get_s3_client():
    """Build and return a boto3 S3 client."""
    if boto3 is None:
        raise RuntimeError("boto3 is not installed. Run: pip install boto3")

    bucket = os.getenv("AWS_S3_BUCKET")
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket or not access_key or not secret_key:
        raise RuntimeError(
            "S3 credentials not configured. Set AWS_S3_BUCKET, "
            "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY in .env"
        )

    client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    return client, bucket, region


def validate_file(file_storage):
    """
    Validate file type and size.
    Returns (is_valid, error_message, file_type)
    file_type is 'image' or 'video'
    """
    content_type = (file_storage.content_type or "").lower()

    if content_type not in ALLOWED_TYPES:
        allowed = ", ".join(ALLOWED_TYPES.keys())
        return False, f"File type '{content_type}' not allowed. Allowed: {allowed}", None

    # Read file to check size, then seek back
    file_storage.stream.seek(0, 2)  # seek to end
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    is_image = content_type in ALLOWED_IMAGE_TYPES
    is_video = content_type in ALLOWED_VIDEO_TYPES

    if is_image and size > MAX_IMAGE_SIZE:
        return False, f"Image too large ({size // (1024*1024)}MB). Max is 10MB.", None

    if is_video and size > MAX_VIDEO_SIZE:
        return False, f"Video too large ({size // (1024*1024)}MB). Max is 100MB.", None

    file_type = "image" if is_image else "video"
    return True, None, file_type


def upload_file_to_s3(file_storage, folder="uploads"):
    """
    Upload a FileStorage object to S3.
    Returns the public URL string.
    Raises RuntimeError on failure.
    """
    is_valid, error, _ = validate_file(file_storage)
    if not is_valid:
        raise ValueError(error)

    client, bucket, region = _get_s3_client()

    content_type = (file_storage.content_type or "application/octet-stream").lower()
    extension = ALLOWED_TYPES.get(content_type, os.path.splitext(file_storage.filename or "")[1])
    date_path = datetime.utcnow().strftime("%Y/%m/%d")
    key = f"{folder}/{date_path}/{uuid4().hex}{extension}"

    file_storage.stream.seek(0)
    try:
        client.upload_fileobj(
            file_storage,
            bucket,
            key,
            ExtraArgs={
                "ContentType": content_type,
                "CacheControl": "max-age=31536000",  # 1 year cache
            },
        )
    except ClientError as e:
        raise RuntimeError(f"S3 upload failed: {str(e)}")

    return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def upload_multiple_files_to_s3(files, folder="uploads"):
    """
    Upload a list of FileStorage objects to S3.
    Returns list of { url, type, name } dicts.
    Raises ValueError on any invalid file before uploading.
    """
    results = []
    # Validate all first before uploading any
    for f in files:
        is_valid, error, _ = validate_file(f)
        if not is_valid:
            raise ValueError(f"File '{f.filename}': {error}")

    for f in files:
        _, _, file_type = validate_file(f)
        url = upload_file_to_s3(f, folder=folder)
        results.append({
            "url": url,
            "type": file_type,
            "name": f.filename,
        })

    return results


def delete_file_from_s3(file_url):
    """
    Delete a file from S3 by its public URL.
    Returns True on success, False on failure/skip.
    """
    if not file_url:
        return False

    try:
        client, bucket, region = _get_s3_client()
        prefix = f"{bucket}.s3.{region}.amazonaws.com/"
        if prefix not in file_url:
            return False
        key = file_url.split(prefix, 1)[1]
        client.delete_object(Bucket=bucket, Key=key)
        return True
    except Exception:
        return False
