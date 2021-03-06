import smtplib
import ssl 
from common.models import Config
from reports.models import (CalendarReminder, 
                            MileageReminder,
                            CalendarReminderAlert,
                            MileageReminderAlert,
                            Alarm,
                            Vehicle)
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

logger = logging.getLogger()

log_format = logging.Formatter("%(asctime)s [%(levelname)-5.5s ] %(message)s")

logger.setLevel(logging.ERROR)
handler = logging.FileHandler('background.log')
handler.setLevel(logging.ERROR)
handler.setFormatter(log_format)


logger.addHandler(handler)

from reports.report_views import login

def create_toast_notification(reminder):
    notification.notify(
        title=reminder.reminder_type.name,
        message=reminder.reminder_message,
        app_name='MDVR+'
    )
    return 0

def send_reminder_email(reminder):
    config = Config.objects.first()
    context = ssl.create_default_context()
    logger.debug(f'sending reminder email for reminder ' +\
                  f'#{reminder.reminder_email}')

    if 'localhost' in config.smtp_server:
        with smtplib.SMTP(config.smtp_server, 
                        config.smtp_port) as server:
            logger.info('logged in successfully')
            resp = server.sendmail(config.email_address,
                                   reminder.reminder_email, 
                                   """
                                   This is an automated message,
                                   Please take note of the following reminder regarding, {}.
                                   {}

                                   MDVR+
                                   """.format(reminder.reminder_type, 
                                              reminder.reminder_message))
            
        return 0
    with smtplib.SMTP_SSL(
            config.smtp_server, 
            config.smtp_port, 
            context=context) as server:
        server.login(
                config.email_address, 
                config.email_password)
        logger.info('logged in successfully')
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
            logger.info('Email sent successfully')
        except smtplib.SMTPException:
            logger.error(f'Email to {reminder.reminder_email} not sent')
            server.quit()
            return -1

        else:
            if len(resp) == 0:
                server.quit()
                return 0

            else:
                logger.error(f'Email to {", ".join(resp.keys())} not sent')
                server.quit()
                return -1 

@background
def check_for_calendar_reminders():
    reminder_count = 0

    logger.info('checking calendar reminders')
    today = datetime.date.today()
    reminders = CalendarReminder.objects.filter(Q(active=True) & Q(
        Q(last_reminder_date__lt=today) | Q(last_reminder_date__isnull=True)
    ))

    def alert_on_reminder(reminder):
        try:
            send_reminder_email(reminder)
        except Exception as e:
            logger.error(e, exc_info=True)
            logger.critical('failed to send email')
        create_toast_notification(reminder)
        reminder.last_reminder_date = today
        reminder.save()
        
    for reminder in reminders:
        if reminder.date == today or \
                reminder.repeat_on_date(today) or \
                reminder.alert_on_date(today):
            
            alert_on_reminder(reminder)
            reminder_count += 1

    return reminder_count



@background
def check_for_mileage_reminders():
    reminder_count = 0
    mileage_reminders = MileageReminder.objects.filter(active=True)
    for reminder in mileage_reminders:
        print(f'reminder: {datetime.datetime.now()}')
        if reminder.reminder_at_mileage() or \
                reminder.alert_at_mileage():
            print('should update')
            try:
                send_reminder_email(reminder)
            except Exception as e:
                logger.error(e, exc_info=True)
                logger.critical('failed to send email')
            create_toast_notification(reminder)
            reminder.update_last_reminder()
            reminder_count += 1

    return reminder_count

            
@background
def run_daily_reports():
    logger.info('running daily reports')
    try:
        generate_daily_harsh_braking_summary()
        try:
            generate_daily_speeding_report()
            return 0
        except Exception as e:
            logger.critical('failed to generate daily speeding report')
            logger.error(e, exc_info=True)
            raise e
    except Exception as e:
        logger.critical('failed to generate daily harsh braking report')
        logger.error(e, exc_info=True)
        return -1
    

