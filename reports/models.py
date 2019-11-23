from django.db import models
from django.shortcuts import reverse
import datetime
import requests 
from common.models import Config
import logging
import json

logging.basicConfig(filename='background.log', level=logging.WARN)


class VehicleService(models.Model):
    FREQUENCY = [
        1, 7, 30, 90, 180
    ]
    REPEAT_METHOD = [
        (0, 'Never'),
        (1, 'After an Interval of Time'),
        (2, 'After a given Mileage'),
        (3, 'Whichever comes first'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    repeat_method = models.PositiveSmallIntegerField(choices=REPEAT_METHOD)
    frequency_time = models.IntegerField()
    interval_mileage= models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/app/"
    

class VehicleServiceLog(models.Model):
    date = models.DateField()
    odometer = models.IntegerField()
    vendor = models.CharField(max_length=255)
    notes = models.ManyToManyField('reports.Note', blank=True)
    vehicle = models.ForeignKey('reports.Vehicle', on_delete=models.CASCADE)
    service = models.ForeignKey('reports.VehicleService', 
        on_delete=models.CASCADE)


    def __str__(self):
        return "%s: %s" % ( self.date, self.service)

class VehicleCertificateOfFitness(models.Model):
    date = models.DateField()
    vehicle = models.ForeignKey('reports.Vehicle', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    notes = models.ManyToManyField('reports.Note', blank=True)
    valid_until = models.DateField()


    @property
    def valid(self):
        return datetime.date.today() < self.valid_until

    def get_absolute_url(self):
        return "/app/"
    

class DriverMedical(models.Model):
    date = models.DateField()
    driver = models.ForeignKey('reports.Driver', on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    notes = models.ManyToManyField('reports.Note', blank=True)
    valid_until = models.DateField()

    @property
    def valid(self):
        return datetime.date.today() < self.valid_until


class DDC(models.Model):
    driver = models.ForeignKey('reports.Driver', 
        on_delete=models.CASCADE)
    expiry_date = models.DateField()
    number = models.CharField(max_length=16, blank=True)

    @property
    def valid(self):
        return datetime.date.today() < self.expiry_date

class Insurance(models.Model):
    COVERAGE = [
        ('comprehensive', 'Comprehensive'),
        ('third-party', 'Third Party'),
    ]
    vendor = models.CharField(max_length=255)
    coverage = models.CharField(choices=COVERAGE, max_length=32)
    valid_until = models.DateField()
    vehicle = models.ForeignKey('reports.Vehicle', on_delete=models.CASCADE)
    notes = models.ManyToManyField('reports.note', blank=True)

    @property
    def valid(self):
        return datetime.date.today() < self.valid_until

    def get_absolute_url(self):
        return "/app/"
    
class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('earth-mover', 'Earth Moving Equipment'),
    ]
    device_id = models.CharField(max_length=64)
    vehicle_id = models.CharField(max_length=64)
    registration_number = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=16, choices=VEHICLE_TYPES)
    make = models.CharField(max_length=32, blank=True)
    model = models.CharField(max_length=32, blank=True)
    year = models.IntegerField(blank=True, null=True)
    seats = models.IntegerField(blank=True, null=True)
    loading_capacity_tons = models.FloatField(blank=True, null=True) 
    notes = models.ManyToManyField('reports.Note', blank=True)


    def __str__(self):
        return self.name

    @property
    def reminders(self):
        return self.reminder_set.all()

    def get_absolute_url(self):
        return reverse("reports:vehicle-details", kwargs={"pk": self.pk})
    
    @property
    def incidents(self):
        return self.incident_set.all().order_by('date')

    @property 
    def insurance(self):
        return self.insurance_set.all().order_by('valid_until')

    @property
    def fitness_certificates(self):
        return self.vehiclecertificateoffitness_set.all().order_by(
            'valid_until')

    @property
    def drivers(self):
        return self.driver_set.all()

    @property
    def service_logs(self):
        return self.vehicleservicelog_set.all().order_by('date')


    def get_status(self):
        config = Config.objects.first()
        # connect to the API
        try:
            resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_login.action', params={
                'account':config.conn_account,
                'password':config.conn_password
            })
        except:
            return 
        if resp.status_code != 200:
            logging.critical('Failed to login for obtaining vehicle #{} status'.format(self.vehicle_id))
            return

        session = json.loads(resp.content)['jsession']

        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_getDeviceStatus.action', params={
            'jsession':session,
            'devIdno':self.device_id,
        })

        if resp.status_code != 200:
            logging.critical('Failed to retrieve status for vehicle #{}'.format(self.vehicle_id))
            return

        return json.loads(resp.content)['status']


