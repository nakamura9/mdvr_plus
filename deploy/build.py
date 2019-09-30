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
    os.path.join('deploy', 'db.sqlite3')
]
NEW_DIRS = [
    'media',
    'daily_reports'
]
DEST_DIR = os.path.join('deploy', 'server')
os.chdir('..')

os.chdir(DEST_DIR)

#migrate database
subprocess.run(['../python/python', 'manage.py', 'migrate'], env=ENV)

#install fixtures
subprocess.run(['../python/python', 'manage.py', 'loaddata', 'common.json', 'reminders.json'], env=ENV)

if False:

    REQUIREMENTS = os.path.join(os.getcwd(), 'requirements.txt')

    if os.path.exists(DEST_DIR):
        #clear the exisitng data
        shutil.rmtree(DEST_DIR)

        #create new server instance 
        os.makedirs(DEST_DIR)


    result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])


    for dir in SERVER_DIRS:
        copy_tree(dir, os.path.join(DEST_DIR, dir))

    for fil in SERVER_FILES:
        shutil.copy(fil, DEST_DIR)

        
    shutil.copy(os.path.join('assets', 'webpack-stats.json'), 
        os.path.join(DEST_DIR, 'assets'))

    for dir in NEW_DIRS:
        os.makedirs(os.path.join(DEST_DIR, dir))


    # build client executable
    os.chdir('deploy')
    code = subprocess.run(['pyinstaller', 'deploy.spec', '--clean'])

    if code.returncode == 0:
        print('copying code')
        copy_tree('server', os.path.join('dist', 'client', 'server'))
        print('copying python')
        
        copy_tree('python', os.path.join('dist', 'client','python'))

        
        os.chdir(PYTHON_PATH)
        subprocess.run(['./python', '-m', 'pip', 'install', '-r', REQUIREMENTS], 
            env=ENV)

        os.chdir(DEST_DIR)

        #migrate database
        subprocess.run(['../python/python', '-m', 'manage.py', 'migrate'], 
            env=ENV)

        #install fixtures
        subprocess.run(['../python/python', '-m', 'manage.py', 'loaddata', 'common.json', 'reminders.json'], 
            env=ENV)    