import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.config import settings
from app.database import get_db
from app.ingest.ingest import ingest_hospital_mrf

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_key: str = Header(default="")):
    if not settings.admin_secret:
        raise HTTPException(status_code=403, detail="Admin access not configured — set ADMIN_SECRET env var")
    if x_admin_key != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Invalid admin key")


@router.post("/ingest/hospital")
async def ingest_hospital_mrf_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Upload and ingest a CMS hospital machine-readable file (.json or .json.gz)."""
    filename = file.filename or ""
    if not (filename.endswith(".json") or filename.endswith(".json.gz")):
        raise HTTPException(status_code=400, detail="File must be .json or .json.gz")

    suffix = ".json.gz" if filename.endswith(".gz") else ".json"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        count = await run_in_threadpool(ingest_hospital_mrf, db, tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"records_ingested": count, "filename": filename}
