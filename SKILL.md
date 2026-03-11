---
name: doc-to-pdf
description: "Convert user-provided materials (work docs, notes, reports, meeting notes, research) into structured, professionally formatted PDFs. Use when asked to: (1) Convert documents to PDF, (2) Create professional PDFs from raw content, (3) Format unstructured text into polished documents, (4) Generate reports or summaries as downloadable PDFs. Triggers: 'make this a PDF', 'convert to PDF', 'format as PDF', 'create a professional document', 'export as PDF'."
---

# Document to PDF Converter

Convert user-provided materials into structured, professionally formatted PDFs.

## Workflow

1. **Analyze Input** - Identify document type and structure
2. **Select Template** - Choose appropriate layout (report, memo, notes, article)
3. **Generate PDF** - Run `scripts/generate_pdf.py` with content
4. **Deliver** - Provide download link

## Quick Start

```bash
# Basic conversion
python scripts/generate_pdf.py input.txt -o output.pdf

# With template
python scripts/generate_pdf.py input.txt -o output.pdf --template report

# From stdin (for inline content)
echo "Your content here" | python scripts/generate_pdf.py - -o output.pdf
```

## Document Types & Templates

| Input Type | Template | Features |
|------------|----------|----------|
| Meeting notes | `notes` | Attendees, agenda, action items |
| Reports | `report` | Title page, TOC, sections, page numbers |
| Memos | `memo` | Header block, body, signature |
| Articles | `article` | Title, author, body with columns |
| General | `default` | Clean formatting, headers, body |

## Content Analysis

Before generating, analyze the input to determine:

1. **Document type** - Report? Meeting notes? Memo? Article?
2. **Structure** - Are there clear sections? Bullet points? Tables?
3. **Metadata** - Title, author, date, recipients?
4. **Special elements** - Tables, code blocks, images?

## Generation Process

### Step 1: Prepare Content

Extract and organize content into sections:

```python
content = {
    "title": "Document Title",
    "subtitle": "Optional Subtitle",
    "author": "Author Name",
    "date": "2025-01-16",
    "sections": [
        {"heading": "Section 1", "body": "Content here..."},
        {"heading": "Section 2", "body": "More content..."}
    ]
}
```

### Step 2: Select Template

Choose based on document characteristics:

- **Has agenda + attendees + action items?** → `notes`
- **Has To/From/Subject/Date header?** → `memo`
- **Long-form with multiple chapters?** → `report`
- **Single topic, publication style?** → `article`
- **General content?** → `default`

### Step 3: Generate

```bash
python scripts/generate_pdf.py content.json -o document.pdf --template report
```

Or generate directly with Python:

```python
from scripts.generate_pdf import create_pdf

create_pdf(
    content=content,
    output_path="document.pdf",
    template="report",
    options={
        "page_numbers": True,
        "toc": True,
        "header": "Company Name"
    }
)
```

## Formatting Options

See `references/formatting.md` for complete styling guide including:

- Typography (fonts, sizes, spacing)
- Colors and branding
- Table styles
- Header/footer customization
- Page layout options

## Professional Formatting Standards

**Typography:**
- Title: 24pt bold
- Headings: 16pt bold
- Body: 11pt regular
- Font: Arial or Helvetica (universal compatibility)

**Layout:**
- Margins: 1 inch all sides
- Line spacing: 1.15
- Paragraph spacing: 6pt after

**Visual Hierarchy:**
- Clear section breaks
- Consistent heading styles
- Proper whitespace

## Examples

### Meeting Notes

Input:
```
Sales Team Weekly Standup
January 15, 2025
Attendees: Alice, Bob, Carol

Updates:
- Q4 closed at 112% of target
- New CRM rollout next week

Action Items:
- [ ] Alice: Send Q4 report by Friday
- [ ] Bob: Schedule CRM training
```

Command:
```bash
python scripts/generate_pdf.py meeting.txt -o standup.pdf --template notes
```

### Report

Input: Any markdown or text file with sections

Command:
```bash
python scripts/generate_pdf.py report.md -o quarterly_report.pdf --template report --toc
```

## Troubleshooting

**PDF looks wrong:** Check input encoding (UTF-8 required)
**Missing fonts:** Install Arial/Helvetica or use `--font "DejaVu Sans"`
**Tables misaligned:** Use consistent column delimiters (| or tabs)

## Dependencies

- `reportlab`: PDF generation
- `markdown2`: Markdown parsing
- `Pillow`: Image handling

Install: `pip install reportlab markdown2 Pillow --break-system-packages`
