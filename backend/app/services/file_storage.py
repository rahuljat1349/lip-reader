import os
import shutil
import uuid
from pathlib import Path

from app.config import settings


def create_job_dir() -> tuple[str, str]:
    job_id = uuid.uuid4().hex[:12]
    job_dir = os.path.join(settings.upload_dir, job_id)
    frames_dir = os.path.join(job_dir, "frames")
    mouth_dir = os.path.join(job_dir, "mouth")
    os.makedirs(frames_dir, exist_ok=True)
    os.makedirs(mouth_dir, exist_ok=True)
    return job_id, job_dir


def save_upload(file_bytes: bytes, job_dir: str, filename: str) -> str:
    ext = Path(filename).suffix
    dest = os.path.join(job_dir, f"input{ext}")
    with open(dest, "wb") as f:
        f.write(file_bytes)
    return dest


def cleanup_job_dir(job_dir: str) -> None:
    if os.path.exists(job_dir):
        shutil.rmtree(job_dir, ignore_errors=True)
