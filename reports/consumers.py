import json
from channels.generic.websocket import WebsocketConsumer
from .state import report_state

class ReportStatus(WebsocketConsumer):
    def connect(self):
        print('connecting dammit')
        self.accept()

    def disconnect(self, close_code):
        print('disconnecting dammit')
        print(close_code)

    def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # usr = text_data_json['message']
        print('receiving')
        print(text_data)
        text_data = int(text_data)
        print(report_state.state)
        print('state')
        
        if not report_state.state.get(text_data, None):
            self.send(text_data=json.dumps({
            'pages': 0,
            'current': 0
        }))
            print('sent something')
            return
        data = {
            'pages': report_state.state[text_data]['pages'],
            'current': report_state.state[text_data]['current'],
        }
        print(data)
        self.send(text_data=json.dumps({
            'pages': report_state.state[text_data]['pages'],
            'current': report_state.state[text_data]['current'],
        }))