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

SERVER_FILES = [
    'manage.py',
    os.path.join('assets', 'webpack-stats.json'),
    os.path.join('deploy', 'db.sqlite3')
]
NEW_DIRS = [
    'media',
]
DEST_DIR = os.path.join('deploy', 'server')
os.chdir('..')

REQUIREMENTS = os.path.join(os.getcwd(), 'requirements.txt')

if os.path.exists(DEST_DIR):
    #clear the exisitng data
    shutil.rmtree(DEST_DIR)

    #create new server instance 
    os.makedirs(DEST_DIR)


for dir in SERVER_DIRS:
    copy_tree(dir, os.path.join(DEST_DIR, dir))

for fil in SERVER_FILES:
    shutil.copy(fil, DEST_DIR)

for dir in NEW_DIRS:
    os.makedirs(os.path.join(DEST_DIR, dir))


# build client executable
os.chdir('deploy')
code = subprocess.run(['pyinstaller', 'deploy.spec', '--clean'])

if code.returncode == 0:
    copy_tree('server', os.path.join('dist', 'client', 'server'))
    copy_tree('python', os.path.join('dist', 'client','python'))

    ENV = copy.deepcopy(os.environ)
    PYTHON_PATH = os.path.join('dist', 'client','python')
    ENV["PATH"] = PYTHON_PATH + ';' + ENV['PATH']
    os.chdir(PYTHON_PATH)
    subprocess.run(['./python', '-m', 'pip', 'install', '-r', REQUIREMENTS], 
        env=ENV)