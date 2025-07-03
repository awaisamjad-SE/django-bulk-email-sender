# bulk_mail/models.py
from django.db import models

class EmailLog(models.Model):
    email = models.EmailField()
    status = models.CharField(max_length=10)  # "Success" or "Failed"
    error = models.TextField(blank=True, null=True)
    sender = models.EmailField(blank=True, null=True)  # NEW: track sender
    timestamp = models.DateTimeField(auto_now_add=True)
