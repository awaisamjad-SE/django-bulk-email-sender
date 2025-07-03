# bulk_mail/utils.py

import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, body, sender_email, app_password):
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()

        return "success"
    except smtplib.SMTPAuthenticationError:
        return "SMTP authentication failed (check email/app password)."
    except smtplib.SMTPRecipientsRefused:
        return f"Recipient address {to_email} refused."
    except smtplib.SMTPException as e:
        return f"SMTP error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"
