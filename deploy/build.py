import os
import shutil
from distutils.dir_util import copy_tree
import subprocess
import copy 

#copy server source
SERVER_DIRS = [
    'common',
    'mdvr_plus',
    os.path.join('assets', 'bundles'),
    'reports'
]

ENV = copy.deepcopy(os.environ)
PYTHON_PATH = os.path.join('dist', 'client','python')
ENV["PATH"] = PYTHON_PATH + ';' + ENV['PATH']

SERVER_FILES = [
    'manage.py',
    'createsuperuser.py',
    os.path.join('deploy', 'db.sqlite3')
]

NEW_DIRS = [
    'media',
    'daily_reports'
]
DEST_DIR = os.path.abspath(os.path.join('dist', 'client', 'server'))
os.chdir('..')

REQUIREMENTS = os.path.abspath('requirements.txt')
result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])


# build client executable
os.chdir('deploy')
code = subprocess.run(['pyinstaller', 'deploy.spec', '--clean'])

if code.returncode != 0:
    raise Exception('Failed to build client')

os.chdir('..')
print('copying code')
if os.path.exists(DEST_DIR):
    #clear the exisitng data
    shutil.rmtree(DEST_DIR)

#create new server instance 
os.makedirs(DEST_DIR)

for dir in SERVER_DIRS:
    copy_tree(dir, os.path.join(DEST_DIR, dir))

for fil in SERVER_FILES:
    shutil.copy(fil, DEST_DIR)

    
shutil.copy(os.path.join('assets', 'webpack-stats.json'), 
    os.path.join(DEST_DIR, 'assets'))

for dir in NEW_DIRS:
    os.makedirs(os.path.join(DEST_DIR, dir))

os.chdir('deploy')
print('copying python')
copy_tree('python', os.path.join('dist', 'client','python'))


os.chdir(PYTHON_PATH)
subprocess.run(['./python', '-m', 'pip', 'install', '-r', REQUIREMENTS], 
    env=ENV)

os.chdir(DEST_DIR)

#migrate database
subprocess.run(['python', 'manage.py', 'migrate'], 
    env=ENV)

#install fixtures
subprocess.run(['python', 'manage.py', 'loaddata', 'common.json', 
    'reminders.json'], env=ENV)    

#create superuser
subprocess.run(['python', 'createsuperuser.py'], env=ENV)
os.chdir('../..')
shutil.make_archive(os.path.abspath('client'), 'zip', os.getcwd())