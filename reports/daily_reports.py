from wkhtmltopdf import utils as pdf_tools
import datetime
import os 
from common.models import Config
import requests
import json
import logging


#set up logging
logging.basicConfig(filename='reports.log', level=logging.DEBUG)


def process_speeding_events(data, events, vehicle):
    if not data['tracks']:
        return 
    duration = 0
    threshold = Config.objects.first().speeding_threshold

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
    # connect to the API
    resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_login.action', params={
        'account':config.conn_account,
        'password':config.conn_password
    })
    if resp.status_code != 200:
        logging.critical("Failed to login to the server, report generation aborting.")
        return 
    data = json.loads(resp.content)
    if data['result'] != 0:
        logging.critical(f"An error code was returned on login:{data['result']}")
        return 
    session = data['jsession']
    
    #get vehicle list    
    resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_queryUserVehicle.action', params={
            'jsession':session
        })
    data = json.loads(resp.content)
    if data['result'] != 0:
        logging.critical(f'An error, {data["result"]}, prevented a ' + \
        f'the system from returning the vehicle list')
        return
    
    vehicle_ids =[{
        'id': v['id'], 
        'did': v['dl'][0]['id'],
        'plate': v['nm']
        } for v in data['vehicles']]
        
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
        process_speeding_events(data, events, vehicle)
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
            process_speeding_events(data, events, vehicle)
    
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
                                f'speeding-summary {today}.pdf')
                })


def process_harsh_braking_events(data, events, vehicle):
    if not data['tracks']:
        return 
    for i in range(len(data['tracks'])):
        track = data['tracks'][i]
        if i == len(data['tracks']) -1:
            return
        next = data['tracks'][i + 1]

        if track['sp'] - next['sp'] > 400:
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
    resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_login.action', params={
        'account':config.conn_account,
        'password':config.conn_password
    })
    if resp.status_code != 200:
        logging.critical("Failed to login to the server, report generation aborting.")
        return 
    data = json.loads(resp.content)
    if data['result'] != 0:
        logging.critical(f"An error code was returned on login:{data['result']}")
        return 
    session = data['jsession']
    
    #get vehicle list    
    resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_queryUserVehicle.action', params={
            'jsession':session
        })
    data = json.loads(resp.content)
    if data['result'] != 0:
        logging.critical(f'An error, {data["result"]}, prevented a ' + \
        f'the system from returning the vehicle list')
        return
    
    vehicle_ids =[{
        'id': v['id'], 
        'did': v['dl'][0]['id'],
        'plate': v['nm']
        } for v in data['vehicles']]
        
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
        process_harsh_braking_events(data, events, vehicle)
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
            procees_harsh_braking_events(data, events, vehicle)
    
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
