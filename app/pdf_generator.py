from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os


def generate_warning_pdf(
    student_name,
    roll_no,
    total_classes,
    attended,
    attendance_percentage
):
    shortage = total_classes - attended

    file_name = f"warning_{roll_no}.pdf"
    file_path = os.path.join(os.getcwd(), file_name)

    pdf = canvas.Canvas(file_path, pagesize=A4)

    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        width / 2,
        height - 80,
        "ATTENDANCE WARNING NOTICE"
    )

    pdf.setFont("Helvetica", 12)

    pdf.drawString(70, height - 140, f"Student Name: {student_name}")
    pdf.drawString(70, height - 165, f"Roll Number: {roll_no}")
    pdf.drawString(70, height - 190, f"Total Classes: {total_classes}")
    pdf.drawString(70, height - 215, f"Classes Attended: {attended}")
    pdf.drawString(
        70,
        height - 240,
        f"Attendance Percentage: {attendance_percentage:.2f}%"
    )
    pdf.drawString(70, height - 265, f"Classes Missed: {shortage}")

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(
        70,
        height - 320,
        "Warning:"
    )

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        70,
        height - 345,
        "Your attendance is below the required minimum of 75%."
    )

    pdf.drawString(
        70,
        height - 365,
        "You are advised to maintain regular attendance."
    )

    pdf.drawString(
        70,
        height - 410,
        "This notice has been generated automatically by AttendX."
    )

    pdf.save()

    return file_path