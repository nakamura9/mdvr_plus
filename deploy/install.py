import os
import subprocess
import copy

from installer import app
import webview
import threading


class InstallApp():
    def run(self):
        self.start_server()
        self.open_window()
        
    def start_server(self):
        def run_server():
            app.run(host='127.0.0.1', port='5000', threaded=True)#debug=False
        t = threading.Thread(target=run_server)
        t.daemon =True
        t.start()

    def open_window(self):
        webview.create_window('MDVR+ Installer', 'http://localhost:5000/')
        webview.start(debug=True, gui='mshtml')

InstallApp().run()