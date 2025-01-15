from django.contrib import admin
from .models import RequestLog, ErrorLog

# Register models with optional customization
@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'sent_at', 'response_status_code', 'send_to', 'error_log')
    list_filter = ('send_to', 'response_status_code', 'sent_at')
    search_fields = ('sender__name', 'send_to')  # Assuming `APIKey` has a `name` field

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'error_type', 'timestamp', 'error_message')
    list_filter = ('error_type', 'timestamp')
    search_fields = ('error_type', 'error_message')

# Register your models here.
