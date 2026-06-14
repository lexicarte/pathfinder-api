from models import PathfinderIntake


def build_follow_up_prompt(intake: PathfinderIntake) -> str:
    return f"""
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

Return 2 to 5 follow-up questions if needed.

The questions should:
- feel conversational
- be specific
- uncover missing information
- not repeat questions already asked

If the resume provides enough detail about current or recent experience, do not ask the user to restate their job history. Focus follow-up questions on motivations, preferences, energy drains, and unclear contradictions.

User responses:

Resume text, if provided:
{intake.resumeText}

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


def build_report_prompt(intake: PathfinderIntake) -> str:
    return f"""
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

If resume text is provided:
- use it to infer current/recent experience
- pull out transferable skills from past roles
- compare resume evidence against the user's self-assessment
- do not ask the user to repeat information that is already clear from the resume
- still prioritize the user's stated energizers, drains, and preferences over resume history alone

User intake:
Resume text, if provided: {intake.resumeText}
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


def build_candidate_summary(intake: PathfinderIntake) -> str:
    return f"""
Current role / industry:
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

Education / certifications:
{intake.education}

Constraints:
{intake.constraints}

Follow-up responses:
{intake.followUpResponses}
"""


def build_job_relevance_prompt(
        intake: PathfinderIntake,
        jobs: list[dict],
) -> str:
    return f"""
You are evaluating real job openings for a career-change candidate.

Candidate context:
{build_candidate_summary(intake)}

Jobs to evaluate:
{jobs}

Score each job from 1 to 10 based on:
- alignment with the candidate's transferable skills
- realistic accessibility as a bridge role
- whether it avoids known energy drains
- whether it matches the likely career direction
- whether the role seems too advanced, specialized, credential-heavy, or unrelated

Return JSON only:

{{
  "scoredJobs": [
    {{
      "url": "original job url",
      "fitScore": 1,
      "fitReason": "brief explanation"
    }}
  ]
}}

Rules:
- Do not invent jobs.
- Only score jobs from the provided list.
- Match using the original job URL.
- Be strict.
- If a job is unrelated, score it 1 to 3.
- If a job requires credentials the user does not appear to have, score it low.
- Keep fitReason under 30 words.
"""


def build_resume_parse_prompt(resume_text: str) -> str:
    return f"""
Extract basic candidate information from this resume.

Return JSON only.

Required shape:

{{
  "firstName": "",
  "lastName": "",
  "email": "",
  "phone": "",
  "educationLevel": ""
}}

Education level must be one of:
- High School or GED
- Trade School / Certification
- Some College
- Associate Degree
- Bachelor's Degree
- Master's Degree or Higher

Rules:
- If a field is unknown, return an empty string.
- Do not guess contact information.
- For name, use the most likely candidate name at the top of the resume.
- For educationLevel, choose the highest completed level clearly supported by the resume.
- Do not infer a degree from coursework alone.

Resume text:
{resume_text}
"""
