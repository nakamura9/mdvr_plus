import os
import subprocess
import copy
from tkinter import messagebox

from winreg import *
import winreg

# must be located next to the service executable
PATH = os.path.abspath(os.getcwd())
SERVICE_PATH = os.path.join(PATH, 'service')

ENVIRONMENT = copy.deepcopy(os.environ)
ENVIRONMENT['PATH'] = ";".join([PATH, SERVICE_PATH ]) + ';' + ENVIRONMENT["PATH"]

#set up a registry value for the application to access when running the service
try:
    key = CreateKey(HKEY_LOCAL_MACHINE, r'SOFTWARE\\mdvrplus')
    SetValueEx(key, "SERVICE_PATH", 0, REG_SZ, SERVICE_PATH)
    CloseKey(key)
except:
    raise Exception('Failed to install registry')

#write config

code = subprocess.run(['service.exe', '--startup=auto', 'install'], 
    env=ENVIRONMENT)


messagebox.showinfo('MDVR+', 'Installed Successfully!')