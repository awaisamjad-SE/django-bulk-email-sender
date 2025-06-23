import pandas as pd
import os
from django.shortcuts import render, redirect
from .forms import FileUploadForm, ColumnMappingForm
import smtplib
from email.mime.text import MIMEText

import smtplib

def get_email_credentials(request):
    if request.method == 'POST':
        sender_email = request.POST.get('sender_email').strip()
        app_password = request.POST.get('app_password').strip()

        # ✅ Test credentials before saving to session
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.quit()

            # ✅ If login successful, save to session
            request.session['sender_email'] = sender_email
            request.session['app_password'] = app_password

            return redirect('upload_file')

        except smtplib.SMTPAuthenticationError as e:
            error_message = "Invalid email or app password. Please double-check and try again."
            return render(request, 'bulk_mail/credentials.html', {'error': error_message})

    return render(request, 'bulk_mail/credentials.html')


# Upload file view
def upload_file(request):
    # Check if credentials exist in session
    if not request.session.get('sender_email') or not request.session.get('app_password'):
        return redirect('get_email_credentials')

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            file_name = file.name.lower()

            if file_name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file_name.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
            else:
                return render(request, 'bulk_mail/error.html', {'message': 'Unsupported file format.'})

            request.session['data'] = df.to_json()
            return redirect('map_columns')
    else:
        form = FileUploadForm()
    return render(request, 'bulk_mail/upload.html', {'form': form})

# Map columns view
def map_columns(request):
    if request.method == 'POST':
        name_column = request.POST.get('name_column', '').strip()
        email_column = request.POST.get('email_column').strip()
        subject = request.POST.get('subject').strip()
        body_template = request.POST.get('body').strip()

        # Load dataframe from session
        import json
        from io import StringIO

        df_json = request.session.get('data')
        if not df_json:
            return render(request, 'bulk_mail/error.html', {'message': 'No file data found in session. Please upload file again.'})

        df = pd.read_json(StringIO(df_json))

        # Validate columns
        missing_columns = []
        if email_column not in df.columns:
            missing_columns.append(email_column)
        if name_column and name_column not in df.columns:
            missing_columns.append(name_column)
        if missing_columns:
            message = f"Error: The following columns were not found: {', '.join(missing_columns)}"
            return render(request, 'bulk_mail/error.html', {'message': message})
        
        # Get credentials from session (THIS IS WHERE YOU USE IT)
        sender_email = request.session.get('sender_email')
        app_password = request.session.get('app_password')

        success_emails = []
        failed_emails = []

        for _, row in df.iterrows():
            email = row[email_column]
            name = row[name_column] if name_column else ""
            name = name if pd.notnull(name) else ""

            personalized_body = body_template.replace("{name}", name if name else "")

            # Use the credentials you got from session
            result = send_email(email, subject, personalized_body, sender_email, app_password)
            
            if result == "success":
                success_emails.append(email)
            else:
                failed_emails.append((email, result))

        context = {
            'success_emails': success_emails,
            'failed_emails': failed_emails
        }
        return render(request, 'bulk_mail/success.html', context)

    return render(request, 'bulk_mail/map_columns.html')

# Email sending function
def send_email(to_email, subject, body, sender_email, app_password):
    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        return "success"
    except Exception as e:
        return str(e)

def logout_credentials(request):
    request.session.flush()  # completely clear the session
    return redirect('get_email_credentials')  # redirect to credentials page
