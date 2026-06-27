from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)

from models import PdfRequest


def add_heading(story, text, styles):
    story.append(Paragraph(text, styles["Heading1"]))
    story.append(Spacer(1, 8))


def add_paragraph(story, text, styles):
    if text:
        story.append(Paragraph(text, styles["BodyText"]))
        story.append(Spacer(1, 10))


def add_bullets(story, items, styles):
    for item in items:
        story.append(Paragraph(f"• {item}", styles["BodyText"]))
        story.append(Spacer(1, 5))

    story.append(Spacer(1, 8))


def build_pdf(request: PdfRequest) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Career Pathfinder Report", styles["Title"]))
    story.append(Spacer(1, 14))

    if request.clientInfo:
        name = f"{request.clientInfo.firstName} {request.clientInfo.lastName}".strip()
        if name:
            story.append(Paragraph(name, styles["Heading2"]))

        if request.clientInfo.email:
            story.append(Paragraph(request.clientInfo.email, styles["BodyText"]))

        if request.clientInfo.phone:
            story.append(Paragraph(request.clientInfo.phone, styles["BodyText"]))

        story.append(Spacer(1, 16))

    add_heading(story, "Client Snapshot", styles)
    add_paragraph(story, request.report.clientSnapshot, styles)

    add_heading(story, "Strengths & Patterns", styles)
    add_bullets(story, request.report.strengthsAndPatterns, styles)

    add_heading(story, "Transferable Skills", styles)
    add_bullets(story, request.report.transferableSkills, styles)

    add_heading(story, "Career Recommendations", styles)

    for index, career in enumerate(request.report.careerRecommendations, start=1):
        story.append(
            Paragraph(
                f"{index}. {career.title}",
                styles["Heading2"],
            )
        )
        story.append(Spacer(1, 6))

        add_paragraph(story, career.fitSummary, styles)

        story.append(Paragraph("Why It Fits", styles["Heading3"]))
        add_bullets(story, career.whyItFits, styles)

        story.append(Paragraph("Bridge Roles", styles["Heading3"]))
        add_bullets(story, career.bridgeRoles, styles)

        story.append(Paragraph("Skills To Build", styles["Heading3"]))
        add_bullets(story, career.skillsToBuild, styles)

        story.append(Paragraph("Possible Job Titles", styles["Heading3"]))
        add_bullets(story, career.possibleJobTitles, styles)

        story.append(
            Paragraph(
                f"Transition Difficulty: {career.transitionDifficulty}",
                styles["BodyText"],
            )
        )
        story.append(Spacer(1, 16))

    add_heading(story, "Resume Positioning Keywords", styles)
    add_bullets(story, request.report.resumePositioningKeywords, styles)

    add_heading(story, "Watch Outs", styles)
    add_bullets(story, request.report.watchOuts, styles)

    add_heading(story, "Recommended Next Steps", styles)
    add_bullets(story, request.report.recommendedNextSteps, styles)

    story.append(PageBreak())

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
