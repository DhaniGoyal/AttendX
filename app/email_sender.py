import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email, subject, body, pdf_path):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(pdf_path, "rb") as f:
        pdf_data = f.read()

    msg.add_attachment(
        pdf_data,
        maintype="application",
        subtype="pdf",
        filename=os.path.basename(pdf_path)
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(msg)

    return True