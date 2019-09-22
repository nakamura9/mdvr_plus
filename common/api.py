import smtplib
import ssl 
from common.models import Config
from reports.models import Reminder
import datetime
from background_task import background
from background_task.models import Task
from plyer import notification

def create_toast_notification(reminder):
    notification.notify(
        title=reminder.reminder_type,
        message=reminder.reminder_message,
        app_name='MDVR+'
    )

def send_reminder_email(reminder):
    config = Config.objects.first()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(
            config.smtp_server, 
            config.smtp_port, 
            context=context) as server:
        server.login(
                config.email_address, 
                config.email_password)
        try:
            resp = server.sendmail(config.email_address,
                                   reminder_reminder_email, 
                                   """
                                   This is an automated message,
                                   Please take note of the following reminder regarding, {}.
                                   {}

                                   MDVR+
                                   """.format(reminder.reminder_type, 
                                              reminder.reminder_message))
        except smtplib.SMTPException:
            print(f'Email to {reminder.reminder_email} not sent')
        else:
            if len(resp) == 0:
                pass
            else:
                print(f'Email to {", ".join(resp.keys())} not sent')

        finally:
            server.quit()


@background
def check_for_reminders():
    today = datetime.date.today()
    reminders = Reminder.objects.filter(active=True, last_reminder__lt=today)
    for reminder in reminders:
        print(reminder)
        if reminder.date == today or reminder.repeat_on_date(today):
            send_reminder_email(reminder)
            create_toast_notification(reminder)
            reminder.last_reminder = today
            reminder.save()


#check_for_reminders(repeat=60)
print('repeating tasks')