from django.db import models

class Config(models.Model):
    email_address = models.CharField(max_length=128)
    email_password = models.CharField(max_length=64)
    smtp_server = models.CharField(max_length=128)
    smtp_port = models.IntegerField()
    default_reminder_email = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj