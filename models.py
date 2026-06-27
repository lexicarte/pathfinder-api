from typing import Any, Dict, Optional, List
from pydantic import BaseModel


class ClientInfo(BaseModel):
    firstName: str = ""
    lastName: str = ""
    email: str = ""
    phone: str = ""


class PathfinderIntake(BaseModel):
    resumeText: str = ""
    clientInfo: Optional[ClientInfo] = None
    answers: Dict[str, Any]
    followUpResponses: str = ""
    desiredLocation: str = ""


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
    location: str = ""


class PdfCareerRecommendation(BaseModel):
    title: str
    fitSummary: str
    whyItFits: List[str]
    bridgeRoles: List[str]
    skillsToBuild: List[str]
    possibleJobTitles: List[str]
    transitionDifficulty: str


class PdfReport(BaseModel):
    clientSnapshot: str
    strengthsAndPatterns: List[str]
    transferableSkills: List[str]
    careerRecommendations: List[PdfCareerRecommendation]
    resumePositioningKeywords: List[str]
    watchOuts: List[str]
    followUpQuestions: List[str]
    recommendedNextSteps: List[str]


class PdfRequest(BaseModel):
    clientInfo: Optional[ClientInfo] = None
    report: PdfReport
    jobs: Optional[JobSearchResponse] = None
