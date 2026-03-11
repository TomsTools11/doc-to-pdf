#!/usr/bin/env python3
"""
Document to PDF Converter

Converts various document formats (text, markdown, JSON) into professionally
formatted PDFs with multiple template options.

Usage:
    python generate_pdf.py input.txt -o output.pdf
    python generate_pdf.py input.md -o output.pdf --template report
    python generate_pdf.py content.json -o output.pdf --template memo
    echo "Content" | python generate_pdf.py - -o output.pdf

Templates: default, report, memo, notes, article
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, gray
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
        ListFlowable, ListItem, KeepTogether
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    print("Error: reportlab not installed. Run: pip install reportlab --break-system-packages")
    sys.exit(1)

try:
    import markdown2
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


# ==============================================================================
# STYLES
# ==============================================================================

def get_styles(template="default"):
    """Create paragraph styles for the specified template."""
    styles = getSampleStyleSheet()

    # Base colors
    primary_color = HexColor("#1a1a1a")
    heading_color = HexColor("#2c3e50")
    accent_color = HexColor("#3498db")

    # Common styles
    styles.add(ParagraphStyle(
        name='DocTitle',
        parent=styles['Title'],
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='DocSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        leading=18,
        textColor=gray,
        spaceAfter=24,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='DocHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=heading_color,
        spaceBefore=18,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='DocHeading2',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=heading_color,
        spaceBefore=14,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='DocBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='DocBullet',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=primary_color,
        leftIndent=20,
        spaceAfter=4,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='DocMeta',
        parent=styles['Normal'],
        fontSize=10,
        leading=12,
        textColor=gray,
        spaceAfter=4,
        fontName='Helvetica'
    ))

    styles.add(ParagraphStyle(
        name='DocFooter',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=gray,
        alignment=TA_CENTER,
        fontName='Helvetica'
    ))

    # Template-specific adjustments
    if template == "memo":
        styles['DocTitle'].alignment = TA_LEFT
        styles['DocTitle'].fontSize = 18
    elif template == "article":
        styles['DocBody'].firstLineIndent = 20
    elif template == "notes":
        styles['DocBody'].spaceAfter = 6
        styles['DocBullet'].spaceAfter = 3

    return styles


# ==============================================================================
# CONTENT PARSING
# ==============================================================================

def parse_input(input_path):
    """Parse input file and return structured content."""
    if input_path == "-":
        text = sys.stdin.read()
        return parse_text(text)

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    content = path.read_text(encoding='utf-8')

    if path.suffix == '.json':
        return json.loads(content)
    elif path.suffix == '.md' and HAS_MARKDOWN:
        return parse_markdown(content)
    else:
        return parse_text(content)


def parse_text(text):
    """Parse plain text into structured content."""
    lines = text.strip().split('\n')
    content = {
        "title": "",
        "subtitle": "",
        "author": "",
        "date": datetime.now().strftime("%B %d, %Y"),
        "sections": []
    }

    current_section = {"heading": "", "body": []}

    for i, line in enumerate(lines):
        line = line.strip()

        # First non-empty line is title
        if not content["title"] and line:
            content["title"] = line
            continue

        # Detect headings (lines ending with colon or all caps)
        if line and (line.endswith(':') or (line.isupper() and len(line) > 3)):
            if current_section["body"]:
                content["sections"].append(current_section)
            heading = line.rstrip(':')
            current_section = {"heading": heading, "body": []}
        elif line:
            current_section["body"].append(line)

    if current_section["body"] or current_section["heading"]:
        content["sections"].append(current_section)

    # Extract metadata from content
    content = extract_metadata(content)

    return content


def parse_markdown(text):
    """Parse markdown into structured content."""
    content = {
        "title": "",
        "subtitle": "",
        "author": "",
        "date": datetime.now().strftime("%B %d, %Y"),
        "sections": []
    }

    lines = text.strip().split('\n')
    current_section = {"heading": "", "body": []}
    in_code_block = False

    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            current_section["body"].append(line)
            continue

        if in_code_block:
            current_section["body"].append(line)
            continue

        # H1 heading - treat as title if not set
        if line.startswith('# '):
            if not content["title"]:
                content["title"] = line[2:].strip()
            else:
                if current_section["body"]:
                    content["sections"].append(current_section)
                current_section = {"heading": line[2:].strip(), "body": []}
        # H2+ headings
        elif line.startswith('## '):
            if current_section["body"]:
                content["sections"].append(current_section)
            current_section = {"heading": line[3:].strip(), "body": []}
        elif line.startswith('### '):
            current_section["body"].append(f"**{line[4:].strip()}**")
        else:
            if line.strip():
                current_section["body"].append(line)

    if current_section["body"] or current_section["heading"]:
        content["sections"].append(current_section)

    content = extract_metadata(content)
    return content


def extract_metadata(content):
    """Extract metadata (author, date, etc.) from content."""
    for section in content.get("sections", []):
        body_text = ' '.join(section.get("body", []))

        # Look for author patterns
        author_match = re.search(r'(?:Author|By|Written by)[:\s]+([^\n,]+)', body_text, re.I)
        if author_match and not content["author"]:
            content["author"] = author_match.group(1).strip()

        # Look for date patterns
        date_match = re.search(r'(?:Date|On)[:\s]+(\w+ \d+,? \d{4}|\d{4}-\d{2}-\d{2})', body_text, re.I)
        if date_match:
            content["date"] = date_match.group(1).strip()

    return content


# ==============================================================================
# PDF GENERATION
# ==============================================================================

def create_pdf(content, output_path, template="default", options=None):
    """Generate PDF from structured content."""
    options = options or {}
    styles = get_styles(template)

    # Setup document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1*inch,
        rightMargin=1*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )

    story = []

    # Build based on template
    if template == "report":
        story = build_report(content, styles, options)
    elif template == "memo":
        story = build_memo(content, styles, options)
    elif template == "notes":
        story = build_notes(content, styles, options)
    elif template == "article":
        story = build_article(content, styles, options)
    else:
        story = build_default(content, styles, options)

    # Build PDF
    doc.build(story)
    return output_path


def build_default(content, styles, options):
    """Build default template."""
    story = []

    # Title
    if content.get("title"):
        story.append(Paragraph(content["title"], styles['DocTitle']))

    # Subtitle
    if content.get("subtitle"):
        story.append(Paragraph(content["subtitle"], styles['DocSubtitle']))

    # Meta info
    meta_parts = []
    if content.get("author"):
        meta_parts.append(f"By {content['author']}")
    if content.get("date"):
        meta_parts.append(content["date"])
    if meta_parts:
        story.append(Paragraph(" | ".join(meta_parts), styles['DocMeta']))
        story.append(Spacer(1, 20))

    # Sections
    for section in content.get("sections", []):
        if section.get("heading"):
            story.append(Paragraph(section["heading"], styles['DocHeading1']))

        body = section.get("body", [])
        if isinstance(body, list):
            for para in body:
                story.extend(format_paragraph(para, styles))
        else:
            story.extend(format_paragraph(body, styles))

    return story


def build_report(content, styles, options):
    """Build report template with title page."""
    story = []

    # Title page
    story.append(Spacer(1, 2*inch))
    if content.get("title"):
        story.append(Paragraph(content["title"], styles['DocTitle']))
    if content.get("subtitle"):
        story.append(Paragraph(content["subtitle"], styles['DocSubtitle']))

    story.append(Spacer(1, 1*inch))

    meta_parts = []
    if content.get("author"):
        meta_parts.append(f"Prepared by: {content['author']}")
    if content.get("date"):
        meta_parts.append(content["date"])
    for part in meta_parts:
        story.append(Paragraph(part, styles['DocMeta']))

    story.append(PageBreak())

    # Table of contents placeholder
    if options.get("toc"):
        story.append(Paragraph("Table of Contents", styles['DocHeading1']))
        for i, section in enumerate(content.get("sections", []), 1):
            if section.get("heading"):
                story.append(Paragraph(f"{i}. {section['heading']}", styles['DocBody']))
        story.append(PageBreak())

    # Content sections
    for section in content.get("sections", []):
        if section.get("heading"):
            story.append(Paragraph(section["heading"], styles['DocHeading1']))

        body = section.get("body", [])
        if isinstance(body, list):
            for para in body:
                story.extend(format_paragraph(para, styles))
        else:
            story.extend(format_paragraph(body, styles))

        story.append(Spacer(1, 12))

    return story


def build_memo(content, styles, options):
    """Build memo template."""
    story = []

    # Memo header
    story.append(Paragraph("<b>MEMORANDUM</b>", styles['DocTitle']))
    story.append(Spacer(1, 20))

    # Header fields
    header_data = []
    if content.get("to"):
        header_data.append(["TO:", content["to"]])
    if content.get("from") or content.get("author"):
        header_data.append(["FROM:", content.get("from", content.get("author", ""))])
    if content.get("date"):
        header_data.append(["DATE:", content["date"]])
    if content.get("subject") or content.get("title"):
        header_data.append(["RE:", content.get("subject", content.get("title", ""))])

    if header_data:
        header_table = Table(header_data, colWidths=[1*inch, 5*inch])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)

    # Divider line
    story.append(Spacer(1, 10))
    story.append(Table([['']], colWidths=[6.5*inch], style=[
        ('LINEABOVE', (0, 0), (-1, 0), 1, black),
    ]))
    story.append(Spacer(1, 20))

    # Body
    for section in content.get("sections", []):
        if section.get("heading"):
            story.append(Paragraph(section["heading"], styles['DocHeading2']))

        body = section.get("body", [])
        if isinstance(body, list):
            for para in body:
                story.extend(format_paragraph(para, styles))
        else:
            story.extend(format_paragraph(body, styles))

    return story


def build_notes(content, styles, options):
    """Build meeting notes template."""
    story = []

    # Title
    if content.get("title"):
        story.append(Paragraph(content["title"], styles['DocTitle']))

    # Date
    if content.get("date"):
        story.append(Paragraph(content["date"], styles['DocMeta']))

    story.append(Spacer(1, 10))

    # Attendees
    if content.get("attendees"):
        attendees = content["attendees"]
        if isinstance(attendees, list):
            attendees = ", ".join(attendees)
        story.append(Paragraph(f"<b>Attendees:</b> {attendees}", styles['DocBody']))
        story.append(Spacer(1, 10))

    # Content sections
    for section in content.get("sections", []):
        heading = section.get("heading", "").lower()

        if section.get("heading"):
            story.append(Paragraph(section["heading"], styles['DocHeading1']))

        body = section.get("body", [])
        if isinstance(body, list):
            for para in body:
                story.extend(format_paragraph(para, styles, is_notes=True))
        else:
            story.extend(format_paragraph(body, styles, is_notes=True))

    return story


def build_article(content, styles, options):
    """Build article template."""
    story = []

    # Title
    if content.get("title"):
        story.append(Paragraph(content["title"], styles['DocTitle']))

    # Author and date
    meta_parts = []
    if content.get("author"):
        meta_parts.append(content["author"])
    if content.get("date"):
        meta_parts.append(content["date"])
    if meta_parts:
        story.append(Paragraph(" | ".join(meta_parts), styles['DocMeta']))

    story.append(Spacer(1, 20))

    # Body with article styling
    for section in content.get("sections", []):
        if section.get("heading"):
            story.append(Paragraph(section["heading"], styles['DocHeading1']))

        body = section.get("body", [])
        if isinstance(body, list):
            for para in body:
                story.extend(format_paragraph(para, styles))
        else:
            story.extend(format_paragraph(body, styles))

    return story


def format_paragraph(text, styles, is_notes=False):
    """Format a paragraph, handling bullets and special formatting."""
    elements = []

    if isinstance(text, list):
        for t in text:
            elements.extend(format_paragraph(t, styles, is_notes))
        return elements

    text = str(text).strip()
    if not text:
        return elements

    # Handle bullet points
    if text.startswith(('- ', '* ', '• ')):
        bullet_text = text[2:].strip()
        # Handle checkbox items
        if bullet_text.startswith('[ ]'):
            bullet_text = "☐ " + bullet_text[3:].strip()
        elif bullet_text.startswith('[x]') or bullet_text.startswith('[X]'):
            bullet_text = "☑ " + bullet_text[3:].strip()
        elements.append(Paragraph(f"• {bullet_text}", styles['DocBullet']))

    # Handle numbered items
    elif re.match(r'^\d+[\.\)]\s', text):
        elements.append(Paragraph(text, styles['DocBullet']))

    # Handle bold markdown
    elif text.startswith('**') and text.endswith('**'):
        elements.append(Paragraph(f"<b>{text[2:-2]}</b>", styles['DocBody']))

    # Regular paragraph
    else:
        # Convert basic markdown to reportlab markup
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)
        elements.append(Paragraph(text, styles['DocBody']))

    return elements


# ==============================================================================
# CLI
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Convert documents to professionally formatted PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.txt -o output.pdf
  %(prog)s input.md -o report.pdf --template report
  %(prog)s notes.txt -o meeting.pdf --template notes
  echo "Content" | %(prog)s - -o output.pdf
        """
    )

    parser.add_argument('input', help='Input file (txt, md, json) or - for stdin')
    parser.add_argument('-o', '--output', required=True, help='Output PDF path')
    parser.add_argument('-t', '--template', default='default',
                        choices=['default', 'report', 'memo', 'notes', 'article'],
                        help='Document template (default: default)')
    parser.add_argument('--toc', action='store_true', help='Include table of contents (report template)')
    parser.add_argument('--title', help='Override document title')
    parser.add_argument('--author', help='Override document author')
    parser.add_argument('--date', help='Override document date')

    args = parser.parse_args()

    try:
        # Parse input
        content = parse_input(args.input)

        # Apply overrides
        if args.title:
            content["title"] = args.title
        if args.author:
            content["author"] = args.author
        if args.date:
            content["date"] = args.date

        # Build options
        options = {"toc": args.toc}

        # Generate PDF
        output = create_pdf(content, args.output, args.template, options)
        print(f"PDF created: {output}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
