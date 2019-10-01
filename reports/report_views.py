from django.views.generic import TemplateView
from wkhtmltopdf.views import PDFTemplateView
import os 
import datetime
from reports.models import Vehicle
from django.shortcuts import reverse
import requests
import json
from common.models import Config
from django.http import HttpResponse
import datetime
import csv
from django.template.loader import render_to_string
from bs4 import BeautifulSoup
from django.test import Client

class HarshBrakingReport(TemplateView):
    template_name = os.path.join('reports', 'report', 'harsh_braking.html')
    harsh_braking_records = []

    def get_vehicle_records(self):
        #get vehicle
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])
        #get time params
        start_time = datetime.time(0,0)
        end_time = datetime.time(23,59,59)
        start = datetime.datetime.combine(
            datetime.datetime.strptime(self.request.GET['start'], "%Y-%m-%d"), 
            start_time)
        end = datetime.datetime.combine(
            datetime.datetime.strptime(self.request.GET['end'], "%Y-%m-%d"), 
            end_time)
        if end < start:
            return HttpResponse('Cannot generate report because'
            ' end time is older than start time')
        
        if (end - start).days > 7:
            return HttpResponse('The request can only process queries not'
            ' greater than 7 days')
        
        #get parameters from config
        config = Config.objects.first()
        # connect to the API
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_login.action', params={
            'account':config.conn_account,
            'password':config.conn_password
        })
        if resp.status_code != 200:
            return HttpResponse('An error prevented the application from' 
            ' communicating with the application server')
        # store session id 
        data = json.loads(resp.content)
        if data['result'] != 0:
            return HttpResponse('The server returned with an error')
        session = data['jsession']
        # get the list of records
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardApiAction_queryTrackDetail.action', params={
            'jsession':session,
            'devIdno': vehicle.device_id,
            'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
            'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
            'currentPage': 1,
            'pageRecords':100,
        })
        #process for harsh braking and discard each chunk
        data = json.loads(resp.content)
        self.process_data(data)
        #iterate over all the pages
        current_page = 1
        if not data['pagination']:
            return

        while data['pagination']['hasNextPage']:
            current_page += 1
            resp = requests.get(f'http://{config.host}:'
                f'{config.server_port}/StandardApiAction_queryTrackDetail.action', 
                params={
                    'jsession':session,
                    'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
                    'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
                    'currentPage': current_page,
                    'pageRecords':100,
                    'devIdno': vehicle.device_id,

                })
            if resp.status_code != 200:
                break
            data = json.loads(resp.content)
            self.process_data(data)
            
            

    def process_data(self, data):
        # compare the speeds of each successive record
        # if the delta > 40km/hr per 3 seconds, save that as harsh braking
        # create event dict with fields for, datetime, location, delta, and 
        # initial speed
        if not data['tracks']:
            return 
        for i in range(len(data['tracks'])):
            track = data['tracks'][i]
            if i == len(data['tracks']) -1:
                return
            next = data['tracks'][i + 1]

            if track['sp'] - next['sp'] > 400:
                self.harsh_braking_records.append({
                    'timestamp': next['gt'],
                    'location': f'{next["lng"]}, {next["lng"]}',
                    'delta': "{0:.2f}".format((track['sp']- next['sp']) / 10.0),
                    'init_speed': "{0:.2f}".format(track['sp'] / 10.0)
                })

    def get(self, *args, **kwargs):
        resp = self.get_vehicle_records()
        if isinstance(resp, HttpResponse):
            return resp
        return super().get(*args, **kwargs)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])
        

        context.update({
            'date': datetime.date.today(),
            'events': self.harsh_braking_records,
            'from': self.request.GET['start'],
            'to': self.request.GET['end'],
            'vehicle': vehicle,
            'company': Config.objects.first().company_name,
            'link': True
        })
        return context 


