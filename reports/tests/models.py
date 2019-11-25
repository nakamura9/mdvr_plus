from django.test import TestCase, Client
from reports import models 
import datetime
from common.models import Config
from django.test.client import RequestFactory
from django.shortcuts import reverse
from test_server.server import (stop_test_server, 
                                MyWSGIRefServer)
import subprocess
import os
import signal
from reports.views import (HarshBrakingPDFReport,
                           SpeedingPDFReport)

from reports.daily_reports import ( generate_daily_speeding_report,
                                    generate_daily_harsh_braking_summary
                                  )

class MileageReminderModelTests(TestCase):
    fixtures = ['common.json', 'reminders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #load test server
        os.chdir('test_server')
        cls.proc = subprocess.Popen(['python', 'server.py'],
            stdout=subprocess.PIPE, shell=True, 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

        os.chdir('..')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.proc.send_signal(signal.CTRL_BREAK_EVENT)
        cls.proc.kill()
        

    @classmethod
    def setUpTestData(cls):
        cls.config = Config.objects.first()
        cls.config.conn_account= 'admin'
        cls.config.conn_password= 'admin'
        cls.config.server_domain= 'localhost'
        cls.config.server_port= 5000
        cls.config.save()
        cls.vehicle = models.Vehicle.objects.create(
            device_id='77779',
            vehicle_id='77779',
            registration_number='1000',
            name='T-1'
        )
        cls.reminder = models.MileageReminder(
            vehicle=cls.vehicle,
            reminder_type=models.ReminderCategory.objects.first(),
            repeatable=True,
            reminder_email='mail@test.com',
            reminder_message='msg',
            mileage=5000,
            repeat_interval_mileage=5000
        )

        cls.alert = models.MileageReminderAlert(
            reminder=cls.reminder,
            mileage=100
        )
        return super().setUpTestData()

    def test_create_reminder(self):
        self.assertIsInstance(self.reminder, models.MileageReminder)
        self.assertIsInstance(str(self.reminder), str)
    
    def test_current_mileage(self):
        self.assertEqual(self.reminder.current_mileage(), 100.0)


    def test_mileage_since_reminder(self):
        self.assertEqual(self.reminder.mileage_since_reminder(), 100.0)

    def test_mileage_till_reminder(self):
        self.assertEqual(self.reminder.mileage_till_reminder(), 4900.0)

    def test_reminder_at_mileage(self):
        self.assertFalse(self.reminder.reminder_at_mileage())

    def test_alert_at_mileage(self):
        self.assertTrue(self.reminder.alert_at_mileage)

    def test_update_last_reminder(self):
        last = self.reminder.last_reminder_mileage
        self.reminder.update_last_reminder()
        self.assertEqual(self.reminder.mileage_since_reminder(), 0)

    def test_create_reminder_alert(self):
        self.assertIsInstance(self.alert, models.MileageReminderAlert)

class CalendarReminderModelTests(TestCase):
    fixtures = ['common.json','reminders.json']

    @classmethod
    def setUpTestData(cls):

        cls.config = Config.objects.first()
        cls.config.conn_account= 'admin'
        cls.config.conn_password= 'admin'
        cls.config.server_domain= 'localhost'
        cls.config.server_port= 5000
        cls.config.save()

        cls.vehicle = models.Vehicle.objects.create(
            device_id='77779',
            vehicle_id='77779',
            registration_number='1000',
            name='T-1'
        )

    def create_reminder(self):
        return models.CalendarReminder.objects.create(
            vehicle=self.vehicle,
            date=datetime.date.today(),
            reminder_email='test@mail.com',
            reminder_message='some message',
            repeatable=True,
            repeat_interval_days=180
        )

    def create_alert(self):
        return models.CalendarReminderAlert.objects.create(
            reminder=self.create_reminder(),
            method=0,
            date=datetime.date.today()
        )

    def test_reminder(self):
        obj = self.create_reminder()
        self.assertIsInstance(obj, models.CalendarReminder)

    def test_reminder_repeat_on_date(self):
        obj = self.create_reminder()
        self.assertFalse(obj.repeat_on_date(datetime.date.today()))
        self.assertTrue(obj.repeat_on_date(
            datetime.date.today() + datetime.timedelta(days=obj.repeat_interval_days)))

    def test_next_reminder_date(self):
        obj = self.create_reminder()
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        self.assertEqual(obj.next_reminder_date, today)

        obj2 = self.create_reminder()
        obj2.date = yesterday
        obj2.last_reminder_date = yesterday
        obj2.repeat_interval_days = 1
        obj2.repeatable=True
        obj2.save()

        obj2 = models.CalendarReminder.objects.latest('pk')
        self.assertEqual(obj2.next_reminder_date, today)

    def test_create_calendar_reminder_alert(self):
        obj = self.create_alert()
        self.assertIsInstance(obj, models.CalendarReminderAlert)

    def test_calendar_alert_on_date(self):
        obj = self.create_alert()
        today = datetime.date.today()
        self.assertTrue(obj.reminder.alert_on_date(today))
        self.assertEqual(obj.alert_date, today)
        self.assertEqual(obj.value, today)
        self.assertIsInstance(obj.alert_type, str)

    def test_other_calendar_reminder_alert(self):
        today = datetime.date.today()
        obj = self.create_alert()
        rem = obj.reminder
        rem.date = today + datetime.timedelta(days=1)#tomorrow
        rem.save()

        obj.reminder = models.CalendarReminder.objects.get(pk=rem.pk)
        obj.method =1 #days before
        obj.days=1 #today
        obj.save()

        obj = models.CalendarReminderAlert.objects.get(pk=obj.pk)
        self.assertTrue(obj.reminder.alert_on_date(today))
        self.assertEqual(obj.alert_date, today)
        self.assertIsInstance(obj.alert_type, str)
        self.assertEqual(obj.value, 1)

class ModelTests(TestCase):
    fixtures = ['common.json','reminders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #load test server
        os.chdir('test_server')
        cls.proc = subprocess.Popen(['python', 'server.py'],
            stdout=subprocess.PIPE, shell=True, 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        os.chdir('..')
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.proc.send_signal(signal.CTRL_BREAK_EVENT)
        cls.proc.kill()


    @classmethod
    def setUpTestData(cls):

        cls.config = Config.objects.first()
        cls.config.conn_account= 'admin'
        cls.config.conn_password= 'admin'
        cls.config.server_domain= 'localhost'
        cls.config.server_port= 5000
        cls.config.save()

        cls.vehicle = models.Vehicle.objects.create(
            device_id='77779',
            vehicle_id='77779',
            registration_number='1000',
            name='T-1'
        )

        cls.vehicle_service =  models.VehicleService.objects.create(
            name='service',
            description='description',
            repeat_method=0,
            frequency_time=100,
        )

        cls.driver = models.Driver.objects.create(
            first_names='Test',
            last_name='Driver',
            date_of_birth = datetime.date(1989,2,15),
            gender='male',
            license_number='123456',
        )

        return super().setUpTestData()

    def test_create_vehicle_service(self):
        obj = self.vehicle_service
        self.assertIsInstance(obj, models.VehicleService)

    def create_service_log(self):
        return models.VehicleServiceLog.objects.create(
            date=datetime.date.today(),
            odometer=1000,
            vendor='Vendor',
            vehicle=self.vehicle,
            service=self.vehicle_service
        )

    def test_vehicle_service_log(self):
        obj = self.create_service_log()
        self.assertIsInstance(obj, models.VehicleServiceLog)

    def create_certificate_of_fitness(self):
        return models.VehicleCertificateOfFitness.objects.create(
            date=datetime.date.today(),
            location='somewhere',
            vehicle=self.vehicle,
            valid_until=datetime.date.today() + datetime.timedelta(days=100),
        )
    def test_vehicle_certificate_of_fitness(self):
        obj = self.create_certificate_of_fitness()
        self.assertIsInstance(obj, models.VehicleCertificateOfFitness)

    def create_medical(self):
        return models.DriverMedical.objects.create(
            date=datetime.date.today(),
            driver=self.driver,
            location='locaiton',
            valid_until=datetime.date.today() + datetime.timedelta(days=100)
        )

    def test_driver_medical(self):
        obj = self.create_medical()
        self.assertIsInstance(obj, models.DriverMedical)

    def create_ddc(self):
        return models.DDC.objects.create(
            driver=self.driver,
            expiry_date = datetime.date.today() + datetime.timedelta(days=100),
        )

    def test_ddc(self):
        obj = self.create_ddc()
        self.assertIsInstance(obj, models.DDC)
        self.assertTrue(obj.valid)

    def create_insurance(self):
        return models.Insurance.objects.create(
            vendor='Vendor',
            coverage='comprehensive',
            valid_until=datetime.date.today() + datetime.timedelta(days=100),
            vehicle=self.vehicle
        )

    def test_insurance(self):
        obj = self.create_insurance()

        self.assertIsInstance(obj, models.Insurance)
        self.assertTrue(obj.valid)


    def test_vehicle(self):
        self.assertIsInstance(self.vehicle, models.Vehicle)
        
    def test_get_vehicle_status(self):
        self.assertIsInstance(self.vehicle.get_status(), dict)

    def test_vehicle_incidents(self):
        self.create_incident()
        incidents = self.vehicle.incidents.count()
        self.assertNotEqual(incidents, 0)

    def test_vehicle_insurance(self):
        self.create_insurance()
        self.assertNotEqual(self.vehicle.insurance.count(), 0)


    def test_vehicle_fitness_certificates(self):
        self.create_certificate_of_fitness()
        certificates = self.vehicle.fitness_certificates.count()
        self.assertNotEqual(certificates, 0)

    def test_vehicle_drivers(self):
        self.driver.vehicles.add(self.vehicle)
        self.driver.save()
        self.assertNotEqual(self.vehicle.drivers.count(), 0)

    def test_vehicle_service_logs(self):
        self.create_service_log()
        self.assertNotEqual(self.vehicle.service_logs.count(), 0)
        log = models.VehicleServiceLog.objects.first()
        self.assertIsInstance(log.__str__(), str)

    def test_driver(self):
        self.assertIsInstance(self.driver, models.Driver)

    def test_driver_ddc_valid(self):
        self.create_ddc()
        self.assertTrue(self.driver.ddc_valid)

    def test_driver_ddc_list(self):
        self.create_ddc()
        self.assertNotEqual(self.driver.ddc_list.count(), 0)
        

    def test_driver_medicals(self):
        self.create_medical()
        self.assertNotEqual(self.driver.medicals.count(), 0)
        medical = models.DriverMedical.objects.first()
        self.assertTrue(medical.valid)

    def test_driver_age(self):
        self.assertGreater(self.driver.age, 29)
        dob = self.driver.date_of_birth
        self.driver.date_of_birth = None
        self.driver.save()

        self.assertEqual(self.driver.age, 0)
        self.driver.date_of_birth = dob
        self.driver.save()

    def test_driver_incidents(self):
        self.create_incident()
        self.assertNotEqual(self.driver.incidents.count(), 0)

    def test_note(self):
        obj = models.Note.objects.create(
            date=datetime.date.today(),
            author='aurthur',
            subject='excalibur',
            note='I call upon thee'
        )
        self.assertIsInstance(obj, models.Note)


    def create_incident(self):
        return models.Incident.objects.create(
            vehicle=self.vehicle,
            date=datetime.date.today(),
            driver=self.driver,
            description='some accident'
        )


    def test_incident(self):
        obj = self.create_incident()
        self.assertIsInstance(obj, models.Incident)


    def test_reminder_category(self):
        obj = models.ReminderCategory.objects.create(
            name='reminder',
            description='has a category'
        )
        self.assertIsInstance(obj, models.ReminderCategory)

    def test_alarm(self):
        obj = models.Alarm.objects.create(
            description='some alarm',
            vehicle=self.vehicle
        )
        self.assertIsInstance(obj, models.Alarm)





# class DailyReportTests(TestCase):
#     fixtures = ['common.json', 'reminders.json']


#     @classmethod
#     def setUpTestData(cls):

#         cls.config = Config.objects.first()
#         cls.config.conn_account= 'admin'
#         cls.config.conn_password= 'admin'
#         cls.config.server_domain= 'localhost'
#         cls.config.server_port= 5000
#         cls.config.smtp_server= 'localhost'
#         cls.config.smtp_port= 25
#         cls.config.email_address= 'test2@mail.com'
#         cls.config.email_password= 'pwd'
#         cls.config.save()


#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.client = Client()
#         os.chdir('test_server')
#         cls.proc = subprocess.Popen(['python', 'server.py'])
#         os.chdir('..')

#         #test email server
#         cls.mail_proc = subprocess.Popen(['python', 
#                             'common/test_mail_server.py'])
    

#     @classmethod
#     def tearDownClass(cls):
#         super().tearDownClass()
#         cls.proc.terminate()
#         cls.mail_proc.terminate()



#     def test_generate_daily_speeding_summary(self):
#         self.assertTrue(generate_daily_speeding_report())

#     def test_generate_harsh_braking_report(self):
#         self.assertTrue(generate_daily_harsh_braking_summary())
