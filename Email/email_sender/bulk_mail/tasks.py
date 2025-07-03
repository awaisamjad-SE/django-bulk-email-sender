# bulk_mail/tasks.py
from celery import shared_task
from .utils import send_email
from .models import EmailLog

@shared_task
def send_bulk_emails_task(df_dict, subject, body_template, email_column, name_column, sender_email, app_password):
    results = []
    for row in df_dict:
        email = row.get(email_column)
        name = row.get(name_column, "")
        name = name if name else ""
        body = body_template.replace("{name}", name)

        try:
            result = send_email(email, subject, body, sender_email, app_password)
            if result == "success":
                EmailLog.objects.create(email=email, status="Success")
                results.append({'email': email, 'status': 'Success'})
            else:
                EmailLog.objects.create(email=email, status="Failed", error=result)
                results.append({'email': email, 'status': 'Failed', 'error': result})
        except Exception as e:
            EmailLog.objects.create(email=email, status="Failed", error=str(e))
            results.append({'email': email, 'status': 'Failed', 'error': str(e)})
    return results
