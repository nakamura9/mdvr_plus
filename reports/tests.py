from django.test import TestCase, Client
from reports import models 
import datetime
from common.models import Config
from django.test.client import RequestFactory
from django.shortcuts import reverse
from test_server.server import (run_test_server, 
                                stop_test_server, 
                                MyWSGIRefServer)
import threading
import subprocess
import os
from bs4 import BeautifulSoup
from reports.views import (HarshBrakingPDFReport,
                           SpeedingPDFReport)

from reports.daily_reports import ( generate_daily_speeding_report,
                                    generate_daily_harsh_braking_summary
                                  )


class ModelTests(TestCase):
    fixtures = ['common.json','reminders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        #load test server
        os.chdir('test_server')
        cls.proc = subprocess.Popen(['python', 'server.py'])
        os.chdir('..')
        

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.proc.terminate()#TODO fix, fails to close open sockets


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
        self.assertIsInstance(self.vehicle.get_status(), list)

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

    def test_driver_age(self):
        self.assertGreater(self.driver.age, 29)

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

    def create_reminder(self):
        return models.Reminder.objects.create(
            vehicle=self.vehicle,
            driver=self.driver,
            date=datetime.date.today(),
            reminder_email='test@mail.com',
            reminder_message='some message'
        )

    def test_reminder(self):
        obj = self.create_reminder()
        self.assertIsInstance(obj, models.Reminder)

    def test_reminder_repeat_on_date(self):
        obj = self.create_reminder()
        self.assertFalse(obj.repeat_on_date(datetime.date.today()))
        self.assertTrue(obj.repeat_on_date(
            datetime.date.today() + datetime.timedelta(days=obj.interval_days)))

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


class ViewTests(TestCase):
    fixtures = ['common.json', 'reminders.json']

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
            vehicle_id='1000',
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

        cls.insurance = models.Insurance.objects.create(
            vendor='Vendor',
            coverage='comprehensive',
            valid_until=datetime.date.today() + datetime.timedelta(days=100),
            vehicle=cls.vehicle
        )

        cls.fitness_certificate = \
                models.VehicleCertificateOfFitness.objects.create(
                    date=datetime.date.today(),
                    location='somewhere',
                    vehicle=cls.vehicle,
                    valid_until=datetime.date.today() + \
                        datetime.timedelta(days=100),
                )

        cls.reminder = models.Reminder.objects.create(
            vehicle=cls.vehicle,
            driver=cls.driver,
            date=datetime.date.today(),
            reminder_email='test@mail.com',
            reminder_message='some message'
        )

        cls.incident = models.Incident.objects.create(
            driver = cls.driver,
            date= datetime.date.today(),
            vehicle=cls.vehicle,
            description='description'
        )

        return super().setUpTestData()
        

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        os.chdir('test_server')
        cls.proc = subprocess.Popen(['python', 'server.py'])
        os.chdir('..')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.proc.terminate()#TODO fix, fails to close open sockets

    #drivers
    def test_get_create_driver_view(self):
        resp = self.client.get(reverse('reports:create-driver'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_driver_view(self):
        resp = self.client.post(reverse('reports:create-driver'), data={
            'last_name': 'test',
            'first_names': 'johnny'
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_update_driver_view(self):
        resp = self.client.get(reverse('reports:update-driver', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_driver_view(self):
        resp = self.client.post(reverse('reports:update-driver', kwargs={
            'pk': 1
        }), data={'last_name': 'test','first_names': 'johnny'})
        self.assertEqual(resp.status_code, 302)

    def test_get_driver_list_view(self):
        resp = self.client.get(reverse('reports:list-drivers'))
        self.assertEqual(resp.status_code, 200)

    def test_get_driver_details(self):
        resp = self.client.get(reverse('reports:driver-details', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_create_medical_view(self):
        resp = self.client.get(reverse('reports:create-medical', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_medical_view(self):
        resp = self.client.post(reverse('reports:create-medical', kwargs={
            'pk': 1
        }), data={
            'driver': 1,
            'location': 'place',
            'date': datetime.date.today(),
            'valid_until': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5

        })
        self.assertEqual(resp.status_code, 302)


    def test_get_create_ddc_view(self):
        resp = self.client.get(reverse('reports:create-ddc', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_ddc_view(self):
        
        resp = self.client.post(reverse('reports:create-ddc', kwargs={
            'pk': 1
        }), data={
            'driver': 1,
            'expiry_date': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5
        })
        self.assertEqual(resp.status_code, 302)

    #insurance
    def test_get_create_insurance_view(self):
        resp = self.client.get(reverse('reports:create-insurance', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_insurance_view(self):
        resp = self.client.post(reverse('reports:create-insurance', kwargs={
            'pk': 1
        }), data={
            'vendor': 'Someone',
            'coverage': 'comprehensive',
            'valid_until': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5,
            'vehicle': 1
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_insurance_update_view(self):
        resp = self.client.get(reverse('reports:update-insurance', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_insurance_update_view(self):
        resp = self.client.post(reverse('reports:update-insurance', kwargs={
            'pk': 1
        }), data={
            'vendor': 'Someone',
            'coverage': 'comprehensive',
            'valid_until': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5,
            'vehicle': 1
        })
        self.assertEqual(resp.status_code, 302)

    #incidents
    def test_get_create_incident_view(self):
        resp = self.client.get(reverse('reports:create-incident', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_incident_view(self):
        resp = self.client.post(reverse('reports:create-incident', kwargs={
            'pk': 1
        }), data={
            'driver': 1,
            'vehicle': 1,
            'description': 'something',
            'date': datetime.date.today(),
            'number_of_vehicles_involved': 1,
            'number_of_pedestrians_involved': 0
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_update_incident_view(self):
        resp = self.client.get(reverse('reports:update-incident', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_incident_view(self):
        resp = self.client.post(reverse('reports:update-incident', kwargs={
            'pk': 1
        }), data={
            'driver': 1,
            'vehicle': 1,
            'description': 'something',
            'date': datetime.date.today(),
            'number_of_vehicles_involved': 1,
            'number_of_pedestrians_involved': 0
        })
        self.assertEqual(resp.status_code, 302)

    #certificates of fitness
    def test_get_create_fitness_certificate(self):
        resp = self.client.get(reverse('reports:create-fitness-certificate',
            kwargs={
                'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)


    def test_post_create_fitness_certificate(self):
        resp = self.client.post(reverse('reports:create-fitness-certificate',
            kwargs={
                'pk': 1
        }), data={
            'vehicle': 1,
            'location': 'location',
            'date': datetime.date.today(),
            'valid_until': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_update_fitness_certificate(self):
        resp = self.client.get(reverse('reports:update-fitness-certificate',
            kwargs={
                'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_fitness_certificate(self):
        resp = self.client.post(reverse('reports:update-fitness-certificate',
            kwargs={
                'pk': 1
        }), data={
            'vehicle': 1,
            'location': 'location',
            'date': datetime.date.today(),
            'valid_until': datetime.date.today() + datetime.timedelta(days=100),
            'reminder_days': 5
        })
        self.assertEqual(resp.status_code, 302)

    #service
    def test_get_create_vehicle_service(self):
        resp = self.client.get(reverse('reports:create-service'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_vehicle_service(self):
        resp = self.client.post(reverse('reports:create-service'), data={
            'name': 'name',
            'description': 'service',
            'repeat_method': 1,
            'frequency_time': 5,
            'interval_mileage': 0
        })
        self.assertEqual(resp.status_code, 302)
        
    def test_get_create_service_log(self):
        resp = self.client.get(reverse('reports:create-service-log', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_service_log(self):
        resp = self.client.post(reverse('reports:create-service-log', kwargs={
            'pk': 1
        }), data={
            'vehicle': 1,
            'vendor': 'vendor',
            'date': datetime.date.today(),
            'odometer': 1232143,
            'service': 1
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_update_service_view(self):
        resp = self.client.get(reverse('reports:update-service', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_service_view(self):
        resp = self.client.post(reverse('reports:update-service', kwargs={
            'pk': 1
        }), data={
            'name': 'name',
            'description': 'service',
            'repeat_method': 1,
            'frequency_time': 5,
            'interval_mileage': 5
        })
        self.assertEqual(resp.status_code, 302)
        

    def test_get_create_note_view(self):
        resp = self.client.get(reverse('reports:create-note', kwargs={
            'app': 'reports',
            'model': 'insurance',
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_note(self):
        resp = self.client.post(reverse('reports:create-note', kwargs={
            'app': 'reports',
            'model': 'insurance',
            'pk': 1
        }), data={
            'author': 'some guy',
            'note': 'note'
        })
        self.assertEqual(resp.status_code, 302)
    
    def test_get_create_vehicle(self):
        resp = self.client.get(reverse('reports:create-vehicle'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_vehicle(self):
        resp = self.client.post(reverse('reports:create-vehicle'), data={
            'name': 'vehicle',
            'registration_number': 1000,
            'vehicle_type':'truck',
            'device_id': 100,
            'vehicle_id': 100
        })
        self.assertEqual(resp.status_code, 302)

    def test_import_vehicles(self):
        prev_count = models.Vehicle.objects.all().count()
        resp = self.client.get(reverse('reports:import-vehicles'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotEqual(models.Vehicle.objects.all().count(), prev_count)


    def test_get_list_vehicles(self):
        resp = self.client.get(reverse('reports:list-vehicles'))
        self.assertEqual(resp.status_code, 200)

    def test_get_update_vehicle_view(self):
        resp = self.client.get(reverse('reports:update-vehicle', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_vehicle_view(self):
        resp = self.client.post(reverse('reports:update-vehicle', kwargs={
            'pk': 1
        }), data={
            'name': 'vehicle',
            'registration_number': 1000,
            'vehicle_type':'truck',
            'device_id': 100,
            'vehicle_id': 100
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_vehicle_details_view(self):
        resp = self.client.get(reverse('reports:vehicle-details', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_create_reminder_view(self):
        resp = self.client.get(reverse('reports:create-reminder'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_reminder(self):
        resp = self.client.post(reverse('reports:create-reminder'), data={
            'vehicle': 1,
            'reminder_type': 1,
            'date': datetime.date.today(),
            'interval_days': 180,
            'interval_mileage': 5000,
            'reminder_email': 'kandoroc@gmail.com',
            'reminder_message': 'message',
            'last_reminder_mileage': 100,
            'reminder_method': 0,
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_create_reminder_category(self):
        resp = self.client.get(reverse('reports:create-reminder-category'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_reminder_category(self):
        resp = self.client.post(reverse('reports:create-reminder-category'),
            data={
                'name': 'Name'
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_reminder_list(self):
        resp = self.client.get(reverse('reports:reminders-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_update_reminder(self):
        resp = self.client.get(reverse('reports:update-reminder', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_reminder(self):
        resp = self.client.post(reverse('reports:update-reminder', kwargs={
            'pk': 1
        }), data={
            'vehicle': 1,
            'reminder_type': 1,
            'date': datetime.date.today(),
            'interval_days': 180,
            'interval_mileage': 5000,
            'reminder_email': 'kandoroc@gmail.com',
            'reminder_message': 'message',
            'last_reminder_mileage': 100,
            'reminder_method': 0
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_reminder_details(self):
        resp = self.client.get(reverse('reports:reminder-details', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_reminder_api(self):
        today = datetime.date.today()
        resp = self.client.get(f'/reports/api/month/{today.year}/{today.month}/')
        self.assertEqual(resp.status_code, 200)

    def test_get_report_form(self):
        resp = self.client.get(reverse('reports:report-form', kwargs={
            'action': 'harsh-braking-report'
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_harsh_braking_report(self):
        resp = self.client.get(reverse('reports:harsh-braking-report'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        self.assertEqual(resp.status_code, 200)
        #look out for the single record

    def test_get_harsh_braking_pdf(self):
        req = RequestFactory().get(reverse('reports:harsh-braking-pdf'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        req.session = {
            'current': 1,
            'pages': 1
        }
        resp = HarshBrakingPDFReport.as_view()(req)
        self.assertEqual(resp.status_code, 200)
        #look out for the single record

    def test_get_harsh_braking_csv(self):
        resp = self.client.get(reverse('reports:harsh-braking-csv'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        self.assertEqual(resp.status_code, 200)
        #look out for the single record

    def test_get_speeding_report(self):
        resp = self.client.get(reverse('reports:speeding-report'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        self.assertEqual(resp.status_code, 200)
        #look out for the single record

    def test_get_speeding_pdf(self):
        req = RequestFactory().get(reverse('reports:speeding-report'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        req.session = {
            'current': 1,
            'pages': 1
        }
        resp = SpeedingPDFReport.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_get_speeding_csv(self):
        resp = self.client.get(reverse('reports:speeding-csv'), data={
            'start': datetime.date.today() - datetime.timedelta(days=6),
            'end': datetime.date.today(),
            'vehicle': 1,
        })
        self.assertEqual(resp.status_code, 200)


    def test_get_alarms(self):
        resp = self.client.get(reverse('reports:alarms'))
        self.assertEqual(resp.status_code, 200)


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