class Driver(models.Model):
    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    CLASSES = [(i, i) for i in range(1,6)]

    first_names = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True,choices=GENDER)
    phone_number = models.CharField(max_length=16, blank=True)
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=16, blank=True)
    license_issuing_date = models.DateField(null=True, blank=True)
    license_class = models.IntegerField(default=1, blank=True)
    photo = models.ImageField(null=True, blank=True, upload_to='driver_photos/')
    vehicles = models.ManyToManyField('reports.Vehicle', blank=True)
    notes = models.ManyToManyField('reports.Note', blank=True)

    def get_absolute_url(self):
        return reverse("reports:driver-details", kwargs={"pk": self.pk})
    
    def __str__(self):
        return f'{self.first_names}, {self.last_name}'
    
    @property
    def ddc_valid(self):
        for ddc in self.ddc_list:
            if ddc.valid:
                return True
        return False

    @property
    def ddc_list(self):
        return self.ddc_set.all()
    
    @property
    def medicals(self):
        return self.drivermedical_set.all().order_by('valid_until')
    
    @property
    def age(self):
        if not self.date_of_birth:
            return 0
        return int((datetime.date.today()- self.date_of_birth).days / 365)

    @property
    def incidents(self):
        return self.incident_set.all().order_by('date')

class Note(models.Model):
    date = models.DateField(auto_now=True)
    author = models.CharField(max_length=32)
    subject = models.CharField(max_length=255, blank=True)
    note = models.TextField()

class Incident(models.Model):
    driver = models.ForeignKey('reports.Driver', on_delete=models.CASCADE)
    date = models.DateField()
    vehicle = models.ForeignKey('reports.Vehicle', on_delete=models.CASCADE)
    description = models.TextField()
    report = models.FileField(upload_to='incident_reports/', null=True, 
        blank=True)
    number_of_vehicles_involved = models.IntegerField(default=0)
    number_of_pedestrians_involved = models.IntegerField(default=0)
    location = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "%s(%s)" %(self.driver, self.vehicle)

    def get_absolute_url(self):
        return reverse("reports:vehicle-details", kwargs={"pk": self.vehicle.pk})

class ReminderEvent(models.Model):
    EVENT_CHOICES = [
        (0, 'Date'),
        (1, 'Days Before'),
        (2, 'Mileage'),
    ]
    
    reminder = models.ForeignKey('reports.reminder', on_delete=models.CASCADE)
    #remind on a specific date
    date = models.DateField(blank=True, null=True)
    #remind days before the event
    days_before = models.IntegerField(default=0.0)
    # remind a certain mileage before the event
    mileage = models.FloatField(default=0.0)

    event_type = models.PositiveSmallIntegerField(default=0,
        choices=EVENT_CHOICES)
    
    @property
    def type_str(self):
        mapping = dict(self.EVENT_CHOICES)
        return mapping[self.event_type]

    @property
    def value(self):
        mapping = {
            0: self.date,
            1: self.days_before,
            2: self.mileage
        }
        return mapping[self.event_type]

class Reminder(models.Model):
    
    vehicle = models.ForeignKey('reports.vehicle', 
        on_delete=models.CASCADE,
        null=True)
    driver = models.ForeignKey('reports.driver', 
        on_delete=models.CASCADE,
        blank=True,
        null=True)

    # reminder date
    date = models.DateField()

    reminder_type = models.ForeignKey('reports.ReminderCategory', default=1, 
        on_delete=models.SET_DEFAULT)

    #repeat event after a number of days
    repeat_after_days = models.BooleanField(default=False)
    interval_days = models.IntegerField(default=180)
    # repeat event after a certain mileage
    repeat_after_mileage = models.BooleanField(default=False)
    interval_mileage = models.IntegerField(default=5000)
    
    reminder_email = models.EmailField()
    reminder_message = models.TextField()
    active = models.BooleanField(default=True)
    last_reminder = models.DateField(null=True, blank=True)
    last_reminder_mileage = models.IntegerField(default=0)
    

    @property
    def next_reminder(self):
        today = datetime.date.today()
        if not self.repeat_after_days:
            return self.date

        if self.last_reminder:
            return self.last_reminder + \
                datetime.timedelta(days=self.interval_days)


    def repeat_on_date(self, date):
        if date > self.date:
            delta = (date - self.date).days
            if self.interval_days and delta % self.interval_days == 0:
                return True
            
        return False

    @property
    def event_at_mileage(self):
        return self.mileage_till_event <= 0

    @property
    def mileage_since_reminder(self):
        status = self.vehicle.get_status()
        if status:
            current_mileage = status['lc'] / 1000.0
            return current_mileage - self.last_reminder_mileage
    
        return -1
    
    @property
    def mileage_till_event(self):
        covered = self.mileage_since_reminder
        if covered != -1:
            return self.interval_mileage - covered
        
        return -1

    @property 
    def label(self):
        if self.driver:
            return str(self.driver)
        elif self.vehicle:
            return self.vehicle.name
        return ''

    def __str__(self):
        return self.label

    def save(self, **kwargs):

        if self.pk is None:
            #record the current mileage
             #get parameters from config
            status = self.vehicle.get_status()
            if status:
                self.last_reminder_mileage = status['lc'] / 1000
            else:
                logging.critical('could not obtain the current mileage for setting a reminder for vehicle {}'.format(self.vehicle.vehicle_id))

        super().save(**kwargs)


        
class ReminderCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Alarm(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    description = models.TextField()
    vehicle = models.ForeignKey('reports.vehicle', on_delete=models.CASCADE)
    

    