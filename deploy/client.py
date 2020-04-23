import logging
logger = logging.getLogger()
logger.disabled = True

import win32gui, win32con, win32console
import threading

def hide_console():
    console = win32console.GetConsoleWindow()
    win32gui.ShowWindow(console , win32con.SW_HIDE)

t = threading.Timer(1, hide_console)
t.daemon =True
t.start()


import webview
webview.create_window('MDVR+', 'http://localhost:8888/login')
webview.start(gui='cef')#setting the gui is important
