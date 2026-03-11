# PDF Formatting Reference

Complete guide to styling and formatting options for document-to-PDF conversion.

## Typography

### Font Sizes

| Element | Size | Leading | Style |
|---------|------|---------|-------|
| Title | 24pt | 28pt | Bold |
| Heading 1 | 16pt | 20pt | Bold |
| Heading 2 | 13pt | 16pt | Bold |
| Body | 11pt | 14pt | Regular |
| Meta/Footer | 9-10pt | 11-12pt | Regular |

### Fonts

**Primary fonts (universal compatibility):**
- Helvetica (sans-serif) - default
- Times-Roman (serif) - formal documents
- Courier - code/monospace

**Custom fonts:** Place TTF files in `assets/fonts/` and register:
```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('CustomFont', 'assets/fonts/custom.ttf'))
```

## Colors

### Default Palette

| Use | Hex | Description |
|-----|-----|-------------|
| Primary text | #1a1a1a | Near-black for readability |
| Headings | #2c3e50 | Dark blue-gray |
| Accent | #3498db | Blue highlight |
| Muted text | #7f8c8d | Gray for meta info |
| Background | #ffffff | White |

### Custom Colors

```python
from reportlab.lib.colors import HexColor

custom_blue = HexColor("#0066cc")
custom_gray = HexColor("#666666")
```

## Page Layout

### Page Sizes

| Size | Dimensions (inches) | Use |
|------|---------------------|-----|
| Letter | 8.5 x 11 | US standard |
| A4 | 8.27 x 11.69 | International |
| Legal | 8.5 x 14 | Legal documents |

### Margins

**Standard margins:**
- All sides: 1 inch (72 points)

**Narrow margins:**
- All sides: 0.75 inch (54 points)

**Wide margins:**
- Left/Right: 1.25 inch (90 points)
- Top/Bottom: 1 inch (72 points)

### Spacing

| Element | Space Before | Space After |
|---------|--------------|-------------|
| Title | 0 | 12pt |
| Heading 1 | 18pt | 10pt |
| Heading 2 | 14pt | 8pt |
| Paragraph | 0 | 8pt |
| Bullet item | 0 | 4pt |

## Tables

### Basic Table Styling

```python
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors

table = Table(data, colWidths=[2*inch, 4*inch])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3498db")),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
]))
```

### Table Patterns

**Header row highlighted:**
```python
('BACKGROUND', (0, 0), (-1, 0), HexColor("#2c3e50")),
('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
```

**Alternating row colors:**
```python
for i in range(1, len(data)):
    bg = HexColor("#f8f9fa") if i % 2 == 0 else colors.white
    styles.append(('BACKGROUND', (0, i), (-1, i), bg))
```

**Bordered table:**
```python
('GRID', (0, 0), (-1, -1), 1, colors.black),
```

**Minimal lines:**
```python
('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header underline
('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Footer line
```

## Headers and Footers

### Page Numbers

```python
def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 9)
    canvas.drawRightString(7.5*inch, 0.5*inch, text)
    canvas.restoreState()

doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
```

### Custom Header

```python
def add_header(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 10)
    canvas.setFillColor(HexColor("#666666"))
    canvas.drawString(inch, 10.5*inch, "Document Title")
    canvas.drawRightString(7.5*inch, 10.5*inch, datetime.now().strftime("%B %d, %Y"))
    canvas.restoreState()
```

## Special Elements

### Horizontal Rules

```python
from reportlab.platypus import HRFlowable

story.append(HRFlowable(width="100%", thickness=1, color=colors.gray))
```

### Callout Boxes

```python
callout_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, -1), HexColor("#e8f4f8")),
    ('BOX', (0, 0), (-1, -1), 1, HexColor("#3498db")),
    ('LEFTPADDING', (0, 0), (-1, -1), 12),
    ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
])

callout = Table([[Paragraph("Note: Important information here", styles['DocBody'])]])
callout.setStyle(callout_style)
```

### Checkbox Items

```
☐ Uncompleted item
☑ Completed item
```

Unicode characters:
- Empty checkbox: `\u2610` (☐)
- Checked box: `\u2611` (☑)
- Crossed box: `\u2612` (☒)

## Template-Specific Options

### Report Template

Options:
- `toc`: Include table of contents
- `page_numbers`: Show page numbers
- `header`: Custom header text

Features:
- Title page with metadata
- Table of contents (optional)
- Section numbering
- Page numbers

### Memo Template

Auto-detected fields:
- TO, FROM, DATE, RE/SUBJECT

Features:
- Standard memo header block
- Horizontal divider
- Formal layout

### Notes Template

Auto-detected sections:
- Attendees
- Agenda
- Discussion/Updates
- Action Items

Features:
- Compact spacing
- Checkbox support
- Bullet optimization

### Article Template

Features:
- First-line paragraph indent
- Publication-style layout
- Author byline
- Clean typography

## JSON Content Format

For programmatic content:

```json
{
  "title": "Document Title",
  "subtitle": "Optional Subtitle",
  "author": "Author Name",
  "date": "January 16, 2025",
  "to": "Recipient (memo only)",
  "from": "Sender (memo only)",
  "subject": "Subject line (memo only)",
  "attendees": ["Alice", "Bob", "Carol"],
  "sections": [
    {
      "heading": "Section Heading",
      "body": [
        "Paragraph one text.",
        "Paragraph two text.",
        "- Bullet item 1",
        "- Bullet item 2"
      ]
    }
  ]
}
```

## Best Practices

1. **Consistent hierarchy** - Use heading levels in order (H1 → H2 → H3)
2. **Adequate whitespace** - Don't crowd content; use spacing
3. **Readable fonts** - Stick to 10-12pt for body text
4. **Limited colors** - Use 2-3 colors maximum
5. **Clear sections** - Break long content into logical sections
6. **Professional metadata** - Include author, date, title
