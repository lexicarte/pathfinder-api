from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import (JobSearchRequest, PathfinderIntake, ResumeParseRequest, ParsedResume)
from openai_service import check_follow_ups, generate_report, parse_resume
from jobs_service import search_jobs

from fastapi.responses import Response
from models import PdfRequest
from pdf_service import build_pdf

from fastapi import UploadFile, File
from docx import Document
from pypdf import PdfReader
from io import BytesIO

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/check-follow-ups")
def check_follow_ups_endpoint(intake: PathfinderIntake):
    return check_follow_ups(intake)


@app.post("/generate-report")
def generate_report_endpoint(intake: PathfinderIntake):
    return generate_report(intake)


@app.post("/search-jobs")
def search_jobs_endpoint(request: JobSearchRequest):
    return search_jobs(request)


@app.post(
    "/parse-resume",
    response_model=ParsedResume,
)
def parse_resume_endpoint(
        request: ResumeParseRequest,
):
    return parse_resume(
        request.resumeText,
    )


@app.post("/generate-pdf")
def generate_pdf_endpoint(request: PdfRequest):
    pdf_bytes = build_pdf(request)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=career_pathfinder_report.pdf"
        },
    )


@app.post("/extract-resume-text")
def extract_resume_text(file: UploadFile = File(...)):
    extension = file.filename.lower().split(".")[-1]

    data = file.file.read()

    if extension == "txt":
        text = data.decode("utf-8", errors="ignore")

    elif extension == "pdf":
        reader = PdfReader(BytesIO(data))
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    elif extension == "docx":
        document = Document(BytesIO(data))
        text = "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        )

    else:
        raise ValueError("Unsupported file type.")

    return {
        "resumeText": text,
    }
