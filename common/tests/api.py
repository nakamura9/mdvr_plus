from django.test import TestCase
from common.models import Config
from django.test import Client
from django.shortcuts import reverse
import datetime
from common import api
from reports import models
import os 
import signal
import subprocess


class ServicesTests(TestCase):
    fixtures = ['common.json', 'reminders.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        os.chdir('common')
        print('###')
        cls.proc = subprocess.Popen(['python', 'test_mail_server.py'],
            stdout=subprocess.PIPE, shell=True, 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        os.chdir('..')
        os.chdir('test_server')
        print('### server.py')
        cls.proc_srv = subprocess.Popen(['python', 'server.py'],
            stdout=subprocess.PIPE, shell=True, 
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        os.chdir('..')
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.proc.send_signal(signal.CTRL_BREAK_EVENT)
        cls.proc.kill()
        cls.proc_srv.send_signal(signal.CTRL_BREAK_EVENT)
        cls.proc_srv.kill()

    @classmethod
    def setUpTestData(cls):
        cls.vehicle = models.Vehicle.objects.create(
            device_id='77779',
            vehicle_id='77779',
            registration_number='1000',
            name='T-1'
        )

        cls.reminder = models.CalendarReminder.objects.create(
            vehicle=cls.vehicle,
            date=datetime.date.today(),
            reminder_message='some message',
            repeatable=True,
            repeat_interval_days=180,
            reminder_email = 'reminder@localhost'
        )

        cls.mileage_reminder = models.MileageReminder.objects.create(
            vehicle=cls.vehicle,
            mileage=0,
            reminder_message='some message',
            repeatable=True,
            repeat_interval_mileage=5000,
            reminder_email = 'reminder@localhost'
        )

        cls.config = Config.objects.first()
        cls.config.conn_account= 'admin'
        cls.config.conn_password= 'admin'
        cls.config.server_domain= 'localhost'
        cls.config.server_port= 5000
        cls.config.smtp_server = 'localhost'
        cls.config.smtp_port = 1025
        cls.config.email_address = 'mail@localhost'
        cls.config.email_password = '1025'
        cls.config.save()

        return super().setUpTestData()

    def test_create_toast(self):
        self.assertEqual(api.create_toast_notification(self.reminder), 0)

    def test_send_reminder_email(self):
        self.assertEqual(api.send_reminder_email(self.reminder), 0)

    def test_check_for_reminders_calendar(self):
        self.assertEqual(api.check_for_calendar_reminders.now(), 1)

    def test_check_for_reminders_mileage(self):
        self.assertEqual(api.check_for_mileage_reminders.now(), 1)
        

    def test_run_daily_reports(self):
        self.assertEqual(api.run_daily_reports.now(), -1)

    def test_live_harsh_braking_checks(self):
        self.assertEqual(api.live_harsh_braking_checks.now(), 1)


    def test_live_status_checks(self):
        self.assertEqual(api.live_status_checks.now(), 2)
        
