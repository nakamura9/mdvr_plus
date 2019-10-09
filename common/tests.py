from django.test import TestCase
from common.models import Config
from django.test import Client
from django.shortcuts import reverse
import datetime

class ModelTests(TestCase):
    #fixtures = ['common.json']
    def create_config(self):
        return Config.objects.create(
            email_address='mail@test.com',
            email_password='pwd',
            smtp_server='smtp.gmail.com',
            smtp_port=465,
            default_reminder_email='test@mail.com',
            DDC_reminder_days=30,
            company_name='test',
            

        )

    def test_create_config(self):
        obj = self.create_config()
        self.assertIsInstance(obj, Config)

    def test_delete_config(self):
        if Config.objects.all().count() == 0:
            self.create_config()

        obj = Config.objects.first()
        obj.delete()
        self.assertEqual(Config.objects.all().count(), 1)

    def test_config_host_property(self):
        if Config.objects.all().count() == 0:
            self.create_config()

        obj = Config.objects.first()
        ip = '192.100.100.1'
        obj.server_ip = ip
        obj.save()
        obj = Config.objects.first()

        self.assertEqual(obj.host, ip)

        domain = 'domain.com'
        obj.server_domain = domain
        obj.server_ip = ''
        obj.save()

        obj = Config.objects.first()
        self.assertEqual(obj.host, domain)


    
class ServicesTests(TestCase):
    def test_create_toast(self):
        pass

    def test_send_reminder_email(self):
        pass

    def test_check_for_reminders_time(self):
        pass

    def test_check_for_reminders_mileage(self):
        pass

    def test_run_daily_reports(self):
        pass

    def test_live_harsh_braking_checks(self):
        pass

    

class ViewTests(TestCase):
    fixtures = ['common.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def test_home_page(self):
        resp = self.client.get(reverse('app:home'))
        self.assertEqual(resp.status_code, 200)

    def test_empty_page(self):
        resp = self.client.get(reverse('app:empty-page'))
        self.assertEqual(resp.status_code, 200)

    def test_get_config_page(self):
        resp = self.client.get(reverse('app:config', kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_config_page(self):
        resp = self.client.post(reverse('app:config', 
                                        kwargs={'pk':1}), data={
                                            'email_address':'mail@test.com',
                                            'email_password':'pwd',
                                            'smtp_server':'smtp.gmail.com',
                                            'smtp_port':465,
                                            'default_reminder_email':'test@mail.com',
                                            'DDC_reminder_days':30,
                                            'company_name':'test',
                                            'server_port': 465,
                                            'conn_account': 'admin',
                                            'speeding_threshold': 80,
                                            'harsh_braking_delta': 40.0,'daily_report_generation_time': datetime.time(23, 30)
                                        })
        self.assertEqual(resp.status_code, 302)