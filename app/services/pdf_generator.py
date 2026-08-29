import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from app.core.config import settings
from app.models.user import User
from app.models.workout import WorkoutPlan
from app.models.physique import PhysiqueScan

class PDFGenerator:
    """Generates professional, printable 4-week coaching blueprint PDFs."""

    @classmethod
    def generate_coaching_dossier(
        cls,
        user: User,
        plan: WorkoutPlan,
        latest_scan: PhysiqueScan = None
    ) -> str:
        os.makedirs(settings.REPORTS_DIR, exist_ok=True)
        filename = f"fitmorph_blueprint_user_{user.id}_{plan.id}.pdf"
        output_path = os.path.join(settings.REPORTS_DIR, filename)

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1E293B"),
            alignment=0
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#64748B")
        )
        h2_style = ParagraphStyle(
            "Heading2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyCustom",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155")
        )
        cell_header_style = ParagraphStyle(
            "CellHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=colors.whitesmoke
        )
        cell_body_style = ParagraphStyle(
            "CellBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#1E293B")
        )

        elements = []

        # --- HEADER ---
        elements.append(Paragraph("FITMORPH ATHLETIC INTELLIGENCE", title_style))
        elements.append(Paragraph(f"Personalized 4-Week Coaching Blueprint & Progression Dossier | Generated {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
        elements.append(Spacer(1, 14))

        # --- PROFILE SUMMARY CARD ---
        profile = user.profile
        profile_data = [
            [
                Paragraph(f"<b>Athlete:</b> {user.full_name or user.email}", body_style),
                Paragraph(f"<b>Primary Goal:</b> {plan.goal.replace('_', ' ').title()}", body_style),
                Paragraph(f"<b>Gender:</b> {plan.gender.title()}", body_style)
            ],
            [
                Paragraph(f"<b>Height / Weight:</b> {profile.height_cm if profile else 0}cm / {profile.weight_kg if profile else 0}kg", body_style),
                Paragraph(f"<b>BMI / Tier:</b> {profile.bmi if profile else 0} ({profile.fitness_goal if profile else 'N/A'})", body_style),
                Paragraph(f"<b>Equipment Setup:</b> {plan.equipment.replace('_', ' ').title()}", body_style)
            ],
            [
                Paragraph(f"<b>Flagged Injuries:</b> {profile.injuries if profile else 'None'}", body_style),
                Paragraph(f"<b>Training Split:</b> {plan.split_type}", body_style),
                Paragraph(f"<b>Deload Status:</b> {'Scheduled' if plan.deload_scheduled else 'Standard Progression'}", body_style)
            ]
        ]
        profile_table = Table(profile_data, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        profile_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(profile_table)
        elements.append(Spacer(1, 14))

        # --- SECTION: WORKOUT DAYS ---
        elements.append(Paragraph("4-WEEK PERIODIZED TRAINING SCHEDULE", h2_style))
        elements.append(Paragraph("Execute the assigned sets and reps with strict adherence to prescribed rest intervals and RPE targets.", subtitle_style))
        elements.append(Spacer(1, 8))

        for day in plan.days:
            elements.append(Paragraph(f"<b>{day.day_name}</b>", ParagraphStyle("DayTitle", parent=h2_style, fontSize=11, leading=14, textColor=colors.HexColor("#2563EB"))))
            elements.append(Paragraph(f"<b>Cardio Protocol:</b> {day.cardio_protocol}", body_style))
            elements.append(Spacer(1, 4))

            # Exercise Table
            table_rows = [
                [
                    Paragraph("Exercise", cell_header_style),
                    Paragraph("Target Muscle", cell_header_style),
                    Paragraph("Sets", cell_header_style),
                    Paragraph("Reps", cell_header_style),
                    Paragraph("Rest (s)", cell_header_style),
                    Paragraph("RPE", cell_header_style),
                    Paragraph("Form & Safety Cue", cell_header_style)
                ]
            ]

            for item in day.exercise_list:
                table_rows.append([
                    Paragraph(item.get("name", ""), cell_body_style),
                    Paragraph(item.get("muscle", ""), cell_body_style),
                    Paragraph(str(item.get("sets", 3)), cell_body_style),
                    Paragraph(str(item.get("reps", "8-12")), cell_body_style),
                    Paragraph(f"{item.get('rest_seconds', 90)}s", cell_body_style),
                    Paragraph(str(item.get("rpe_target", 8.0)), cell_body_style),
                    Paragraph(item.get("cues", "")[:80], cell_body_style)
                ])

            ex_table = Table(table_rows, colWidths=[1.8*inch, 1.0*inch, 0.5*inch, 0.6*inch, 0.6*inch, 0.5*inch, 2.5*inch])
            ex_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ]))
            elements.append(ex_table)
            elements.append(Spacer(1, 10))

        # --- SECTION: AI PHYSIQUE ANALYSIS (IF PRESENT) ---
        if latest_scan:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph("AI PHYSIQUE SYMMETRY & POSTURAL ASSESSMENT", h2_style))
            scan_info = [
                [
                    Paragraph(f"<b>Overall Muscular Symmetry Score:</b> {latest_scan.symmetry_score} / 100", body_style),
                    Paragraph(f"<b>Estimated Body Composition:</b> {latest_scan.estimated_body_composition}", body_style)
                ],
                [
                    Paragraph(f"<b>Strong Muscle Groups:</b> {latest_scan.strong_muscle_groups}", body_style),
                    Paragraph(f"<b>Lagging / Priority Focus:</b> {latest_scan.lagging_muscle_groups}", body_style)
                ],
                [
                    Paragraph(f"<b>Postural Alignment Notes:</b> {latest_scan.posture_assessment}", body_style),
                    Paragraph(f"<b>Biomechanical Guidance:</b> {latest_scan.ai_analysis_notes[:100]}...", body_style)
                ]
            ]
            scan_table = Table(scan_info, colWidths=[3.75*inch, 3.75*inch])
            scan_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]))
            elements.append(scan_table)

        # --- FOOTER RULES ---
        elements.append(Spacer(1, 12))
        rules_text = (
            "<b>Progressive Overload Principle:</b> Strive to add 1 repetition or increase weight by 1-2kg per week while maintaining pristine form. "
            "If joint discomfort occurs, utilize FitMorph's 1-click exercise swap engine to maintain joint-safe momentum without training through sharp pain."
        )
        elements.append(Paragraph(rules_text, subtitle_style))

        doc.build(elements)
        return output_path
