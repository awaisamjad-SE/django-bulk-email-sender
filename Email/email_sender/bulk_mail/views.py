import pandas as pd
import os
from django.shortcuts import render, redirect
from .forms import FileUploadForm, ColumnMappingForm
import smtplib
from email.mime.text import MIMEText
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
import tempfile
import os
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from django.shortcuts import render
import os
import pandas as pd
from django.shortcuts import render, redirect
from .tasks import send_bulk_emails_task  # Celery task
from io import StringIO
import smtplib
import smtplib
from email.mime.text import MIMEText

from .utils import send_email

def get_email_credentials(request):
    if request.method == 'POST':
        sender_email = request.POST.get('sender_email').strip()
        app_password = request.POST.get('app_password').strip()

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.quit()

            request.session['sender_email'] = sender_email
            request.session['app_password'] = app_password

            return redirect('upload_file')

        except smtplib.SMTPAuthenticationError:
            error_message = "Invalid email or app password. Please double-check and try again."
            return render(request, 'bulk_mail/credentials.html', {'error': error_message})

    return render(request, 'bulk_mail/credentials.html')


def upload_file(request):
    # ✅ Ensure email credentials exist in session
    if not request.session.get('sender_email') or not request.session.get('app_password'):
        return redirect('get_email_credentials')

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_name = file.name.lower()

            try:
                # ✅ Load file into DataFrame
                if file_name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file_name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    return render(request, 'bulk_mail/error.html', {
                        'message': 'Unsupported file format. Please upload a CSV or Excel file.'
                    })

                # ✅ Save DataFrame to a temporary JSON file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8') as tmp:
                    df.to_json(tmp.name, orient='records')  # Save data as a list of dicts
                    tmp.flush()
                    request.session['data_file'] = tmp.name  # Save path in session
                    request.session.modified = True  # ✅ Force Django to save the session

                return redirect('map_columns')

            except Exception as e:
                return render(request, 'bulk_mail/error.html', {
                    'message': f"File processing failed: {str(e)}"
                })
    else:
        form = FileUploadForm()

    return render(request, 'bulk_mail/upload.html', {'form': form})

# views.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import io, base64
from django.shortcuts import render
from .tasks import send_bulk_emails_task
from .models import EmailLog

from django.shortcuts import render
import pandas as pd
import os
import matplotlib.pyplot as plt
import io, base64

from .tasks import send_bulk_emails_task
from .models import EmailLog

def map_columns(request):
    if request.method == 'POST':
        name_column = request.POST.get('name_column', '').strip()
        email_column = request.POST.get('email_column').strip()
        subject = request.POST.get('subject').strip()
        body_template = request.POST.get('body').strip()

        data_file = request.session.get('data_file')
        if not data_file or not os.path.exists(data_file):
            return render(request, 'bulk_mail/error.html', {
                'message': 'Uploaded data not found. Please upload your file again.'
            })

        try:
            df = pd.read_json(data_file)
        except Exception as e:
            return render(request, 'bulk_mail/error.html', {
                'message': f"Error reading data file: {str(e)}"
            })

        # Validate required columns
        missing_columns = []
        if email_column not in df.columns:
            missing_columns.append(email_column)
        if name_column and name_column not in df.columns:
            missing_columns.append(name_column)
        if missing_columns:
            return render(request, 'bulk_mail/error.html', {
                'message': f"Missing columns: {', '.join(missing_columns)}"
            })

        # Clean email column
        df = df[df[email_column].notna()]
        df[email_column] = df[email_column].astype(str).str.strip()
        df = df[df[email_column] != ""]

        # Get email credentials
        sender_email = request.session.get('sender_email')
        app_password = request.session.get('app_password')

        # ✅ Trigger Celery in background
        df_dict = df.to_dict(orient='records')
        send_bulk_emails_task.delay(
            df_dict, subject, body_template,
            email_column, name_column,
            sender_email, app_password
        )

        total = len(df)

        return render(request, 'bulk_mail/success.html', {
            'total': total,
            'success': 0,
            'failed': 0,
            'graph': '',  # optional: show "emails being sent..." spinner
            'message': '✅ Emails are being sent in the background. This may take a few minutes.'
        })

    return render(request, 'bulk_mail/map_columns.html')

from .models import EmailLog

def email_logs_view(request):
    logs = EmailLog.objects.all().order_by('-timestamp')
    return render(request, 'bulk_mail/email_logs.html', {'logs': logs})


def logout_credentials(request):
    request.session.flush()  # completely clear the session
    return redirect('get_email_credentials')  # redirect to credentials page
def pricing_view(request):
    return render(request, 'pricing.html')

def support_view(request):
    return render(request, 'Support.html')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render

def success_view(request):
    # For demo purpose let's assume:
    total_count = 100
    success_count = 80
    failed_count = 20

    # Create the bar chart
    labels = ['Success', 'Failed']
    values = [success_count, failed_count]

    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['#22c55e', '#ef4444'])
    ax.set_title('Email Sending Results')
    ax.set_ylabel('Count')

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    context = {
    'success_emails': success_emails,
    'failed_emails': failed_emails
    }
    return render(request, 'bulk_mail/success.html', context)

# views.py

from django.shortcuts import redirect

def home_view(request):
    if request.session.get('sender_email') and request.session.get('app_password'):
        return redirect('upload_file')  # or whatever your upload file url name
    else:
        return redirect('get_email_credentials')
