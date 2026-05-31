import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel
import requests
from typing import List

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not os.getenv("ADZUNA_APP_ID"):
    raise Exception("Missing ADZUNA_APP_ID")

if not os.getenv("ADZUNA_APP_KEY"):
    raise Exception("Missing ADZUNA_APP_KEY")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PathfinderIntake(BaseModel):
    currentRole: str
    naturalStrengths: str
    workPreference: str
    drainsEnergy: str
    energizingWork: str
    workToAvoid: str
    education: str
    constraints: str
    followUpResponses: str = ""


class FollowUpResponse(BaseModel):
    needsFollowUp: bool
    questions: list[str]


class JobSearchRequest(BaseModel):
    location: str
    titles: List[str]


class JobOpportunity(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    description: str
    url: str


class JobSearchResponse(BaseModel):
    roles: List[JobOpportunity]


def _format_salary(job: dict) -> str:
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if salary_min and salary_max:
        return f"${salary_min:,.0f} - ${salary_max:,.0f}"

    if salary_min:
        return f"From ${salary_min:,.0f}"

    if salary_max:
        return f"Up to ${salary_max:,.0f}"

    return "Not listed"


REPORT_SCHEMA = {
    "name": "pathfinder_report",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "clientSnapshot": {"type": "string"},
            "strengthsAndPatterns": {
                "type": "array",
                "items": {"type": "string"},
            },
            "transferableSkills": {
                "type": "array",
                "items": {"type": "string"},
            },
            "careerRecommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "fitSummary": {"type": "string"},
                        "whyItFits": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "bridgeRoles": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "skillsToBuild": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "possibleJobTitles": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "transitionDifficulty": {"type": "string"},
                    },
                    "required": [
                        "title",
                        "fitSummary",
                        "whyItFits",
                        "bridgeRoles",
                        "skillsToBuild",
                        "possibleJobTitles",
                        "transitionDifficulty",
                    ],
                },
            },
            "resumePositioningKeywords": {
                "type": "array",
                "items": {"type": "string"},
            },
            "watchOuts": {
                "type": "array",
                "items": {"type": "string"},
            },
            "followUpQuestions": {
                "type": "array",
                "items": {"type": "string"},
            },
            "recommendedNextSteps": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
        "required": [
            "clientSnapshot",
            "strengthsAndPatterns",
            "transferableSkills",
            "careerRecommendations",
            "resumePositioningKeywords",
            "watchOuts",
            "followUpQuestions",
            "recommendedNextSteps",
        ],
    },
}


@app.post("/check-follow-ups")
def check_follow_ups(intake: PathfinderIntake):
    prompt = f"""
You are an expert career coach conducting a discovery conversation.

Review the user's answers.

Determine whether you have enough information to confidently recommend career paths.

Look for:

- vague answers
- contradictory answers
- missing motivations
- unclear strengths
- unclear dislikes
- unclear work preferences

Be skeptical.

If any answer is generic, short, abstract, or could apply to almost anyone, ask a follow-up.

Generic answers include:
- "helping people"
- "working with people"
- "stress"
- "bad jobs"
- "depends"
- "communication"
- "problem solving"
- "teamwork"
- "leadership"
- "flexible"

When in doubt, ask follow-up questions.

Only return needsFollowUp false if the user's answers include specific examples, clear preferences, and enough context to distinguish between multiple career paths.

If more information would materially improve the career recommendations:

Return 2 to 5 follow-up questions.

The questions should:
- feel conversational
- be specific
- uncover missing information
- not repeat questions already asked

If the information is already sufficient:

Return no questions.

User responses:

Current role:
{intake.currentRole}

Natural strengths:
{intake.naturalStrengths}

Preferred work style:
{intake.workPreference}

Draining work:
{intake.drainsEnergy}

Energizing work:
{intake.energizingWork}

Work to avoid:
{intake.workToAvoid}

Education:
{intake.education}

Constraints:
{intake.constraints}
"""

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
"""
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return json.loads(
        response.choices[0].message.content
    )


@app.post("/generate-report")
def generate_report(intake: PathfinderIntake):
    prompt = f"""
You are an expert career transition strategist.

Your task is to create a practical Career Pathfinder Report for someone who may not know what they want to do next.

Use the user's answers to infer:
- transferable skills
- energizing work patterns
- draining work patterns
- realistic career paths
- bridge roles
- skill gaps
- resume positioning keywords
- follow-up questions that would improve the recommendation

Do not overpromise.
Do not recommend paths that obviously conflict with what drains the user.
Do not assume the user wants to go back to school unless necessary.
Prefer realistic bridge roles over dramatic career pivots.

Do not present recommendations as certain conclusions.

If the user's answers are vague, limited, or incomplete:
- avoid highly specific career paths unless clearly supported
- identify what information is missing
- let the user know that their career coach will walk them through each step

Prefer realistic categories and bridge roles over overly specific titles.

Bad example:
"UX Researcher is a strong fit."

Better example:
"Research-adjacent roles may be worth exploring if the user enjoys interviewing people, analyzing patterns, and translating insights into recommendations. More information is needed before treating this as a primary target."

User intake:
Current role / industry: {intake.currentRole}
Natural strengths: {intake.naturalStrengths}
Preferred work style: {intake.workPreference}
Draining tasks / environments: {intake.drainsEnergy}
Energizing work: {intake.energizingWork}
Work to avoid: {intake.workToAvoid}
Education / certifications: {intake.education}
Constraints: {intake.constraints}
Follow-up clarification responses: {intake.followUpResponses}

Return 2 to 5 career recommendations. If the input is thin, keep them broad and exploratory.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
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


@app.post("/search-jobs")
def search_jobs(request: JobSearchRequest):
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise Exception("Missing Adzuna credentials")

    collected_jobs = []
    seen_urls = set()

    for title in request.titles[:6]:
        response = requests.get(
            "https://api.adzuna.com/v1/api/jobs/us/search/1",
            params={
                "app_id": app_id,
                "app_key": app_key,
                "results_per_page": 5,
                "what": title,
                "where": request.location,
                "sort_by": "date",
                "content-type": "application/json",
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        for job in data.get("results", []):
            url = job.get("redirect_url", "")

            if not url or url in seen_urls:
                continue

            seen_urls.add(url)

            company = job.get("company", {}).get("display_name", "Not listed")
            location = job.get("location", {}).get("display_name", request.location)

            collected_jobs.append(
                {
                    "title": job.get("title", ""),
                    "company": company,
                    "location": location,
                    "salary": _format_salary(job),
                    "description": job.get("description", ""),
                    "url": url,
                }
            )

            if len(collected_jobs) >= 10:
                break

        if len(collected_jobs) >= 10:
            break

    return {"roles": collected_jobs}
