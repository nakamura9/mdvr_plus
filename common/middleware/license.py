import json 
from django.http import HttpResponseRedirect
import logging 
logger = logging.getLogger(__file__)
import hmac 
import hashlib
import os
import subprocess

#runs every 50 requests
RESPONSE_COUNT = 0

def generate_hardware_id():
    result = subprocess.run('wmic csproduct get uuid', 
            stdout=subprocess.PIPE, shell=True)
    _id = result.stdout.decode('utf-8')
    _id = _id[_id.find('\n') + 1:]
    id = _id[:_id.find(' ')]

    return id

class LicenseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global RESPONSE_COUNT
        """
        Checks that each request is within the limits of the purchased license.
            1. Checks that the users are not using the same account on multiple 
                machines.
            2. Verifies that the license file has not been tampered with.
        """

        #condition is evaluated to ensure an infinite loop is avoided
        if RESPONSE_COUNT % 20 != 0 or \
                request.path.startswith('/app/error-page') or \
                'api' in request.path:
            RESPONSE_COUNT += 1
            return self.get_response(request)

        license = None
        try:
            #installer requires license in top level directory
            with open(os.path.join( os.getcwd(), 'license.json'), 'r') as f:
                license = json.load(f)
        
        except FileNotFoundError:
            logger.critical('The license file is not found')
            return HttpResponseRedirect('/app/error-page')

        license_str = json.dumps(license['license'])
        hid = generate_hardware_id()
        data_string = hid + license_str

        byte_data = bytes(data_string, 'ascii')
        hash = hashlib.sha3_512(byte_data).hexdigest()
        

        if not hmac.compare_digest(hash, license['signature']):
            logger.critical('the license hash check has failed')
            return HttpResponseRedirect('/app/error-page')

        else:
            RESPONSE_COUNT += 1
            return self.get_response(request)