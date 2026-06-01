import requests

from config import ADZUNA_APP_ID, ADZUNA_APP_KEY
from models import JobSearchRequest
from openai_service import score_jobs_for_fit


def format_salary(job: dict) -> str:
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if salary_min and salary_max:
        return f"${salary_min:,.0f} - ${salary_max:,.0f}"

    if salary_min:
        return f"From ${salary_min:,.0f}"

    if salary_max:
        return f"Up to ${salary_max:,.0f}"

    return "Not listed"


def is_relevant_job(job: dict, search_title: str) -> bool:
    job_title = job.get("title", "").lower()
    description = job.get("description", "").lower()

    search_words = [
        word.lower()
        for word in search_title.split()
        if len(word) > 3
    ]

    if not search_words:
        return False

    title_matches = sum(
        1 for word in search_words if word in job_title
    )

    description_matches = sum(
        1 for word in search_words if word in description
    )

    return title_matches >= 1 or description_matches >= 2


def search_jobs(request: JobSearchRequest) -> dict:
    collected_jobs = []
    seen_urls = set()

    for title in request.titles[:6]:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/us/search/1",
            params={
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": 20,
                "what": f'"{title}"',
                "where": request.location,
                "sort_by": "date",
                "content-type": "application/json",
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        for job in data.get("results", []):
            if not is_relevant_job(job, title):
                continue

            url = job.get("redirect_url", "")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            collected_jobs.append(
                {
                    "title": job.get("title", ""),
                    "company": job.get("company", {}).get(
                        "display_name",
                        "Not listed",
                    ),
                    "location": job.get("location", {}).get(
                        "display_name",
                        request.location,
                    ),
                    "salary": format_salary(job),
                    "description": job.get("description", ""),
                    "url": url,
                }
            )

            if len(collected_jobs) >= 10:
                break

        if len(collected_jobs) >= 10:
            break

    jobs_to_score = collected_jobs[:10]

    scored_response = score_jobs_for_fit(
        request.intake,
        jobs_to_score,
    )

    ranked_jobs = apply_fit_scores(
        jobs_to_score,
        scored_response,
    )

    return {
        "roles": [
                     job for job in ranked_jobs
                     if job.get("fitScore", 0) >= 5
                 ][:8]
    }


def apply_fit_scores(
    jobs: list[dict],
    scored_response: dict,
) -> list[dict]:
    scores_by_url = {
        item.get("url"): item
        for item in scored_response.get("scoredJobs", [])
    }

    scored_jobs = []

    for job in jobs:
        score = scores_by_url.get(job.get("url"))

        if not score:
            continue

        job["fitScore"] = int(score.get("fitScore", 0))
        job["fitReason"] = score.get("fitReason", "")

        scored_jobs.append(job)

    scored_jobs.sort(
        key=lambda item: item.get("fitScore", 0),
        reverse=True,
    )

    return scored_jobs
