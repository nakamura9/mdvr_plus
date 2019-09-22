from django.urls import path
from . import views
from reports.api import get_month
app_name = 'reports'

report_urls = [
    path('harsh-braking-form/', views.HarshBrakingReportForm.as_view(),
        name='harsh-braking-report-form'),
    path('harsh-braking-report/', 
        views.HarshBrakingReport.as_view(),
        name='harsh-braking-report'),
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


urlpatterns = [
    path('create-note/<str:app>/<str:model>/<int:pk>', 
        views.NoteCreateView.as_view(), 
        name='create-note'),
    path('create-vehicle/', views.VehicleCreateView.as_view(), 
        name='create-vehicle'),
    path('list-vehicles/', views.VehicleListView.as_view(), 
        name='list-vehicles'),
    path('update-vehicle/<int:pk>', views.VehicleUpdateView.as_view(), 
        name='update-vehicle'),
    path('vehicle-details/<int:pk>/', views.VehicleDetailView.as_view(), 
        name='vehicle-details'),
    path('create-reminder/', views.ReminderCreateView.as_view(),
        name='create-reminder'),
    path('create-reminder-category/', 
        views.CreateReminderCategory.as_view(),
        name='create-reminder-category'),
    path('reminders-list/', views.ReminderListView.as_view(),
        name='reminders-list'),
    path('update-reminder/<int:pk>', views.ReminderUpdateView.as_view(),
        name='update-reminder'),
    path('reminder-details/<int:pk>', views.ReminderDetailView.as_view(),
        name='reminder-details'),
    
    path('api/month/<int:year>/<int:month>/', get_month),
] + driver_urls + insurance_urls + fitness_certificates_urls + \
    service_urls + incident_urls + report_urls
