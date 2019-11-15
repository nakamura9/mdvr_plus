import json
import sys
import threading
import os
import subprocess
import copy 

from cefpython3 import cefpython as cef

#add wkhtmltopdf path to path


ENVIRONMENT = copy.deepcopy(os.environ)
ENVIRONMENT['PATH'] = ";".join([
    os.path.abspath('python'),
    os.path.abspath(os.path.join('server', 'wkhtmltopdf', 'bin')),
    os.path.abspath('server'),
    ]) + ';' + ENVIRONMENT["PATH"]


def start_server():
    os.chdir('server')
    subprocess.Popen(['python', 'manage.py', 'runserver', '0.0.0.0:8888'], 
        env=ENVIRONMENT)
    subprocess.Popen(['python', 'manage.py', 'process_tasks'], 
        env=ENVIRONMENT)


def main():
    sys.excepthook = cef.ExceptHook
    start_server()
    
    import time
    time.sleep(5)#give server time to initialize

    cef.Initialize()
    cef.CreateBrowserSync(url="localhost:8888/login",
                        window_title="MDVR+")

    cef.MessageLoop()
    cef.Shutdown()


if __name__ == "__main__":
    main()