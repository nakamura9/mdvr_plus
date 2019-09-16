from django.views.generic import (TemplateView, 
                                  CreateView, 
                                  DetailView, 
                                  ListView,
                                  UpdateView,
                                  FormView
                                  )
from .models import Vehicle, Reminder
from .forms import VehicleForm, ReminderForm, HarshBrakingReportForm
import os
from common.mixins import ContextMixin, PaginationMixin
from django.urls import reverse_lazy as reverse
from .filters import ReminderFilter
from django_filters.views import FilterView
from common.models import Config
from common import api
CREATE_TEMPLATE = os.path.join('common', 'create.html')

class VehicleCreateView(ContextMixin, CreateView):
    model = Vehicle
    form_class= VehicleForm
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Create Vehicle'
    }

class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = os.path.join('reports', 'vehicle_detail.html')

class VehicleUpdateView(ContextMixin, UpdateView):
    form_class = VehicleForm
    queryset = Vehicle.objects.all()
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Update Vehicle Information'
    }

class ReminderCreateView(ContextMixin, CreateView):
    template_name =CREATE_TEMPLATE
    form_class = ReminderForm
    model = Reminder
    success_url = reverse('reports:reminders-list')
    context = {
        'title': 'Generate Reminder'
    }

    def get_initial(self):
        config = Config.objects.first()
        return {
            'reminder_email': config.default_reminder_email
        }

class ReminderUpdateView(ContextMixin, UpdateView):
    template_name =CREATE_TEMPLATE
    form_class = ReminderForm
    queryset = Reminder.objects.all()
    success_url = reverse('reports:reminder-list')
    context = {
        'title': 'Update Reminder'
    }

class ReminderListView(PaginationMixin, FilterView):
    template_name = os.path.join('reports', 'reminder_list.html')
    queryset = Reminder.objects.all()
    filterset_class = ReminderFilter
    paginate_by = 20

class HarshBrakingReport(FormView):
    form_class=HarshBrakingReportForm
    template_name = os.path.join('reports', 'harsh_braking.html')
    success_url = reverse('app:home')


class CalendarView(TemplateView):
    template_name = os.path.join('reports','calendar.html')