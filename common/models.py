from django.db import models

class Config(models.Model):
    email_address = models.CharField(max_length=128)
    email_password = models.CharField(max_length=64)
    smtp_server = models.CharField(max_length=128)
    smtp_port = models.IntegerField()
    default_reminder_email = models.CharField(max_length=255)
    DDC_reminder_days = models.IntegerField()
    server_ip = models.CharField(max_length=16, default='', blank=True)
    server_domain = models.CharField(max_length=16, default='', blank=True)
    server_port = models.IntegerField(default=8080)
    conn_account = models.CharField(max_length=255, default='admin')
    conn_password = models.CharField(max_length=32, default='', blank=True)
    company_name = models.CharField(max_length=255)
    speeding_threshold = models.FloatField(default=80.0)
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def host(self):
        if self.server_ip != '':
            return self.server_ip
        return self.server_domain