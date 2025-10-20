from pathlib import Path
from typing import Optional

import aiofiles
from fastapi import HTTPException, UploadFile
from prisma import Prisma

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "text/plain"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
STORAGE_DIR = Path(__file__).resolve().parents[2] / "storage"


async def _ensure_storage_dir() -> None:
  STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _is_allowed_type(upload: UploadFile) -> bool:
  return upload.content_type in ALLOWED_TYPES


async def _scan(upload: UploadFile) -> bool:
  # Placeholder for antivirus integration
  return True


async def save_file(
  upload: UploadFile,
  *,
  uploader_id: str,
  request_id: Optional[str] = None,
  message_id: Optional[str] = None,
) -> dict:
  if not _is_allowed_type(upload):
    raise HTTPException(status_code=400, detail="Unsupported file type")
  await _ensure_storage_dir()
  data = await upload.read()
  if len(data) > MAX_FILE_SIZE:
    raise HTTPException(status_code=400, detail="File too large")
  if not await _scan(upload):
    raise HTTPException(status_code=400, detail="Virus detected")
  file_path = STORAGE_DIR / upload.filename
  async with aiofiles.open(file_path, "wb") as f:
    await f.write(data)

  prisma = Prisma()
  if not prisma.is_connected():
    await prisma.connect()
  try:
    created = await prisma.file.create(
      data={
        "request_id": request_id,
        "message_id": message_id,
        "uploader_id": uploader_id,
        "category": "REQUEST" if request_id else "MESSAGE",
        "path": str(file_path),
        "filename": upload.filename,
        "mime_type": upload.content_type or "application/octet-stream",
        "size_bytes": len(data)
      }
    )
    return {
      "id": created.id,
      "filename": created.filename,
      "url": str(file_path)
    }
  finally:
    await prisma.disconnect()
