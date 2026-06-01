from typing import List
from pydantic import BaseModel


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


class JobSearchRequest(BaseModel):
    location: str
    titles: List[str]
    intake: PathfinderIntake


class JobOpportunity(BaseModel):
    title: str
    company: str
    location: str
    salary: str
    description: str
    url: str
    fitScore: int = 0
    fitReason: str = ""
