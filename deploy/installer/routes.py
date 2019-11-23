from flask import render_template, jsonify, request, url_for, redirect
import os
from installer import app
import subprocess
import json
import hmac
import hashlib
from winreg import *
import winreg
import copy
import logging
import shutil


logger = logging.getLogger()
logger.setLevel(logging.ERROR)
handler = logging.FileHandler('dump.log')
handler.setLevel(logging.ERROR)

logger.addHandler(handler)

class StateManager(object):
    _installation_messages = []
    _installation_status = {
        'license_verified': False,
        'error': ''
    }

    @property
    def installation_status(self):
        return self._installation_status

    def set_installation_status(self,  key, val):
        self._installation_status[key] = val

    @property
    def messages(self):
        return self._installation_messages
    
    def set_messages(self, msg):
        self._installation_messages.append(msg)

state = StateManager()


def install_mdvr():
    PATH = os.path.abspath(os.getcwd())
    SERVICE_PATH = os.path.join(PATH, 'service')

    ENVIRONMENT = copy.deepcopy(os.environ)
    ENVIRONMENT['PATH'] = ";".join([PATH, SERVICE_PATH ]) + ';' + ENVIRONMENT["PATH"]

    #set up a registry value for the application to access when running the service
    try:
        key = CreateKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\\mdvrplus')
        SetValueEx(key, "SERVICE_PATH", 0, REG_SZ, SERVICE_PATH)
        CloseKey(key)
    except Exception as e:
        state.set_installation_status('error', e)
        logging.exception('Failed to access registry')
        return -1

        
    #write config

    try:
        code = subprocess.run(['service.exe', '--startup=auto', 'install'], 
            env=ENVIRONMENT, stdout=subprocess.PIPE)
    except Exception as e:
        state.set_installation_status('error', e)
        logging.exception('failed to load service')
        return -1 
    else:
        if code != 0:
            state.set_installation_status('error', 'Failed to start application service')
            return -1 
        
        shutil.move('license.json', 'service/server')
        return 0

def generate_hardware_id():
    result = subprocess.run('wmic csproduct get uuid', 
            stdout=subprocess.PIPE, shell=True)
    _id = result.stdout.decode('utf-8')
    _id = _id[_id.find('\n') + 1:]
    id = _id[:_id.find(' ')]

    return id

def generate_key_file():
    id = generate_hardware_id()
    with open('mdvr_key.txt', 'w') as f:
        f.write(id)

    state.set_messages('License key generated')

    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/keygen')
def keygen():
    if not os.path.exists('mdvr_key.txt'):
        logger.error(os.getcwd())
        state.set_messages('No license key found')
        generate_key_file()

    return render_template('keygen.html')


@app.route('/install')
def what_next():
    if not os.path.exists('license.json'):
        state.set_messages('No license found. Please ensure a copy of license.json is located in the current folder. Contact your vendor for assistance')
    else:
        with open('license.json', 'r') as f:
            lic = json.load(f)
            hid = generate_hardware_id()

            lic_str = json.dumps(lic['license'])
            data_string = hid + lic_str

            byte_data = bytes(data_string, 'ascii')
            hash = hashlib.sha3_512(byte_data).hexdigest()
            if not hmac.compare_digest(hash, lic['signature']):
                state.set_messages('License check failed for this hardware. Please contact your vendor for assistance')
            else:
                state.set_messages('License verified')
                result = install_mdvr()
                if result == -1:
                    return render_template('error.html', reason=state.installation_status['error'])

                state.set_installation_status('license_verified', True)

    return render_template('install.html')
    

@app.route('/finished')
def finished():
    return render_template('finished.html')


@app.route('/status')
def get_status():
    return jsonify({
        'notes': state.messages,
        'status': state.installation_status
    })
