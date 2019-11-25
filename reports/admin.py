from django.contrib import admin
from reports.models import CalendarReminder, MileageReminder
# Register your models here.
admin.site.register(CalendarReminder)
admin.site.register(MileageReminder)
