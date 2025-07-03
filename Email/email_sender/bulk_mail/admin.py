# bulk_mail/admin.py
from django.contrib import admin
from .models import EmailLog

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('email', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('email',)
