from django.urls import path
from . import views
from reports.api import get_month
from rest_framework.routers import DefaultRouter
app_name = 'reports'

calendar_alert_router = DefaultRouter()
calendar_alert_router.register('api/calendar-reminder-alerts', 
    views.CalendarReminderAlertViewset)

mileage_alert_router = DefaultRouter()
mileage_alert_router.register('api/mileage-reminder-alerts', 
    views.MileageReminderAlertViewset)

report_urls = [
    
    path('harsh-braking-report/', 
        views.HarshBrakingReport.as_view(),
        name='harsh-braking-report'),
    path('harsh-braking-pdf/', 
        views.HarshBrakingPDFReport.as_view(),
        name='harsh-braking-pdf'),
    path('harsh-braking-csv/', 
        views.harsh_braking_csv_report,
        name='harsh-braking-csv'),
    path('speeding-report/', 
        views.SpeedingReport.as_view(),
        name='speeding-report'),
    path('speeding-pdf/', 
        views.SpeedingPDFReport.as_view(),
        name='speeding-pdf'),
    path('speeding-csv/', 
        views.speeding_report_csv,
        name='speeding-csv'),
]

driver_urls = [
    path('create-driver/', views.DriverCreateView.as_view(), 
        name='create-driver'),
    path('update-driver/<int:pk>/', views.DriverUpdateView.as_view(), 
        name='update-driver'),
    path('list-drivers/', views.DriverListView.as_view(), 
        name='list-drivers'),
    path('driver-details/<int:pk>/', views.DriverDetailView.as_view(), 
        name='driver-details'),
    path('create-medical/<int:pk>', views.CreateMedical.as_view(), 
        name='create-medical'),
    path('create-ddc/<int:pk>', views.CreateDDC.as_view(), 
        name='create-ddc'),
]

insurance_urls = [
    path('create-insurance/<int:pk>/', views.CreateInsurance.as_view(), 
        name='create-insurance'),
    path('update-insurance/<int:pk>/', views.UpdateInsurance.as_view(), 
        name='update-insurance'),
]

incident_urls = [
    path('create-incident/<int:pk>/', views.CreateIncident.as_view(), 
        name='create-incident'),
    path('update-incident/<int:pk>/', views.UpdateIncident.as_view(), 
        name='update-incident'),
]


fitness_certificates_urls = [
    path('create-fitness-certificate/<int:pk>/', 
        views.CreateFitnessCertificate.as_view(), 
        name='create-fitness-certificate'),
    path('update-fitness-certificate/<int:pk>/', 
        views.UpdateFitnessCertificate.as_view(), 
        name='update-fitness-certificate'),
]

service_urls = [
    path('create-service/', views.CreateVehicleService.as_view(), 
        name='create-service'),
    path('create-service-log/<int:pk>', 
        views.CreateServiceLog.as_view(), 
        name='create-service-log'),
    path('update-service/<int:pk>/', views.UpdateVehicleService.as_view(), 
        name='update-service'),
]

reminder_urls = [
    path('create-reminder/', views.CalendarReminderCreateView.as_view(),
        name='create-reminder'),
    path('create-reminder-category/', 
        views.CreateReminderCategory.as_view(),
        name='create-reminder-category'),
    path('reminders-list/', views.CalendarReminderListView.as_view(),
        name='reminders-list'),
    path('update-reminder/<int:pk>', views.CalendarReminderUpdateView.as_view(),
        name='update-reminder'),
    path('reminder-details/<int:pk>', 
        views.CalendarReminderDetailView.as_view(),
        name='reminder-details'),
    path('create-mileage-reminder/', views.MileageReminderCreateView.as_view(),
        name='create-mileage-reminder'),
    path('mileage-reminders-list/', views.MileageReminderListView.as_view(),
        name='mileage-reminders-list'),
    path('update-mileage-reminder/<int:pk>', views.MileageReminderUpdateView.as_view(),
        name='update-mileage-reminder'),
    path('mileage-reminder-details/<int:pk>', 
        views.MileageReminderDetailView.as_view(),
        name='mileage-reminder-details'),
    path('create-mileage-reminder-alert/<int:pk>', 
        views.MileageReminderAlertCreateView.as_view(),
        name='create-mileage-reminder-alert'),
    path('create-reminder-alert/<int:pk>', 
        views.CalendarReminderAlertCreateView.as_view(),
        name='create-reminder-alert'),
]

urlpatterns = [
    path('create-note/<str:app>/<str:model>/<int:pk>', 
        views.NoteCreateView.as_view(), 
        name='create-note'),
    path('create-vehicle/', views.VehicleCreateView.as_view(), 
        name='create-vehicle'),
    path('import-vehicles/', views.ImportVehiclesView.as_view(), 
        name='import-vehicles'),
    path('list-vehicles/', views.VehicleListView.as_view(), 
        name='list-vehicles'),
    path('update-vehicle/<int:pk>', views.VehicleUpdateView.as_view(), 
        name='update-vehicle'),
    path('vehicle-details/<int:pk>/', views.VehicleDetailView.as_view(), 
        name='vehicle-details'),
    path('api/month/<int:year>/<int:month>/', get_month),
    path('report-form/<str:action>/', views.ReportFormView.as_view(),
        name='report-form'),
    path('alarms/', views.retrieve_alarms,
        name='alarms'),
    path('upcoming-reminders/', views.UpcomingRemindersViews.as_view(),
        name='upcoming-reminders'),
    path('map/<str:lat>/<str:lng>/', views.GPSView.as_view(),
        name='map'),
] + driver_urls + insurance_urls + fitness_certificates_urls + \
    service_urls + incident_urls + report_urls + calendar_alert_router.urls + \
        mileage_alert_router.urls + reminder_urls

