"""
Cloudinary upload/delete utilities.
Replaces the previous S3 implementation.
"""
import os
import cloudinary
import cloudinary.uploader

# Allowed MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/webm",
    "video/quicktime",
}

ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES

MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100 MB


def _configure_cloudinary():
    """Configure cloudinary from env vars. Raises if credentials missing."""
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise RuntimeError(
            "Cloudinary credentials not configured. "
            "Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, "
            "CLOUDINARY_API_SECRET in .env"
        )

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )


def validate_file(file_storage):
    """
    Validate file type and size.
    Returns (is_valid: bool, error: str | None, file_type: 'image'|'video'|None)
    """
    content_type = (file_storage.content_type or "").lower().split(";")[0].strip()

    if content_type not in ALLOWED_TYPES:
        allowed = ", ".join(sorted(ALLOWED_TYPES))
        return False, f"File type '{content_type}' not allowed. Allowed: {allowed}", None

    # Check file size without loading into memory
    file_storage.stream.seek(0, 2)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)

    is_image = content_type in ALLOWED_IMAGE_TYPES
    is_video = content_type in ALLOWED_VIDEO_TYPES

    if is_image and size > MAX_IMAGE_SIZE:
        return False, f"Image too large ({size // (1024*1024)}MB). Max is 10MB.", None

    if is_video and size > MAX_VIDEO_SIZE:
        return False, f"Video too large ({size // (1024*1024)}MB). Max is 100MB.", None

    return True, None, "image" if is_image else "video"


def upload_file_to_cloudinary(file_storage, folder="media"):
    """
    Upload a single FileStorage object to Cloudinary.
    Returns dict: { url, public_id, type, name }
    Raises ValueError on validation failure, RuntimeError on upload failure.
    """
    is_valid, error, file_type = validate_file(file_storage)
    if not is_valid:
        raise ValueError(error)

    _configure_cloudinary()

    content_type = (file_storage.content_type or "").lower().split(";")[0].strip()
    resource_type = "video" if file_type == "video" else "image"

    file_storage.stream.seek(0)
    try:
        result = cloudinary.uploader.upload(
            file_storage.stream,
            folder=f"glass-bottle/{folder}",
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
        )
    except Exception as e:
        raise RuntimeError(f"Cloudinary upload failed: {str(e)}")

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "type": file_type,
        "name": file_storage.filename,
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
        "bytes": result.get("bytes"),
    }


def upload_multiple_files_to_cloudinary(files, folder="media"):
    """
    Upload a list of FileStorage objects.
    Validates all first, then uploads.
    Returns list of result dicts.
    """
    # Validate all before uploading any
    for f in files:
        is_valid, error, _ = validate_file(f)
        if not is_valid:
            raise ValueError(f"'{f.filename}': {error}")

    results = []
    for f in files:
        result = upload_file_to_cloudinary(f, folder=folder)
        results.append(result)

    return results


def delete_file_from_cloudinary(public_id, resource_type="image"):
    """
    Delete a file from Cloudinary by its public_id.
    Returns True on success, False on failure.
    """
    if not public_id:
        return False
    try:
        _configure_cloudinary()
        cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return True
    except Exception:
        return False


# Keep this alias so the existing admin_extended_routes upload call doesn't break
def upload_file_to_s3(file_storage, folder="media"):
    """Alias for backwards compatibility — now uses Cloudinary."""
    result = upload_file_to_cloudinary(file_storage, folder=folder)
    return result["url"]


def delete_file_from_s3(file_url):
    """Alias for backwards compatibility — no-op without public_id."""
    return False