@background 
def live_status_checks():
    '''
    Checks for:
                no video alarm, 
                disk error alarm, 
                video block alarm, 
                video loss alarm. 
                Checks for camera Failure alarm.
    '''
    #camera failure s4 bit 12
    #channel video lost s3 0-7bit
    #hard disk state s1 bit9, 10
    alarm_count = 0
    session = login()
    if isinstance(session, HttpResponse):
        logger.critical(session.content)

    ids = get_vehicle_list(session, config)
    if not ids:
        return

    for vehicle in ids:
        vehicle_obj = Vehicle.objects.get(
            vehicle_id=vehicle['id']
        )

        url = f'http://{config.host}:{config.server_port}/' + \
              f'StandardApiAction_getDeviceStatus.action'
        params = {
            'jsession':session,
            'devIdno': vehicle['did'],
            'toMap': 1
        }
        resp = requests.get(url, params=params)
        #process for harsh braking and discard each chunk
        data = json.loads(resp.content)['status'][0]
        status_1 = '{0:032b}'.format(data['s1'])
        status_2 = '{0:032b}'.format(data['s2'])
        status_3 = '{0:032b}'.format(data['s3'])
        status_4 = '{0:032b}'.format(data['s4'])

        camera_status = int(status_4[19]) # for bit 12
        hdd_status = int(status_1[21:23][::-1], 2) # bits 9 and 10 and then reverse
        #individual camera feeds. need to experiment for the order
        alarm_array = status_3[24:32][::-1]
        camera_1 = int(alarm_array[0:2], 2)
        camera_2 = int(alarm_array[2:4], 2)
        camera_3 = int(alarm_array[4:6], 2)
        camera_4 = int(alarm_array[6:8], 2)


        #check for individual camera failures
        if camera_1 > 0:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has experienced a camera video loss on camera number 1',
                vehicle=vehicle_obj
            )
            alarm_count += 1
        if camera_2 > 0:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has experienced a camera video loss on camera number 2',
                vehicle=vehicle_obj
            )
            alarm_count += 1


        if camera_3 > 0:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has experienced a camera video loss on camera number 3',
                vehicle=vehicle_obj
            )
            alarm_count += 1


        if camera_4 > 0:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has experienced a camera video loss on camera number 4',
                vehicle=vehicle_obj
            )
            alarm_count += 1

        
        #check for camera system errors
        if camera_status > 0:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has reported an error on the camera system.',
                vehicle=vehicle_obj
            )
            alarm_count += 1

        
        #check for hard drive errors
        if hdd_status == 1:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has reported that its hard drive is not operational. This could be due to a physical disconnection of the drive',
                vehicle=vehicle_obj
            )
            alarm_count += 1

        if hdd_status == 2:
            Alarm.objects.create(
                description=f'Vehicle {vehicle_obj} has reported that its hard drive has experienced a power outage.',
                vehicle=vehicle_obj
            )
            alarm_count += 1

    return alarm_count



@background
def live_harsh_braking_checks():
    # iterate over each car
    # check if harsh braking has happened in the last minute
    # create an alarm for each instance
    # have a method view that retrieves all the alarms and raises them in the software
    braking_events = 0
    session = login()
    if isinstance(session, HttpResponse):
        logger.critical(session.content)

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
        braking_events += 1

    return braking_events

try:
    if not Task.objects.filter(
            task_name__contains='check_for_calendar_reminders'):
        check_for_calendar_reminders(repeat=Task.DAILY)
    if not Task.objects.filter(
            task_name__contains='check_for_mileage_reminders'):
        check_for_mileage_reminders(repeat=Task.HOURLY)

    check_for_mileage_reminders(repeat=60)
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

    if not Task.objects.filter(
            task_name__contains='live_status_checks').exists():
        live_status_checks(repeat=300)#every 5 minutes


except OperationalError:
    pass

if __name__  == "__main__":
    #live_harsh_braking_checks.now()
    #check_for_reminders.now()
    pass