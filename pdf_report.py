from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


def create_pdf(question, sql, explanation, result):
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    sections = [
        ("Question", question),
        ("Generated SQL", sql),
        ("AI explanation", explanation),
    ]

    content = [
        Paragraph("Data Analysis Report", styles["Title"]),
        Spacer(1, 16),
    ]

    for heading, text in sections:
        content.append(Paragraph(heading, styles["Heading2"]))

        safe_text = escape(str(text)).replace("\n", "<br/>")
        content.append(Paragraph(safe_text, styles["BodyText"]))
        content.append(Spacer(1, 12))

    preview = result.iloc[:20, :6]

    content.append(Paragraph("Result preview", styles["Heading2"]))
    content.append(
        Paragraph(
            f"Showing {len(preview)} rows and {len(preview.columns)} columns "
            "from the displayed result. Use the CSV download for more data.",
            styles["BodyText"],
        )
    )
    content.append(Spacer(1, 12))

    if len(preview.columns) > 0:
        table_data = [
            [
                Paragraph(escape(str(column)), styles["BodyText"])
                for column in preview.columns
            ]
        ]

        for row in preview.itertuples(index=False, name=None):
            table_data.append([
                Paragraph(escape(str(value)), styles["BodyText"])
                for value in row
            ])

        table = Table(
            table_data,
            colWidths=[document.width /
                       len(preview.columns)] * len(preview.columns),
            repeatRows=1,
        )
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        content.append(table)

    document.build(content)
    return buffer.getvalue()
