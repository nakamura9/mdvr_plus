from django.views.generic import TemplateView
from wkhtmltopdf.views import PDFTemplateView
import os 
import datetime
from reports.models import Vehicle
import requests
import json
from common.models import Config
from django.http import HttpResponse

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
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardAPIAction_login.action', params={
            'account':config.account,
            'password':config.password
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
        resp = requests.get(f'http://{config.host}:{config.server_port}/StandardAPIAction_queryTrackDetail.action', params={
            'jsession':session,
            'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
            'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
            'currentPage': 1,
            'pageRecords':100,
        })
        #process for harsh braking and discard each chunk
        self.determine_harsh_braking(resp)
        #iterate over all the pages
        current_page = 1
        while resp['pagination']['hasNextPage']:
            current_page += 1
            resp = requests.get(f'http://{config.host}:'
                f'{config.port}/StandardAPIAction_queryTrackDetail.action', 
                params={
                    'jsession':session,
                    'begintime':start.strftime('%Y-%m-%d %H:%M:%S'),
                    'endtime':end.strftime('%Y-%m-%d %H:%M:%S'),
                    'currentPage': current_page,
                    'pageRecords':100,
                })

            self.determine_harsh_braking(resp)
            
            

    def determine_harsh_braking(self, resp):
        # compare the speeds of each successive record
        # if the delta > 40km/hr per 3 seconds, save that as harsh braking
        # create event dict with fields for, datetime, location, delta, and 
        # initial speed
        data = json.loads(resp.content)
        for i in range(len(data['tracks'])):
            track = data['tracks'][i]
            if i == len(data['tracks']):
                return
            next = data['tracks'][i + 1]

            if track['sp'] - next['sp'] > 400:
                self.harsh_braking_records.append({
                    'timestamp': next['gt'],
                    'location': f'{next["lng"]}, {next["lng"]}',
                    'delta': "{0:.2f}".format((track['sp']- next['sp']) / 10.0),
                    'init_speed': "{0:.2f}".format(track['sp'] / 10.0)
                })
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicle = Vehicle.objects.get(pk=self.request.GET['vehicle'])
        self.get_vehicle_records()

        context.update({
            'date': dateime.date.today(),
            'events': self.harsh_braking_records,
            'from': self.request.GET['start'],
            'to': self.request.GET['end'],
            'vehicle': vehicle,
        })
        return context 


class SpeedingReport(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context 


class HarshBrakingPDFReport(PDFTemplateView):
    pass

class SpeedingPDFReport(PDFTemplateView):
    pass