class SpeedingReport(TemplateView):
    speeding_records = []
    template_name = os.path.join('reports', 'report','speeding.html')

    def get(self, *args, **kwargs):
        resp = HarshBrakingReport.get_vehicle_records(self)
        if isinstance(resp, HttpResponse):
            return resp
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])

        context.update({
            'date': datetime.date.today(),
            'events': self.speeding_records,
            'from': self.request.GET['start'],
            'to': self.request.GET['end'],
            'vehicle': vehicle,
            'config': Config.objects.first(),
            'link': True
        })

        return context 

    def process_data(self, data):
        # note the speeds of each successive record
        # if the speed > set point note it as speeding
        # create event dict with fields for, datetime, location, delta, and 
        # initial speed
        if not data['tracks']:
            return 
        duration = 0
        threshold = Config.objects.first().speeding_threshold

        for i in range(len(data['tracks'])):
            track = data['tracks'][i]
            if track['sp'] > threshold:
                duration += 3
                self.speeding_records.append({
                    'timestamp': track['gt'],
                    'location': f'{track["lng"]}, {track["lng"]}',
                    'speed': "{0:.2f}".format(track['sp'] / 10.0),
                    'duration': duration
                })
            else:
                duration = 0

class HarshBrakingPDFReport(PDFTemplateView):
    template_name = os.path.join('reports', 'report', 'harsh_braking.html')
    harsh_braking_records = []

    def process_data(self, data):
        return HarshBrakingReport.process_data(self, data)

    def get(self, *args, **kwargs):
        resp = HarshBrakingReport.get_vehicle_records(self)
        if isinstance(resp, HttpResponse):
            return resp
        return super().get(*args, **kwargs)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])

        context.update({
            'date': datetime.date.today(),
            'events': self.harsh_braking_records,
            'from': self.request.GET['start'],
            'to': self.request.GET['end'],
            'vehicle': vehicle,
            'company': Config.objects.first().company_name,
        })
        return context 

class SpeedingPDFReport(PDFTemplateView):
    template_name = SpeedingReport.template_name
    speeding_records = []

    def process_data(self, data):
        return SpeedingReport.process_data(self, data)

    def get(self, *args, **kwargs):
        resp = HarshBrakingReport.get_vehicle_records(self)
        if isinstance(resp, HttpResponse):
            return resp
        return super().get(*args, **kwargs)
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])

        context.update({
            'date': datetime.date.today(),
            'events': self.speeding_records,
            'from': self.request.GET['start'],
            'to': self.request.GET['end'],
            'vehicle': vehicle,
            'config': Config.objects.first()
        })
        return context 

def harsh_braking_csv_report(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="harsh_braking.csv"'
    

    c = Client()
    writer = csv.writer(response)
    vehicle_id = request.GET['vehicle']
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    start = request.GET['start']
    end = request.GET['end']
    string =c.get(reverse('reports:harsh-braking-report') + \
                   f'?vehicle={vehicle_id}' + \
                  f'&start={start}&end={end}').content
    
    soup = BeautifulSoup(string)
    
    data = soup.find('table', {'id': 'report'})
    
    rows = data.find_all('tr')
    writer.writerow(['Harsh Braking Report'])
    writer.writerow(['Vehicle', vehicle.name])
    writer.writerow(['From', start])
    writer.writerow(['To', end])
    writer.writerow(['Date-Time', 'Location', 'Delta', 'Initial Speed'])
    for row in rows:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 

def speeding_report_csv(request):
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="speeding.csv"'
    

    c = Client()
    writer = csv.writer(response)
    vehicle_id = request.GET['vehicle']
    vehicle = Vehicle.objects.get(pk=vehicle_id)
    start = request.GET['start']
    end = request.GET['end']
    string =c.get(reverse('reports:speeding-report') + \
                   f'?vehicle={vehicle_id}' + \
                  f'&start={start}&end={end}').content
    
    soup = BeautifulSoup(string)
    
    data = soup.find('table', {'id': 'report'})
    
    rows = data.find_all('tr')
    writer.writerow(['Speeding Report'])
    writer.writerow(['Vehicle', vehicle.name])
    writer.writerow(['From', start])
    writer.writerow(['To', end])
    writer.writerow(['Date-Time', 'Location', 'Speed', 'Duration'])
    for row in rows:
        writer.writerow([i.string for i in row.find_all('td')])

    return response 