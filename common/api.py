import smtplib
import ssl 
from common.models import Config
from reports.models import Reminder, Alarm, Vehicle
import datetime
from django.db.models import Q
from background_task import background
from background_task.models import Task
from plyer import notification
from reports.daily_reports import (generate_daily_harsh_braking_summary, 
                                  generate_daily_speeding_report)
from django.db.utils import OperationalError
import logging
from django.http import HttpResponse
import requests
from reports.daily_reports import get_vehicle_list, process_harsh_braking_events
import json

logging.basicConfig(filename='background.log', level=logging.ERROR)
logging.info('started task runner')

from reports.report_views import login

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
    print(reminders)
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

    mileage_reminders = Reminder.objects.filter(reminder_method=1, active=True)
    for reminder in mileage_reminders:
        curr_mileage = reminder.vehicle.get_status()['lc'] / 1000
        if curr_mileage - \
                reminder.last_reminder_mileage > reminder.interval_mileage:
            try:
                send_reminder_email(reminder)
            except Exception as e:
                logging.error(e, exc_info=True)
                logging.critical('failed to send email')
            create_toast_notification(reminder)
            reminder.last_reminder_mileage = curr_mileage
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


@background
def live_harsh_braking_checks():
    # iterate over each car
    # check if harsh braking has happened in the last minute
    # create an alarm for each instance
    # have a method view that retrieves all the alarms and raises them in the software
    session = login()
    if isinstance(session, HttpResponse):
        logging.critical(session.content)

    # last 60 seconds
    now = datetime.datetime.now()
    start = now - datetime.timedelta(seconds=60)
    config = Config.objects.first()
    events = []

    ids = get_vehicle_list(session, config)
    if not ids:
        return 
    
    for vehicle in ids:
        url = f'http://{config.host}:{config.server_port}/' + \
              f'StandardApiAction_queryTrackDetail.action'
        params = {
            'jsession':session,
            'devIdno': vehicle['did'],
            'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
            'endtime':now.strftime('%Y-%m-%d %H:%M:%S'),
            'currentPage': 1,
            'toMap': 1,
            'pageRecords':100,
        }
        resp = requests.get(url, params=params)
        #process for harsh braking and discard each chunk
        data = json.loads(resp.content)
        process_harsh_braking_events(data, events, vehicle, config)

        #no pagination because there are only 20 records per minute
    
    #create alarms 
    for event in events:
        Alarm.objects.create(
            vehicle = Vehicle.objects.get(vehicle_id=event['vehicle_id']),
            description="""
            Vehicle {} experienced harsh braking at {} while located at {}!
            """.format(event['vehicle_id'], event['timestamp'], 
                        event['location'])
        )

try:
    if not Task.objects.filter(task_name__contains='check_for_reminders'):
        check_for_reminders(repeat=Task.DAILY)

    config = Config.objects.first()
    if not Task.objects.filter(
            task_name__contains='run_daily_reports').exists() and config:
        today = datetime.date.today()
        time = config.daily_report_generation_time
        run_daily_reports(schedule=datetime.datetime(
            today.year, 
            today.month, 
            today.day,
            time.hour, time.minute), repeat=Task.DAILY)

    if not Task.objects.filter(
            task_name__contains='live_harsh_braking_checks').exists():
        live_harsh_braking_checks(repeat=60)#every minute
except OperationalError:
    pass

if __name__  == "__main__":
    #live_harsh_braking_checks.now()
    check_for_reminders.now()
