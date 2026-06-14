from typing import List
from pydantic import BaseModel


class ClientInfo(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str


class PathfinderIntake(BaseModel):
    clientInfo: ClientInfo
    currentRole: str
    naturalStrengths: str
    workPreference: str
    drainsEnergy: str
    energizingWork: str
    workToAvoid: str
    education: str
    constraints: str
    followUpResponses: str = ""
    resumeText: str = ""


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


class JobSearchResponse(BaseModel):
    strongMatches: List[JobOpportunity]
    exploratoryMatches: List[JobOpportunity]
    message: str


class ResumeParseRequest(BaseModel):
    resumeText: str


class ParsedResume(BaseModel):
    firstName: str = ""
    lastName: str = ""
    email: str = ""
    phone: str = ""
    educationLevel: str = ""
