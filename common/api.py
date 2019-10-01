import smtplib
import ssl 
from common.models import Config
from reports.models import Reminder
import datetime
from django.db.models import Q
from background_task import background
from background_task.models import Task
from plyer import notification
from reports.daily_reports import (generate_daily_harsh_braking_summary, 
                                  generate_daily_speeding_report)
from django.db.utils import OperationalError
import logging
logging.basicConfig(filename='background.log', level=logging.WARN)

def create_toast_notification(reminder):
    notification.notify(
        title=reminder.reminder_type.name,
        message=reminder.reminder_message,
        app_name='MDVR+'
    )

def send_reminder_email(reminder):
    config = Config.objects.first()
    context = ssl.create_default_context()
    logging.debug(f'sending reminder email for reminder ' +\
                  f'#{reminder.reminder_email}')
    with smtplib.SMTP_SSL(
            config.smtp_server, 
            config.smtp_port, 
            context=context) as server:
        server.login(
                config.email_address, 
                config.email_password)
        logging.info('logged in successfully')
        try:
            resp = server.sendmail(config.email_address,
                                   reminder.reminder_email, 
                                   """
                                   This is an automated message,
                                   Please take note of the following reminder regarding, {}.
                                   {}

                                   MDVR+
                                   """.format(reminder.reminder_type, 
                                              reminder.reminder_message))
            logging.info('Email sent successfully')
        except smtplib.SMTPException:
            logging.error(f'Email to {reminder.reminder_email} not sent')
        else:
            if len(resp) == 0:
                pass
            else:
                logging.error(f'Email to {", ".join(resp.keys())} not sent')

        finally:
            server.quit()


@background
def check_for_reminders():
    logging.info('checking reminders')
    today = datetime.date.today()
    reminders = Reminder.objects.filter(Q(active=True) & Q(
        Q(last_reminder__lt=today) | Q(last_reminder__isnull=True)
    ))
    for reminder in reminders:
        if reminder.date == today or reminder.repeat_on_date(today):
            try:
                send_reminder_email(reminder)
            except Exception as e:
                logging.error(e, exc_info=True)
                logging.critical('failed to send email')
            create_toast_notification(reminder)
            reminder.last_reminder = today
            reminder.save()
            
@background
def run_daily_reports():
    logging.info('running daily reports')
    try:
        generate_daily_harsh_braking_summary()
        generate_daily_speeding_report()
    except Exception as e:
        logging.critical('failed to generate daily summary reports')
        logging.error(e, exc_info=True)


try:
    if not Task.objects.filter(task_name__contains='check_for_reminders'):
        check_for_reminders(repeat=Task.DAILY)

    if not Task.objects.filter(
            task_name__contains='run_daily_reports').exists():
        today = datetime.date.today()
        run_daily_reports(schedule=datetime.datetime(
            today.year, 
            today.month, 
            today.day,
            23, 30, 0), repeat=Task.DAILY)

except OperationalError:
    pass