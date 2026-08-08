"""
Upload Routes (Cloudinary)

POST   /api/admin/upload                  - Upload single image or video
POST   /api/admin/upload/multiple         - Upload up to 10 files
DELETE /api/admin/upload                  - Delete file from Cloudinary + DB
GET    /api/admin/media                   - List all uploaded media (paginated, filterable)
GET    /api/admin/media/<media_id>        - Get single media record
GET    /api/admin/upload/allowed-types    - Allowed types & size limits

Folder options: products | homepage | media | reviews | categories
All routes require admin JWT.
"""
from flask import Blueprint, request, jsonify, current_app
from bson.objectid import ObjectId
from datetime import datetime
from app.utils.auth import admin_required, objectid_to_string
from app.utils.cloudinary_utils import (
    upload_file_to_cloudinary,
    upload_multiple_files_to_cloudinary,
    delete_file_from_cloudinary,
    validate_file,
    ALLOWED_IMAGE_TYPES,
    ALLOWED_VIDEO_TYPES,
)

upload_bp = Blueprint("upload", __name__, url_prefix="/api/admin")

VALID_FOLDERS = {"products", "homepage", "media", "reviews", "categories"}


def _resolve_folder(requested):
    folder = (requested or "media").strip().lower()
    return folder if folder in VALID_FOLDERS else "media"


def _save_media_record(db, result, folder, user_id):
    """
    Persist an upload record to the media collection.
    Returns the inserted document dict (with id field).
    Raises on failure — callers decide whether to abort.
    """
    doc = {
        "_id": ObjectId(),
        "name": result.get("name") or "",
        "url": result.get("url"),
        "public_id": result.get("public_id"),
        "type": result.get("type"),          # 'image' or 'video'
        "format": result.get("format"),      # 'jpg', 'mp4', etc.
        "bytes": result.get("bytes"),
        "width": result.get("width"),
        "height": result.get("height"),
        "folder": folder,
        "uploaded_by": user_id,
        "created_at": datetime.utcnow(),
    }
    db.media.insert_one(doc)
    return objectid_to_string(doc)


# ---------------------------------------------------------------
# POST /api/admin/upload
# Upload a single image or video.
#
# Form fields:
#   file    (required) multipart file
#   folder  (optional) products | homepage | media | reviews | categories
#
# Response 201:
# {
#   "message": "File uploaded successfully",
#   "media": {
#     "id": "...",
#     "url": "https://res.cloudinary.com/...",
#     "public_id": "glass-bottle/products/abc123",
#     "type": "image",
#     "name": "bottle.jpg",
#     "format": "jpg",
#     "width": 1200,
#     "height": 800,
#     "bytes": 204800,
#     "folder": "products",
#     "created_at": "..."
#   }
# }
# ---------------------------------------------------------------
@upload_bp.route("/upload", methods=["POST"])
@admin_required
def upload_single(user_id, user_role):
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'file'."}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Empty file received"}), 400

    folder = _resolve_folder(request.form.get("folder"))

    is_valid, error, _ = validate_file(file)
    if not is_valid:
        return jsonify({"error": error}), 422

    try:
        result = upload_file_to_cloudinary(file, folder=folder)
    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 500

    try:
        media_doc = _save_media_record(current_app.mongo.db, result, folder, user_id)
    except Exception as e:
        # Cloudinary upload succeeded but DB write failed — return url anyway
        # with a warning so the client isn't left hanging
        return jsonify({
            "message": "File uploaded but DB record failed",
            "warning": str(e),
            "url": result.get("url"),
            "public_id": result.get("public_id"),
        }), 201

    return jsonify({
        "message": "File uploaded successfully",
        "media": media_doc,
    }), 201


# ---------------------------------------------------------------
# POST /api/admin/upload/multiple
# Upload up to 10 files at once.
#
# Form fields:
#   files[]  (required) one or more files
#   folder   (optional)
#
# Response 201:
# {
#   "message": "3 file(s) uploaded successfully",
#   "media": [ { "id": "...", "url": "...", "public_id": "...", ... } ],
#   "folder": "products"
# }
# ---------------------------------------------------------------
@upload_bp.route("/upload/multiple", methods=["POST"])
@admin_required
def upload_multiple(user_id, user_role):
    files = request.files.getlist("files[]")
    if not files or all(not f.filename for f in files):
        return jsonify({"error": "No files provided. Use field name 'files[]'."}), 400

    if len(files) > 10:
        return jsonify({"error": "Maximum 10 files per request"}), 422

    folder = _resolve_folder(request.form.get("folder"))

    for f in files:
        is_valid, error, _ = validate_file(f)
        if not is_valid:
            return jsonify({"error": f"'{f.filename}': {error}"}), 422

    try:
        results = upload_multiple_files_to_cloudinary(files, folder=folder)
    except (ValueError, RuntimeError) as e:
        return jsonify({"error": str(e)}), 500

    db = current_app.mongo.db
    saved = []
    errors = []
    for r in results:
        try:
            doc = _save_media_record(db, r, folder, user_id)
            saved.append(doc)
        except Exception as e:
            # Still include the URL even if DB write fails
            errors.append({"url": r.get("url"), "error": str(e)})

    response = {
        "message": f"{len(saved)} file(s) uploaded and saved successfully",
        "media": saved,
        "folder": folder,
    }
    if errors:
        response["db_errors"] = errors

    return jsonify(response), 201


