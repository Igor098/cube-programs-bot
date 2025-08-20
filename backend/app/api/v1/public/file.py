from fastapi import APIRouter
from fastapi.responses import FileResponse
from pathlib import Path


router = APIRouter(prefix="/v1/files", tags=["Файлы"])

PDF_PATH=Path("./app/files/заявление_it-куб.pdf")

@router.get("/enroll-form")
async def get_enroll_form():
    if not PDF_PATH.exists():
        return {"error": "file not found"}
    return FileResponse(
        PDF_PATH,
        filename="enroll_form.pdf",
        media_type="application/pdf"
    )