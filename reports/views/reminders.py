from django.views.generic import (TemplateView, 
                                  CreateView, 
                                  DetailView, 
                                  ListView,
                                  UpdateView,
                                  FormView
                                  )
import datetime
from reports import forms, models, filters
import os
from common.mixins import ContextMixin, PaginationMixin
from django.urls import reverse_lazy as reverse
from django_filters.views import FilterView
from common.models import Config
# from common import api
from reports.serializers import (AlarmSerializer, 
                                 CalendarReminderAlertSerializer,
                                 MileageReminderAlertSerializer,
                                 )

CREATE_TEMPLATE = os.path.join('common', 'create.html')

class CalendarReminderCreateView(ContextMixin, CreateView):
    template_name =CREATE_TEMPLATE
    form_class = forms.CalendarReminderForm
    model = models.CalendarReminder
    success_url = reverse('reports:reminders-list')
    context = {
        'title': 'Generate Calendar Reminder'
    }

    def get_initial(self):
        config = Config.objects.first()
        return {
            'reminder_email': config.default_reminder_email
        }

   
class CalendarReminderUpdateView(ContextMixin, UpdateView):
    template_name =CREATE_TEMPLATE
    form_class = forms.CalendarReminderForm
    queryset = models.CalendarReminder.objects.all()
    success_url = reverse('reports:reminders-list')
    context = {
        'title': 'Update Calendar Reminder'
    }


class CalendarReminderListView(PaginationMixin, FilterView):
    template_name = os.path.join('reports', 'reminder','list.html')
    queryset = models.CalendarReminder.objects.all()
    filterset_class = filters.CalendarReminderFilter
    paginate_by = 20

    def get_context_data(self, **kwargs):
        today = datetime.date.today()
        context = super().get_context_data(**kwargs)
        context["calendar_url"] = f'/calendar/month/{today.year}/{today.month}'
        return context
    


class CalendarReminderDetailView(DetailView):
    template_name = os.path.join('reports','reminder', 'detail.html')
    model = models.CalendarReminder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date"] = datetime.date.today()
        return context
    



class MileageReminderCreateView(ContextMixin, CreateView):
    template_name =CREATE_TEMPLATE
    form_class = forms.MileageReminderForm
    model = models.MileageReminder
    success_url = reverse('reports:mileage-reminders-list')
    context = {
        'title': 'Generate Mileage Reminder'
    }

    def get_initial(self):
        config = Config.objects.first()
        return {
            'reminder_email': config.default_reminder_email
        }

   

class MileageReminderUpdateView(ContextMixin, UpdateView):
    template_name =CREATE_TEMPLATE
    form_class = forms.MileageReminderForm
    queryset = models.MileageReminder.objects.all()
    success_url = reverse('reports:mileage-reminders-list')
    context = {
        'title': 'Update Mileage Reminder'
    }

class MileageReminderListView(PaginationMixin, FilterView):
    template_name = os.path.join('reports', 'reminder','mileage_list.html')
    queryset = models.MileageReminder.objects.all()
    filterset_class = filters.MileageReminderFilter
    paginate_by = 20


class MileageReminderDetailView(DetailView):
    template_name = os.path.join('reports','reminder', 'mileage_detail.html')
    model = models.MileageReminder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current"] = self.object.current_mileage()
        context['covered'] = context['current'] - \
            self.object.last_reminder_mileage
        return context
    


class MileageReminderAlertCreateView(ContextMixin ,CreateView):
    template_name = os.path.join('common', 'frame_create_template.html')
    form_class = forms.MileageReminderAlertForm
    context = {
        'title': 'Add Mileage Reminder Alert'
    }

    def get_initial(self):
        return {
            'reminder': self.kwargs['pk']
        }

class CalendarReminderAlertCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common', 'frame_create_template.html')
    form_class = forms.CalendarReminderAlertForm
    context = {
        'title': 'Add Calendar Reminder Alert'
    }

    def get_initial(self):
        return {
            'reminder': self.kwargs['pk']
        }