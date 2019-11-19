# import sys
# import os

# from cefpython3 import cefpython as cef


# def main():
#     sys.excepthook = cef.ExceptHook
    
#     cef.Initialize()
#     cef.CreateBrowserSync(url="localhost:8888/login",
#                         window_title="MDVR+")

#     cef.MessageLoop()
#     cef.Shutdown()


# if __name__ == "__main__":
import logging
logger = logging.getLogger()
logger.disabled = True

import webview
webview.create_window('MDVR+', 'http://localhost:8888/login')
webview.start(gui='cef')#setting the gui is important
