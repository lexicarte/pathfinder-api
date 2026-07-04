from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)

from models import PdfRequest

BRAND_GREEN = "#7F947B"
DARK_TEXT = "#2F3430"
MUTED_TEXT = "#6B716A"
REPORT_TITLE = "Personal Pathfinder"
REPORT_SUBTITLE = "TRANSITIONAL CAREERS"


def build_styles():
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=30,
            leading=34,
            textColor=HexColor(DARK_TEXT),
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=14,
            textColor=HexColor(BRAND_GREEN),
            spaceAfter=16,
        ),
        "section": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=HexColor(BRAND_GREEN),
            spaceBefore=20,
            spaceAfter=10,
        ),
        "card_title": ParagraphStyle(
            "CardTitle",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=HexColor(DARK_TEXT),
            spaceBefore=10,
            spaceAfter=8,
        ),
        "subheading": ParagraphStyle(
            "Subheading",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=HexColor(DARK_TEXT),
            spaceBefore=8,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            textColor=HexColor(DARK_TEXT),
            spaceAfter=8,
        ),
        "muted": ParagraphStyle(
            "Muted",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=HexColor(MUTED_TEXT),
            spaceAfter=8,
        ),
    }


def add_header(story, request: PdfRequest, styles):
    story.append(Paragraph(REPORT_TITLE, styles["title"]))
    story.append(Paragraph(REPORT_SUBTITLE, styles["subtitle"]))

    if request.clientInfo:
        name = f"{request.clientInfo.firstName} {request.clientInfo.lastName}".strip()

        if name:
            story.append(Paragraph(f"Curated for {name}", styles["muted"]))

        contact = " | ".join(
            item
            for item in [
                request.clientInfo.email,
                request.clientInfo.phone,
            ]
            if item
        )

        if contact:
            story.append(Paragraph(contact, styles["muted"]))

    story.append(Spacer(1, 18))


def add_section(story, title: str, styles):
    story.append(Paragraph(title.upper(), styles["section"]))


def add_paragraph(story, text: str, styles):
    if text:
        story.append(Paragraph(text, styles["body"]))


def add_bullets(story, items: list[str], styles):
    for item in items:
        story.append(Paragraph(f"&#8226;&nbsp;&nbsp;{item}", styles["body"]))


def build_pdf(request: PdfRequest) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = build_styles()
    story = []

    add_header(story, request, styles)

    add_section(story, "Client Snapshot", styles)
    add_paragraph(story, request.report.clientSnapshot, styles)

    add_section(story, "Strengths & Patterns", styles)
    add_bullets(story, request.report.strengthsAndPatterns, styles)

    add_section(story, "Transferable Skills", styles)
    add_bullets(story, request.report.transferableSkills, styles)

    add_section(story, "Career Recommendations", styles)

    for index, career in enumerate(request.report.careerRecommendations, start=1):
        story.append(
            Paragraph(
                f"{index}. {career.title}",
                styles["card_title"],
            )
        )

        add_paragraph(story, career.fitSummary, styles)

        story.append(Paragraph("Why It Fits", styles["subheading"]))
        add_bullets(story, career.whyItFits, styles)

        story.append(Paragraph("Bridge Roles", styles["subheading"]))
        add_bullets(story, career.bridgeRoles, styles)

        story.append(Paragraph("Skills To Build", styles["subheading"]))
        add_bullets(story, career.skillsToBuild, styles)

        story.append(Paragraph("Possible Job Titles", styles["subheading"]))
        add_bullets(story, career.possibleJobTitles, styles)

        add_paragraph(
            story,
            f"<b>Transition Difficulty:</b> {career.transitionDifficulty}",
            styles,
        )

        story.append(Spacer(1, 10))

    add_section(story, "Resume Positioning Keywords", styles)
    add_bullets(story, request.report.resumePositioningKeywords, styles)

    add_section(story, "Watch Outs", styles)
    add_bullets(story, request.report.watchOuts, styles)

    add_section(story, "Recommended Next Steps", styles)
    add_bullets(story, request.report.recommendedNextSteps, styles)

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
