from django.urls import path
from . import views
from reports.api import get_month
app_name = 'reports'

urlpatterns = [
    path('create-vehicle/', views.VehicleCreateView.as_view(), 
        name='create-vehicle'),
    path('update-vehicle/<int:pk>', views.VehicleUpdateView.as_view(), 
        name='update-vehicle'),
    path('vehicle-details/<int:pk>/', views.VehicleDetailView.as_view(), 
        name='vehicle-details'),
    path('create-reminder/', views.ReminderCreateView.as_view(),
        name='create-reminder'),
    path('reminders-list/', views.ReminderListView.as_view(),
        name='reminders-list'),
    path('update-reminder/<int:pk>', views.ReminderUpdateView.as_view(),
        name='update-reminder'),
    path('harsh-braking-form', views.HarshBrakingReport.as_view(),
        name='harsh-braking-report'),
    path('api/month/<int:year>/<int:month>/', get_month),
]
