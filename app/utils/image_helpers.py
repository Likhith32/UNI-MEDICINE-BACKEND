# image_helpers.py placeholder
# app/utils/image_helpers.py

import os
import uuid
from typing import Tuple

from flask import current_app
from werkzeug.utils import secure_filename

# If you want to do resizing/compression later, uncomment these:
# from PIL import Image

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "bmp"}


def allowed_file(filename: str) -> bool:
    """
    Check if a filename has an allowed image extension.
    """
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a secure, unique filename preserving the extension.
    """
    ext = ""
    if "." in original_filename:
        ext = "." + original_filename.rsplit(".", 1)[1].lower()

    uid = uuid.uuid4().hex
    safe = secure_filename(uid)  # mostly redundant but safe
    return safe + ext


def ensure_upload_folder(subfolder: str = "uploads") -> str:
    """
    Ensure an upload folder inside instance_path exists and return its path.
    By default, uses: <instance_path>/<subfolder> (e.g. instance/uploads).
    """
    base_folder = current_app.instance_path
    upload_folder = os.path.join(base_folder, subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def save_uploaded_image(file_storage, subfolder: str = "uploads") -> str:
    """
    Save a Werkzeug FileStorage image to the instance upload folder
    with a unique secure filename.

    Returns the full file path of the saved image.

    Usage:
        file = request.files.get("image")
        file_path = save_uploaded_image(file)
    """
    if file_storage is None or file_storage.filename == "":
        raise ValueError("No file provided")

    if not allowed_file(file_storage.filename):
        raise ValueError("Unsupported file type")

    upload_folder = ensure_upload_folder(subfolder=subfolder)
    unique_name = generate_unique_filename(file_storage.filename)
    file_path = os.path.join(upload_folder, unique_name)

    file_storage.save(file_path)

    # Optional: resize/compress here using Pillow
    # _resize_image_in_place(file_path, max_size=(512, 512))

    return file_path


def delete_file_safely(path: str) -> None:
    """
    Delete a file if it exists, ignore errors.
    """
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        # Log in real app if needed
        pass


# Optional: enable this if you want automatic resizing/compression
# def _resize_image_in_place(path: str, max_size: Tuple[int, int] = (512, 512)) -> None:
#     """
#     Resize image in-place so it is not too large.
#     Useful for saving disk/memory before ML inference.
#     """
#     try:
#         img = Image.open(path)
#         img.thumbnail(max_size)
#         img.save(path)
#     except Exception as e:
#         # Log but don't break the flow
#         print(f"Image resize failed for {path}: {e}")
#         return
