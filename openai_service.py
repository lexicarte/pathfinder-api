import json
from openai import OpenAI

from config import OPENAI_API_KEY
from models import PathfinderIntake
from prompts import (
    build_follow_up_prompt,
    build_report_prompt,
    build_job_relevance_prompt,
)
from schemas import REPORT_SCHEMA

from prompts import (
    build_follow_up_prompt,
    build_report_prompt,
    build_job_relevance_prompt,
    build_resume_parse_prompt,
)

client = OpenAI(api_key=OPENAI_API_KEY)


def check_follow_ups(intake: PathfinderIntake) -> dict:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """
Return JSON only.

{
  "needsFollowUp": true,
  "questions": [
    "question",
    "question"
  ]
}
""",
            },
            {
                "role": "user",
                "content": build_follow_up_prompt(intake),
            },
        ],
    )

    return json.loads(response.choices[0].message.content)


def generate_report(intake: PathfinderIntake) -> dict:
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=build_report_prompt(intake),
        text={
            "format": {
                "type": "json_schema",
                "name": REPORT_SCHEMA["name"],
                "schema": REPORT_SCHEMA["schema"],
                "strict": True,
            }
        },
    )

    return json.loads(response.output_text)


def score_jobs_for_fit(
        intake: PathfinderIntake,
        jobs: list[dict],
) -> dict:
    if not jobs:
        return {"scoredJobs": []}

    compact_jobs = [
        {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "salary": job.get("salary", ""),
            "description": job.get("description", "")[:700],
            "url": job.get("url", ""),
        }
        for job in jobs
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": build_job_relevance_prompt(
                    intake,
                    compact_jobs,
                ),
            }
        ],
    )

    return json.loads(response.choices[0].message.content)


def parse_resume(resume_text: str) -> dict:
    if not resume_text.strip():
        return {
            "firstName": "",
            "lastName": "",
            "email": "",
            "phone": "",
            "educationLevel": "",
        }

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": build_resume_parse_prompt(resume_text),
            }
        ],
    )

    return json.loads(response.choices[0].message.content)