# ---------------------------------------------------------------
# DELETE /api/admin/upload
# Delete from Cloudinary AND remove the DB record.
#
# Request body:
#   { "public_id": "glass-bottle/products/abc123", "resource_type": "image" }
#   resource_type defaults to "image". Use "video" for videos.
#
# Response 200: { "message": "File deleted successfully" }
# Response 404: { "error": "File not found or already deleted" }
# ---------------------------------------------------------------
@upload_bp.route("/upload", methods=["DELETE"])
@admin_required
def delete_upload(user_id, user_role):
    data = request.get_json() or {}
    public_id = data.get("public_id", "").strip()
    resource_type = data.get("resource_type", "image").strip()

    if not public_id:
        return jsonify({"error": "'public_id' is required in request body"}), 400

    if resource_type not in ("image", "video", "raw"):
        resource_type = "image"

    deleted = delete_file_from_cloudinary(public_id, resource_type=resource_type)
    if not deleted:
        return jsonify({"error": "File not found or already deleted from Cloudinary"}), 404

    current_app.mongo.db.media.delete_one({"public_id": public_id})

    return jsonify({"message": "File deleted successfully"}), 200


# ---------------------------------------------------------------
# GET /api/admin/media
# List all media records stored in DB, paginated and filterable.
#
# Query params:
#   page     (default 1)
#   limit    (default 20, max 100)
#   folder   filter by folder (products | homepage | media | ...)
#   type     filter by type: image | video
#
# Response 200:
# {
#   "media": [ { "id": "...", "url": "...", "name": "...", "type": "image",
#                "folder": "products", "bytes": 204800, "created_at": "..." } ],
#   "pagination": { "current_page": 1, "limit": 20, "total_count": 45, "total_pages": 3 }
# }
# ---------------------------------------------------------------
@upload_bp.route("/media", methods=["GET"])
@admin_required
def list_media(user_id, user_role):
    db = current_app.mongo.db

    page = max(1, request.args.get("page", 1, type=int))
    limit = min(max(1, request.args.get("limit", 20, type=int)), 100)
    folder_filter = request.args.get("folder", "").strip().lower()
    type_filter = request.args.get("type", "").strip().lower()

    query = {}
    if folder_filter and folder_filter in VALID_FOLDERS:
        query["folder"] = folder_filter
    if type_filter in ("image", "video"):
        query["type"] = type_filter

    total_count = db.media.count_documents(query)
    skip = (page - 1) * limit
    docs = list(db.media.find(query).sort("created_at", -1).skip(skip).limit(limit))

    return jsonify({
        "media": [objectid_to_string(d) for d in docs],
        "pagination": {
            "current_page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": max(1, (total_count + limit - 1) // limit),
        },
    }), 200


# ---------------------------------------------------------------
# GET /api/admin/media/<media_id>
# Get a single media record by its DB id.
#
# Response 200: { "id": "...", "url": "...", "public_id": "...", ... }
# Response 404: { "error": "Media not found" }
# ---------------------------------------------------------------
@upload_bp.route("/media/<media_id>", methods=["GET"])
@admin_required
def get_media(media_id, user_id, user_role):
    if not ObjectId.is_valid(media_id):
        return jsonify({"error": "Invalid media ID"}), 400

    doc = current_app.mongo.db.media.find_one({"_id": ObjectId(media_id)})
    if not doc:
        return jsonify({"error": "Media not found"}), 404

    return jsonify(objectid_to_string(doc)), 200


# ---------------------------------------------------------------
# GET /api/admin/upload/allowed-types
# Returns allowed MIME types and size limits for frontend validation.
# ---------------------------------------------------------------
@upload_bp.route("/upload/allowed-types", methods=["GET"])
@admin_required
def allowed_types(user_id, user_role):
    return jsonify({
        "images": {
            "mime_types": sorted(ALLOWED_IMAGE_TYPES),
            "max_size_mb": 10,
        },
        "videos": {
            "mime_types": sorted(ALLOWED_VIDEO_TYPES),
            "max_size_mb": 100,
        },
        "folders": sorted(VALID_FOLDERS),
    }), 200
