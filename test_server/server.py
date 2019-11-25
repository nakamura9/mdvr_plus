from bottle import request, route, run, Bottle, ServerAdapter
import json
import os
import sys

SESSION_ID = '3u1239uuijjr8ew7324'
VEHICLE_ID = '77779'
PAGINATION_COUNTER = 0
#urls 
# device status
# track detail
# userVehicle


@route('/StandardApiAction_login.action')
def login():
    if request.query.get('password', None)== 'admin' and \
            request.query.get('account', None) == 'admin':
        return {
            'result': 0,
            'jsession': SESSION_ID
        }
    return {
        'result': 1
    }


@route('/StandardApiAction_queryTrackDetail.action')
def get_tracks():
    global PAGINATION_COUNTER
    PAGINATION_COUNTER += 1
    if request.query.get('jsession', None) != SESSION_ID:
        return {
            'result': 5
        }

    if request.query.get('devIdno', None) != VEHICLE_ID:
        return {
            'result': 19
        }
    #API simplified by not specifying the dates and times 
    
    #TODO handle pagination 
    data = None
    with open('data/trackDetail.json', 'r') as f:
        data = json.load(f)
    if PAGINATION_COUNTER == 5:
        data['pagination']['hasNextPage'] = False
        PAGINATION_COUNTER = 0
    return data

@route('/StandardApiAction_getDeviceStatus.action')
def get_status():
    if request.query.get('jsession', None) != SESSION_ID:
        return {
            'result': 5
        }

    if request.query.get('devIdno', None) != VEHICLE_ID:
        return {
            'result': 19
        }

    data = None
    with open('data/deviceStatus.json', 'r') as f:
        data = json.load(f)

    return data

@route('/StandardApiAction_queryUserVehicle.action')
def get_vehicles():
    if request.query.get('jsession', None) != SESSION_ID:
        return {
            'result': 5
        }

    data = None
    with open('data/userVehicle.json', 'r') as f:
        data = json.load(f)

    return data


@route('/StandardApiAction_getDeviceOlStatus.action')
def get_devices():
    if request.query.get('jsession', None) != SESSION_ID:
        return {
            'result': 5
        }

    data = None
    with open('data/devices.json', 'r') as f:
        data = json.load(f)

    return data


#for controlling the server programatically
class MyWSGIRefServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()

app = Bottle()
server = MyWSGIRefServer(host='localhost', port=5000)

def stop_test_server():
    server.stop()


if __name__ == "__main__":
    print('### running server')
    run(debug=True, port=5000, reloader=True)