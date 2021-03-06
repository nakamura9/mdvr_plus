from django.views.generic import (TemplateView, 
                                  CreateView, 
                                  DetailView, 
                                  ListView,
                                  UpdateView,
                                  FormView
                                  )

from reports import forms, models, filters
import os
from common.mixins import ContextMixin, PaginationMixin
from django.urls import reverse_lazy as reverse
from django_filters.views import FilterView
from common.models import Config
from common import api
from django.apps import apps
import datetime
from django.http import HttpResponse, JsonResponse
import requests
import json
import urllib
from reports.models import Alarm
from reports.serializers import (AlarmSerializer, 
                                 CalendarReminderAlertSerializer,
                                 MileageReminderAlertSerializer,
                                 )
from django.db.utils import OperationalError
from rest_framework.viewsets import ModelViewSet

CREATE_TEMPLATE = os.path.join('common', 'create.html')


from reports.report_views import (SpeedingPDFReport, 
                                  SpeedingReport, 
                                  HarshBrakingPDFReport, 
                                  HarshBrakingReport,
                                  harsh_braking_csv_report,
                                  speeding_report_csv,
                                )


class VehicleCreateView(ContextMixin, CreateView):
    model = models.Vehicle
    form_class= forms.VehicleForm
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Create Vehicle'
    }

class VehicleDetailView(ContextMixin, DetailView):
    model = models.Vehicle
    template_name = os.path.join('reports', 'vehicle','detail.html')
    context = {
        'app': 'reports',
        'model': 'vehicle'
    }
class VehicleUpdateView(ContextMixin, UpdateView):
    form_class = forms.VehicleForm
    queryset = models.Vehicle.objects.all()
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Update Vehicle Information'
    }

class VehicleListView(ContextMixin, FilterView):
    filterset_class = filters.VehicleFilter
    queryset = models.Vehicle.objects.all()
    paginate_by = 20
    template_name = os.path.join('reports', 'vehicle', 'list.html')
    context = {
        'title': 'Vehicle List',
        'action_list': [
            {
                'link': reverse('reports:create-vehicle'),
                'icon': 'pen',
                'label': 'Create New Vehicle'
            }
        ]
    }


    
class ReportFormView(ContextMixin,FormView):
    form_class=forms.ReportForm
    template_name = os.path.join('reports', 'report_form.html')
    success_url = reverse('app:home')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['action'] = self.kwargs['action']
        return context
    




class CalendarView(TemplateView):
    template_name = os.path.join('reports','calendar.html')


class NoteCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common', 'frame_create_template.html')
    model = models.Note
    form_class = forms.NoteForm
    success_url = '/app/'

    def form_valid(self, form):
        resp = super().form_valid(form)
        
        model = apps.get_model(self.kwargs['app'], self.kwargs['model'])
        item = model.objects.get(pk=self.kwargs['pk'])
        item.notes.add(self.object)

        return resp 
    

class DriverCreateView(ContextMixin, CreateView):
    form_class = forms.DriverForm
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Create Driver'
    }

class DriverListView(ContextMixin, FilterView):
    queryset = models.Driver.objects.all()
    template_name = os.path.join('reports', 'driver', 'list.html')
    filterset_class = filters.DriverFilter
    paginate_by = 20
    context = {
        'title': 'Driver List',
        'action_list': [
            {
                'link': reverse('reports:create-driver'),
                'icon': 'user',
                'label': 'Create Driver'
            }
        ]
    }
class DriverDetailView(ContextMixin, DetailView):
    model = models.Driver
    template_name = os.path.join('reports', 'driver', 'detail.html')
    context = {
        'app': 'reports',
        'model': 'driver'
    }
class DriverUpdateView(ContextMixin, UpdateView):
    form_class = forms.DriverForm
    template_name = CREATE_TEMPLATE
    context = {
        'title': 'Update Driver'
    }
    model = models.Driver

