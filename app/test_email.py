from email_sender import send_email
from pdf_generator import generate_warning_pdf

student_name = "Vaani"
roll_no = "101"
total_classes = 3
attended = 2
attendance = (attended / total_classes) * 100

pdf_path = generate_warning_pdf(
    student_name,
    roll_no,
    total_classes,
    attended,
    attendance
)

send_email(
    to_email="vaanigoel15@gmail.com",
    subject="AttendX Warning Notice Test",
    body="This is a test email from AttendX.",
    pdf_path=pdf_path
)

print("Email sent successfully!")