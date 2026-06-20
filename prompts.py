from models import PathfinderIntake


def format_answers(answers: dict) -> str:
    lines = []

    for key, value in answers.items():
        if isinstance(value, list):
            formatted_value = ", ".join(value)
        else:
            formatted_value = str(value)

        lines.append(f"{key}: {formatted_value}")

    return "\n".join(lines)


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

If the user mentions wanting to own a business, work for themselves, freelance, consult, or become self-employed, ask follow-up questions that clarify:

- what type of business they imagine
- whether they want to sell a service, product, or expertise
- what business skills they already have
- what parts of business ownership they want to avoid
- whether they need income stability before pursuing self-employment

User responses:

User answers:
{format_answers(intake.answers)}

Resume text, if provided:
{intake.resumeText}

Follow-up clarification responses:
{intake.followUpResponses}
"""


def build_report_prompt(intake: PathfinderIntake) -> str:
    return f"""
You are an expert career transition strategist.

Your task is to create a practical Career Pathfinder Report for someone who may not know what they want to do next.

Use the user's answers and resume, if provided, to infer:
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

If the user's long-term goal involves self-employment, business ownership, entrepreneurship, freelancing, consulting, or running their own business:

- Do not treat self-employment as a reason to avoid career recommendations.
- Recommend roles that can act as stepping stones toward business ownership.
- Focus on jobs that build critical business skills such as sales, customer acquisition, operations, project management, budgeting, client communication, leadership, marketing, estimating, scheduling, and service delivery.
- Explain how each recommended role could prepare the user for future self-employment.
- Include business-readiness gaps the user should close before becoming self-employed.
- Avoid implying that they should immediately start a business unless their background clearly supports it.

If resume text is provided:
- use it to infer current/recent experience
- pull out transferable skills from past roles
- compare resume evidence against the user's self-assessment
- do not ask the user to repeat information that is already clear from the resume
- still prioritize the user's stated energizers, drains, and preferences over resume history alone

User answers:
{format_answers(intake.answers)}

Resume text, if provided:
{intake.resumeText}

Follow-up clarification responses:
{intake.followUpResponses}

Return 2 to 5 career recommendations. If the user’s stated goal is business ownership, include stepping-stone roles that build the skills, industry exposure, and confidence needed for successful self-employment."""


def build_candidate_summary(intake: PathfinderIntake) -> str:
    return f"""
User answers:
{format_answers(intake.answers)}

Resume text, if provided:
{intake.resumeText}

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

If the user's long-term goal involves self-employment, entrepreneurship, consulting, freelancing, or business ownership:

- Score jobs higher when they build business-owner skills.
- Valuable stepping-stone skills include sales, customer acquisition, operations, budgeting, estimating, project management, scheduling, client communication, leadership, marketing, and service delivery.
- Do not penalize a job just because it is not the user's final long-term goal.
- Penalize jobs that are dead-end, overly narrow, or unlikely to build useful business experience.
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
  "educationLevel": "",
  "location": ""
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
- If a city/state is clearly shown near the candidate name, contact information, or most recent experience, return it as location.

Resume text:
{resume_text}
"""