class CreateInsurance(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.InsuranceForm
    context = {
        'title': 'Create Insurance'
    }

    def get_initial(self):
        return {
            'vehicle': self.kwargs['pk']
        }

    @staticmethod
    def create_reminder(self, form):
        models.CalendarReminder.objects.create(
            vehicle=self.object.vehicle,
            date=self.object.valid_until - datetime.timedelta(
                days=int(form.cleaned_data['reminder_days'])),
            repeatable=False,
            reminder_email=Config.objects.first().default_reminder_email,
            reminder_message="""
            The insurance for vehicle {} will expire within {} days.
            Please renew.
            """.format(self.object.vehicle, form.cleaned_data['reminder_days'])
        )

    def form_valid(self, form):
        resp = super().form_valid(form)
        CreateInsurance.create_reminder(self, form)
        
        return resp

class UpdateInsurance(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.InsuranceForm
    model = models.Insurance
    context = {
        'title': 'Update Insurance'
    }

    def form_valid(self, form):
        resp = super().form_valid(form)
        if not models.CalendarReminder.objects.filter(
                vehicle=self.object.vehicle, 
                date=self.object.valid_until - datetime.timedelta(
                    days=int(form.cleaned_data['reminder_days']))).exists():
            CreateInsurance.create_reminder(self, form)
        return resp


class CreateFitnessCertificate(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.FitnessCertificateForm
    context = {
        'title': 'Create Certificate of Fitness'
    }

    def get_initial(self):
        return {
            'vehicle': self.kwargs['pk']
        }

    @staticmethod
    def create_reminder(self, form):
        models.CalendarReminder.objects.create(
            vehicle=self.object.vehicle,
            date=self.object.valid_until - datetime.timedelta(
                days=int(form.cleaned_data['reminder_days'])),
            repeatable=False,
            reminder_email=Config.objects.first().default_reminder_email,
            reminder_message="""
            The certificate of fitness for vehicle {} will expire within {} days.
            Please renew.
            """.format(self.object.vehicle, form.cleaned_data['reminder_days'])
        )

    def form_valid(self, form):
        resp = super().form_valid(form)
        CreateInsurance.create_reminder(self, form)
        
        return resp

class UpdateFitnessCertificate(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.FitnessCertificateForm
    model = models.VehicleCertificateOfFitness
    context = {
        'title': 'Update Certificate of Fitness'
    }

    def form_valid(self, form):
        resp = super().form_valid(form)
        if not models.CalendarReminder.objects.filter(
                vehicle=self.object.vehicle, 
                date=self.object.valid_until - datetime.timedelta(
                    days=int(form.cleaned_data['reminder_days']))).exists():
            CreateFitnessCertificate.create_reminder(self, form)
        return resp

class CreateServiceLog(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ServiceLogForm
    context = {
        'title': 'Create Service Log'
    }

    def get_success_url(self):
        return reverse('reports:vehicle-details', kwargs={
            'pk': self.kwargs['pk']
        })

    def get_initial(self):
        return {
            'vehicle': self.kwargs['pk']
        }


    def form_valid(self, form):
        resp = super().form_valid(form)
        service = self.object.service

        if service.repeat_method == 1:
            models.CalendarReminder.objects.create(
                vehicle=self.object.vehicle,
                date=self.object.date + datetime.timedelta(days=
                    service.frequency_time),
                repeatable=False,
                reminder_email=Config.objects.first().default_reminder_email,
                reminder_message="""
                The vehicle is due for the following service: {}
                .
                """.format(service)
            )
        else:
            models.MileageReminder.objects.create(
                vehicle=self.object.vehicle,
                repeat_interval_mileage=service.interval_mileage,
                repeatable=False,
                reminder_email=Config.objects.first().default_reminder_email,
                reminder_message="""
                The vehicle will due for the following service: {}
                after {}km.
                """.format(service, service.interval_mileage)
            )
        return resp

class CreateVehicleService(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ServiceForm
    context = {
        'title': 'Create Service'
    }

class UpdateVehicleService(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ServiceForm
    model = models.VehicleService
    context = {
        'title': 'Update Service'
    }


class CreateIncident(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IncidentForm
    context = {
        'title': 'Create Incident'
    }

    def get_initial(self):
        return {
            'vehicle': self.kwargs['pk']
        }

class UpdateIncident(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.IncidentForm
    model = models.Incident
    context = {
        'title': 'Update Incident Details'
    }

class CreateMedical(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.MedicalForm
    context = {
        'title': 'Create Medical'
    }

    def get_initial(self):
        return {
            'driver': self.kwargs['pk']
        }
    
    def form_valid(self, form):
        resp = super().form_valid(form)

        models.CalendarReminder.objects.create(
                driver=self.object.driver,
                date=self.object.valid_until + datetime.timedelta(days=
                    int(form.cleaned_data['reminder_days'])),
                repeatable=False,
                reminder_email=Config.objects.first().default_reminder_email,
                reminder_message="""
                {} is due for another medical in {} days
                .
                """.format(self.object.driver, 
                            form.cleaned_data['reminder_days'])
            )

        return resp
    def get_success_url(self):
        return reverse('reports:driver-details', kwargs={
            'pk': self.kwargs['pk']
        })

class CreateDDC(ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.DDCFrom
    context = {
        'title': 'Record Defensive Driving Certificate'
    }

    def get_initial(self):
        return {
            'driver': self.kwargs['pk']
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = models.Driver.objects.get(pk=self.kwargs['pk'])
        return context 
    
    def get_success_url(self):
        return reverse('reports:driver-details', kwargs={
            'pk': self.kwargs['pk']
        })

    def form_valid(self, form):
        resp = super().form_valid(form)

        models.CalendarReminder.objects.create(
                driver=self.object.driver,
                date=self.object.expiry_date + datetime.timedelta(days=
                    int(form.cleaned_data['reminder_days'])),
                repeatable=False,
                reminder_email=Config.objects.first().default_reminder_email,
                reminder_message="""
                {}'s defensive driving certificate will expire in {} days.
                Please renew.
                """.format(self.object.driver, 
                            form.cleaned_data['reminder_days'])
            )

        return resp

class CreateReminderCategory(ContextMixin, CreateView):
    context = {
        'title': 'Create Reminder Category'
    }
    template_name = CREATE_TEMPLATE
    form_class = forms.ReminderCategoryForm
    success_url = reverse('reports:reminders-list')

class ImportVehiclesView(TemplateView):
    template_name = os.path.join('reports', 'import.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        config = Config.objects.first()
        # connect to the API
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_login.action', params={
            'account':config.conn_account,
            'password':config.conn_password
        })
        if resp.status_code != 200:
            context['errors'] = f'An error prevented the application from' + \
            f' communicating with the application server: code {resp.status_code}'
            return context
        # store session id 
        data = json.loads(resp.content)
        if data['result'] != 0:
            context['errors'] = 'The server returned with an error'
            return context

        session = data['jsession']
        # get the list of records
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_getDeviceOlStatus.action', params={
            'jsession':session
        })
        data = json.loads(resp.content)
        if data['result'] != 0:
            context['errors'] = 'An error prevented a suitable response from being returned'
            return context
        
        context['imported'] = []
        for v in data['onlines']:
            if models.Vehicle.objects.filter(vehicle_id=v['vid']).exists():
                continue
            vehicle = models.Vehicle.objects.create(
                vehicle_id=v['vid'],
                device_id=v['did'],
                name=v['vid'],
                vehicle_type='truck'
            )

            context['imported'].append(vehicle)


        return context
        

def retrieve_alarms(request):
    # delete all alarms older than 5 minutes 
    now = datetime.datetime.now()
    threshold = now - datetime.timedelta(seconds=300)
    Alarm.objects.filter(timestamp__lte=threshold).delete()

    # raise all alarms from the last minute
    minute = now - datetime.timedelta(seconds=60)
    current = Alarm.objects.filter(timestamp__gte=minute)
    data = AlarmSerializer(current, many=True).data

    return JsonResponse(data, safe=False)


class GPSView(TemplateView):
    template_name = os.path.join('reports', 'gps.html')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context.update({
            'lat': self.kwargs['lat'],
            'lng': self.kwargs['lng']
        })
        
        return context

class CalendarReminderAlertViewset(ModelViewSet):
    serializer_class = CalendarReminderAlertSerializer
    queryset = models.CalendarReminderAlert.objects.all()

class MileageReminderAlertViewset(ModelViewSet):
    serializer_class = MileageReminderAlertSerializer
    queryset = models.MileageReminderAlert.objects.all()


class UpcomingRemindersViews(TemplateView):
    template_name = os.path.join('reports', 'reminder', 'upcoming.html')

    def get_context_data(self, **kwargs):
        #load reminders asynchronously for distance reminders
        context = super().get_context_data(**kwargs)
        today = datetime.date.today()
        reminders = models.CalendarReminder.objects.filter(
            active=True)
        print(reminders)
        today_events = [i for i in reminders if i.repeat_on_date(today)] + [
            i for i in reminders.filter(date=today)
        ]

        seven_days = [i for i in reminders \
            if abs((today - i.next_reminder_date).days) < 8 and \
                abs((today - i.next_reminder_date).days) > 1]
        thirty_days = [i for i in reminders \
            if abs((today - i.next_reminder_date).days) > 8 and \
                abs((today - i.next_reminder_date).days) < 31]
        
        context.update({
            'today': today_events,
            'seven': seven_days,
            'thirty': thirty_days 
        })
        
        return context