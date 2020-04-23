import os
import shutil
from distutils.dir_util import copy_tree
import subprocess
import copy 
#separate application into two phases, the service that starts with the machine and the executable client that is launched.


#copy server source



class AppBuilder():
    def __init__(self):
        self.env = copy.deepcopy(os.environ)
        self.server_files = [
            'manage.py',
            'createsuperuser.py',
            # os.path.join('deploy', 'db.sqlite3')
        ]
        self.new_dirs = [
            'media',
            'daily_reports'
        ]
        self.server_dirs = [
            'common',
            'mdvr_plus',
            os.path.join('assets', 'bundles'),
            'reports',
            'wkhtmltopdf'
        ]
        self.app_dir = os.path.abspath('..')

        self.dest_dir = os.path.abspath(os.path.join('dist', 'app'))
        self.server_dir = os.path.join(self.dest_dir, 'server')
        self.build_dir = os.path.abspath('.')
        self.requirements = os.path.join(self.app_dir, 'requirements.txt')
        self.py_path = os.path.join(self.build_dir, 'dist', 'app','python')

        self.env["PATH"] = self.py_path + ';' + self.env['PATH']
        

    def run(self):
        self.copy_src()
        self.build_service()
        self.build_installer()
        self.build_client()
        self.setup_python()
        self.setup_database()

    def setup_python(self):
        os.chdir(self.build_dir)
        print('copying python')
        copy_tree('python', self.py_path)

        os.chdir(self.py_path)
        subprocess.run(['./python', '-m', 'pip', 'install', '-r', self.requirements], 
            env=self.env)

    def build_client(self):
        os.chdir(self.build_dir)

        code = subprocess.run(['pyinstaller', 'client.spec', '--clean'])

        if code.returncode != 0:
            raise Exception('Failed to build client')

    def build_service(self):
        os.chdir(self.build_dir)
        code = subprocess.run(['pyinstaller', 'service.spec', '--clean'])

        if code.returncode != 0:
            raise Exception('Failed to build service')

    def build_installer(self):
        os.chdir(self.build_dir)

        code = subprocess.run(['pyinstaller', 'install.py', '--clean', '--onefile'])

        if code.returncode != 0:
            raise Exception('Failed to build installer')

    def copy_src(self):
        os.chdir(self.app_dir)
        print('setting up static files')
        result = subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
        os.chdir(self.build_dir)

        print('copying code')
        if os.path.exists(self.dest_dir):
            #clear the exisitng data
            shutil.rmtree(self.dest_dir)
        
        os.makedirs(self.dest_dir)
        
        for dir in self.server_dirs:
            copy_tree(os.path.join(self.app_dir, dir), os.path.join(self.server_dir, dir))

        for dir in self.new_dirs:
            os.makedirs(os.path.join(self.server_dir, dir))

        for fil in self.server_files:
            shutil.copy(os.path.join(self.app_dir, fil), self.server_dir)

        shutil.copy(os.path.join(self.app_dir, 'assets', 'webpack-stats.json'), 
            os.path.join(self.server_dir, 'assets'))

    def setup_database(self):
        os.chdir(self.server_dir)
        #migrate database
        subprocess.run(['python', 'manage.py', 'migrate'], 
            env=self.env)

        #install fixtures
        subprocess.run(['python', 'manage.py', 'loaddata', 'common.json', 
            'reminders.json'], env=self.env)    

        #create superuser
        subprocess.run(['python', 'createsuperuser.py'], env=self.env)
        os.chdir('../..')

if __name__ == '__main__':
    builder = AppBuilder()
    builder.run()