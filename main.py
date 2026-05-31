from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import JobSearchRequest, PathfinderIntake
from openai_service import check_follow_ups, generate_report
from jobs_service import search_jobs

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
