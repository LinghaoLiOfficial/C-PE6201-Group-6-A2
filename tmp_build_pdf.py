import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path("/Users/llh/PycharmProjects/C-PE6201-Group-6-A2")
NB = ROOT / "Part3_LI_LINGHAO" / "PE6201_Class4_C2_Agent_Build_中文.ipynb"
PDF = ROOT / "Part3_LI_LINGHAO" / "PE6201_Class4_C2_Agent_Build_中文.pdf"


def register_fonts():
    candidates = [
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", "CJK"),
        ("/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf", "CJK"),
        ("/System/Library/Fonts/Supplemental/Songti.ttc", "CJK"),
    ]
    for path, name in candidates:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(name, path))
            return name
    raise FileNotFoundError("No Unicode Chinese font found")


def inline_markup(text):
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="7.8">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)
    return text


def markdown_blocks(text, styles):
    lines = text.splitlines()
    story = []
    paragraph = []
    i = 0

    def flush():
        nonlocal paragraph
        if paragraph:
            story.append(Paragraph(inline_markup(" ".join(x.strip() for x in paragraph)), styles["CNBody"]))
            paragraph = []

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
            i += 1
            continue
        if line.startswith("```"):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i])
                i += 1
            story.append(Table([[Preformatted("\n".join(code), styles["CNCode"])]], colWidths=[178 * mm],
                               style=TableStyle([
                                   ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F5F6F7")),
                                   ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#D7DBE0")),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                   ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                                   ("TOPPADDING", (0, 0), (-1, -1), 5),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                               ])))
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            flush()
            level, title = len(heading.group(1)), inline_markup(heading.group(2))
            style = styles["CNTitle"] if level == 1 else styles["CNH2"] if level == 2 else styles["CNH3"]
            story.append(Paragraph(title, style))
            i += 1
            continue
        if line.strip() == "---":
            flush()
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#AEBECA"), spaceBefore=3, spaceAfter=6))
            i += 1
            continue
        if line.startswith(">"):
            flush()
            quote = []
            while i < len(lines) and lines[i].startswith(">"):
                quote.append(lines[i][1:].strip())
                i += 1
            story.append(Paragraph(inline_markup(" ".join(quote)), styles["CNQuote"]))
            continue
        item = re.match(r"^\s*(\*|-|\d+\.)\s+(.*)$", line)
        if item:
            flush()
            story.append(Paragraph(f"{item.group(1)} {inline_markup(item.group(2))}", styles["CNBody"]))
            i += 1
            continue
        if line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [x.strip() for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", c or " ") for c in cells):
                    rows.append([Paragraph(inline_markup(c), styles["CNBody"]) for c in cells])
                i += 1
            if rows:
                width = 178 * mm / len(rows[0])
                table = Table(rows, colWidths=[width] * len(rows[0]), repeatRows=1)
                table.setStyle(TableStyle([
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AEBECA")),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]))
                story.append(table)
            continue
        paragraph.append(line)
        i += 1
    flush()
    return story


def build_story(font):
    data = json.loads(NB.read_text(encoding="utf-8"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CNBody", parent=styles["BodyText"], fontName=font, fontSize=9.6,
        leading=14, spaceAfter=4, textColor=colors.HexColor("#202124"),
    ))
    styles.add(ParagraphStyle(
        name="CNTitle", parent=styles["Title"], fontName=font, fontSize=19,
        leading=23, textColor=colors.HexColor("#17365D"), spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="CNH2", parent=styles["Heading2"], fontName=font, fontSize=14,
        leading=18, textColor=colors.HexColor("#1F4E79"), spaceBefore=10, spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="CNH3", parent=styles["Heading3"], fontName=font, fontSize=11.5,
        leading=15, textColor=colors.HexColor("#365F91"), spaceBefore=8, spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="CNCode", fontName=font, fontSize=6.1, leading=7.5,
        leftIndent=6, rightIndent=6, textColor=colors.HexColor("#1f2933"),
    ))
    styles.add(ParagraphStyle(
        name="CNQuote", parent=styles["CNBody"], leftIndent=9, rightIndent=5,
        borderPadding=6, backColor=colors.HexColor("#F2F6FA"),
        borderColor=colors.HexColor("#6B9AC4"), borderWidth=2, borderStart=True,
    ))
    story = []
    for cell in data["cells"]:
        if cell["cell_type"] == "markdown":
            raw = "".join(cell.get("source", []))
            story.extend(markdown_blocks(raw, styles))
        else:
            code = "".join(cell.get("source", []))
            code_lines = code.splitlines()
            for start in range(0, len(code_lines), 48):
                chunk = "\n".join(code_lines[start:start + 48])
                story.append(Preformatted(chunk, styles["CNCode"]))
                story.append(Spacer(1, 3))
        story.append(HRFlowable(width="100%", thickness=0.35, color=colors.HexColor("#DCE6F1"), spaceBefore=4, spaceAfter=6))
    return story


def main():
    font = register_fonts()
    doc = SimpleDocTemplate(
        str(PDF), pagesize=A4, rightMargin=15 * mm, leftMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm, title="PE6201 Class 4 Capsule 2 中文版",
    )
    doc.build(build_story(font))
    print(PDF)


if __name__ == "__main__":
    main()
