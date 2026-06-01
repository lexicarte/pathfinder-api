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


def build_job_search_message(
    strong_jobs: list[dict],
    exploratory_jobs: list[dict],
) -> str:
    if len(strong_jobs) >= 3:
        return (
            "Several strong local matches were found "
            "based on the recommended career paths."
        )

    if len(strong_jobs) == 1:
        return (
            "One strong local match was found. "
            "Additional exploratory roles may also be worth reviewing."
        )

    if len(strong_jobs) >= 2:
        return (
            "A few strong local matches were found. "
            "Additional exploratory roles may also be worth reviewing."
        )

    if len(exploratory_jobs) >= 1:
        return (
            "No strong matches were found, but a few exploratory roles "
            "may be worth reviewing with your career coach."
        )

    return (
        "No strong local matches were found for these career paths "
        "at this time. Your career coach may be able to identify "
        "available careers that match your skills."
    )


def normalize_job_key(job: dict) -> str:
    title = job.get("title", "").lower().strip()
    company = job.get("company", "").lower().strip()

    title = title.replace("(usa)", "")
    title = title.replace("-", " ")
    title = " ".join(title.split())

    company = company.replace(",", "")
    company = " ".join(company.split())

    return f"{title}|{company}"


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
    seen_job_keys = set()

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

            company = job.get("company", {}).get("display_name", "Not listed")
            location = job.get("location", {}).get("display_name", request.location)

            candidate_job = {
                "title": job.get("title", ""),
                "company": company,
            }

            dedupe_key = normalize_job_key(candidate_job)

            if dedupe_key in seen_job_keys:
                continue

            seen_job_keys.add(dedupe_key)

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

    strong_matches = [
        job
        for job in ranked_jobs
        if job.get("fitScore", 0) >= 7
    ]

    exploratory_matches = [
        job
        for job in ranked_jobs
        if 5 <= job.get("fitScore", 0) < 7
    ]

    return {
        "strongMatches": strong_matches[:5],
        "exploratoryMatches": exploratory_matches[:5],
        "message": build_job_search_message(
            strong_matches,
            exploratory_matches,
        ),
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
