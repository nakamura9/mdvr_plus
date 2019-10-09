from wkhtmltopdf import utils as pdf_tools
import datetime
import os 
from common.models import Config
import requests
import json
import logging
from reports.report_views import login
from django.http import HttpResponse
import smtplib
import ssl
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ntpath
#set up logging
logging.basicConfig(filename='reports.log', level=logging.DEBUG)


def get_vehicle_list(session, config):
    resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_queryUserVehicle.action', params={
            'jsession':session
        })
    data = json.loads(resp.content)
    if data['result'] != 0:
        logging.critical(f'An error, {data["result"]}, prevented a ' + \
        f'the system from returning the vehicle list')
        return
    
    return [{
        'id': v['id'], 
        'did': v['dl'][0]['id'],
        'plate': v['nm']
        } for v in data['vehicles']]

def process_speeding_events(data, events, vehicle, config):
    if not data['tracks']:
        return 
    duration = 0
    threshold = config.speeding_threshold

    for i in range(len(data['tracks'])):
        track = data['tracks'][i]
        if track['sp'] > threshold:
            duration += 3
            events.append({
                'vehicle_id': vehicle['id'],
                'plate_no': vehicle['plate'],
                'timestamp': track['gt'],
                'location': f'{track["lng"]}, {track["lng"]}',
                'speed': "{0:.2f}".format(track['sp'] / 10.0),
                'duration': duration
            })
        else:
            duration = 0

def generate_daily_speeding_report():
    template = os.path.join('reports', 'report', 'speeding_summary.html')
    today = datetime.date.today()
    context = {
        'date': today,
    }
    events = []
    start  =datetime.datetime(2019, 9, 15, 0, 0,0)
    end  =datetime.datetime(2019, 9, 21, 23, 59,59)
    
    #start  =datetime.datetime(today.year, today.month, today.day, 0, 0,0)
    #end  =datetime.datetime(today.year, today.month, today.day, 23, 59,59)

    #login
    #get parameters from config
    config = Config.objects.first()
    
    session = login()
    if isinstance(session, HttpResponse):
        logging.critical(session.content)
        return
    
    #get vehicle list    
    vehicle_ids = get_vehicle_list(session, config)
    if not vehicle_ids:
        return
        
    #get speeding records for each vehicle.
    for vehicle in vehicle_ids:
        url = f'http://{config.host}:{config.server_port}/' + \
              f'StandardApiAction_queryTrackDetail.action'
        params = {
            'jsession':session,
            'devIdno': vehicle['did'],
            'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
            'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
            'currentPage': 1,
            'pageRecords':100,
        }
        resp = requests.get(url, params=params)
        #process for harsh braking and discard each chunk
        data = json.loads(resp.content)
        process_speeding_events(data, events, vehicle, config)
        current_page = 1
        if not data['pagination']:
            continue

        while data['pagination']['hasNextPage']:
            current_page += 1
            params['currentPage'] = current_page
            resp = requests.get(url, params=params)
            if resp.status_code != 200:
                break
            data = json.loads(resp.content)
            process_speeding_events(data, events, vehicle, config)
    
    #store the records in a list and return the list.
    context.update({
        'events': events,
        'vehicles': len(vehicle_ids),
        'config': config
    })
    print(context)
    outfile = os.path.abspath(
        os.path.join('daily_reports', f'speeding-summary {today}.pdf'))
    print(outfile)

    pdf_tools.render_pdf_from_template(
                template, None, None, context,
                cmd_options={
                    'output': outfile
                })
                
    email_speeding_report(outfile, config)
    return True


def email_speeding_report(path, config):
    #preparing email
    mime_msg = MIMEMultipart('alternative')
    mime_msg['Subject'] = 'Daily Speeding Summary(MDVR+)'
    mime_msg['From'] = config.email_address
    mime_msg['To'] = config.default_reminder_email
    mime_msg.attach(MIMEText('''
    Please find attached the daily speeding summary report.
    Regards,
    MDVR+
    ''', 'plain'))

    attachment = MIMEBase('application', 'octet-stream')
    with open(path, 'rb') as att:
        attachment.set_payload(att.read())
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-disposition',
            'attachment; filename={}'.format(
                ntpath.basename(path)
            )
        )
    mime_msg.attach(attachment)

    #sending email
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
                                   mime_msg['To'], 
                                   mime_msg.as_string())
        except smtplib.SMTPException:
            logging.error(f'Email not sent')
        else:
            if len(resp) == 0:
                pass
            else:
                logging.error(f'Email not sent')

        finally:
            server.quit()


def process_harsh_braking_events(data, events, vehicle, config):
    if not data['tracks']:
        return 
    for i in range(len(data['tracks'])):
        track = data['tracks'][i]
        if i == len(data['tracks']) -1:
            return
        next = data['tracks'][i + 1]

        if (track['sp'] - next['sp']) / 10.0 > config.harsh_braking_delta:
            events.append({
                'vehicle_id': vehicle['id'],
                'plate_no': vehicle['plate'],
                'timestamp': next['gt'],
                'location': f'{next["lng"]}, {next["lng"]}',
                'delta': "{0:.2f}".format((track['sp']- next['sp']) / 10.0),
                'init_speed': "{0:.2f}".format(track['sp'] / 10.0)
            })


def generate_daily_harsh_braking_summary():
    template = os.path.join('reports', 'report', 'harsh_braking_summary.html')
    today = datetime.date.today()
    context = {
        'date': today,
    }
    events = []
    start  =datetime.datetime(today.year, today.month, today.day, 0, 0,0)
    end  =datetime.datetime(today.year, today.month, today.day, 23, 59,59)

    #login
    #get parameters from config
    config = Config.objects.first()
    # connect to the API
     
    session = login()
    if isinstance(session, HttpResponse):
        logging.critical(session.content)
        return
    
    #get vehicle list    
    vehicle_ids = get_vehicle_list(session, config)
    if not vehicle_ids:
        return
        
    #get speeding records for each vehicle.
    for vehicle in vehicle_ids:
        url = f'http://{config.host}:{config.server_port}/' + \
              f'StandardApiAction_queryTrackDetail.action'
        params = {
            'jsession':session,
            'devIdno': vehicle['did'],
            'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
            'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
            'currentPage': 1,
            'pageRecords':100,
        }
        resp = requests.get(url, params=params)
        #process for harsh braking and discard each chunk
        data = json.loads(resp.content)
        process_harsh_braking_events(data, events, vehicle, config)
        current_page = 1
        if not data['pagination']:
            continue

        while data['pagination']['hasNextPage']:
            current_page += 1
            params['currentPage'] = current_page
            resp = requests.get(url, params=params)
            if resp.status_code != 200:
                break
            data = json.loads(resp.content)
            process_harsh_braking_events(data, events, vehicle, config)
    
    #store the records in a list and return the list.
    context.update({
        'events': events,
        'vehicles': len(vehicle_ids),
        'config': config
    })
    pdf_tools.render_pdf_from_template(
                template, None, None, context,
                cmd_options={
                    'output': os.path.join('daily_reports', 
                                f'harsh-braking-summary {today}.pdf')
                })
    pass
