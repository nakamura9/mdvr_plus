import os
import subprocess
import copy
# from winreg import *
import logging 

class InstallApp():
    def run(self):
        self.install_service()
        
    def install_service(self):
        PATH = os.path.abspath(os.getcwd())
        SERVICE_PATH = os.path.join(PATH, 'service')

        ENVIRONMENT = copy.deepcopy(os.environ)
        ENVIRONMENT['PATH'] = ";".join([PATH, SERVICE_PATH ]) + ';' + ENVIRONMENT["PATH"]

        # try:
        #     key = CreateKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\\mdvrplus')
        #     SetValueEx(key, "SERVICE_PATH", 0, REG_SZ, SERVICE_PATH)
        #     CloseKey(key)
        # except Exception as e:
        #     logging.exception('Failed to access registry')
        #     return -1

            
        #write config

        try:
            code = subprocess.run(['service.exe', '--startup=auto', 'install'], 
                env=ENVIRONMENT, stdout=subprocess.PIPE)
        except Exception as e:
            logging.exception('failed to load service')
            return -1 
        else:
            if code != 0:
                return -1 
        
            return 0

        res = subprocess.run(['sc', 'start', 'MDVRService'])
        if res.returncode != 0:
            logging.exception('failed to start service')
            
   

InstallApp().run()