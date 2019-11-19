import os 

os.environ['WERKZEUG_RUN_MAIN'] = 'true'


from flask import Flask

app =  Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.disabled = True
app.logger.disabled = True

from installer import routes

