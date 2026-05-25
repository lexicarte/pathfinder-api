import json
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

User intake:
Current role / industry: {intake.currentRole}
Natural strengths: {intake.naturalStrengths}
Preferred work style: {intake.workPreference}
Draining tasks / environments: {intake.drainsEnergy}
Energizing work: {intake.energizingWork}
Work to avoid: {intake.workToAvoid}
Education / certifications: {intake.education}
Constraints: {intake.constraints}

Return 3 to 5 career recommendations.
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
