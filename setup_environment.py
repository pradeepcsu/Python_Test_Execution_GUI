from __future__ import print_function
from __future__ import with_statement
import zipfile
import pip
import sys
import os
if sys.version_info[0] < 3:
    import urllib2 as _urllib
else:
    import urllib.request as _urllib


def fetch_file(url, save_as=None):
    file_name = url.split('/')[-1] if not save_as else save_as
    u = _urllib.urlopen(url)
    with open(file_name, 'wb') as f:
        meta = u.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print("Downloading: {} Bytes: {}".format(file_name, file_size))
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print(status, end='')

##
##def install_drivers():
##    print('Installing Selenium drivers...')
##    base_path = os.path.join(os.getcwd(), 'resources')
##    chromedriver_installed = os.path.isfile(os.path.join(base_path, 'chromedriver.exe'))
##    iedriver_installed = os.path.isfile(os.path.join(base_path, 'IEDriverServer.exe'))
##    maindriver_installed = os.path.isfile(os.path.join(base_path, 'selenium-server-standalone-2.53.0.jar'))
##    batch_script_installed = os.path.isfile(os.path.join(base_path, 'start_selenium.bat'))
##    if chromedriver_installed and iedriver_installed and maindriver_installed and batch_script_installed:
##        pass
##    else:
##        fn = 'drivers.zip'
##        fetch_file('http://90tvmcjnkd.ssfcuad.ssfcu.org/resources/drivers.zip', fn)
##        with zipfile.ZipFile(fn, 'r') as zr:
##            zr.extractall('resources')
##        os.remove(fn)
##    print('... Selenium drivers installed.')


def install_dependencies():
    print('Installing package dependencies...')
    install_dependency('robotframework-selenium2library')
    install_dependency('lxml')
    install_dependency('psycopg2')
    install_dependency('pypiwin32')
    install_dependency('enum34')
    install_dependency('futures')
    print('... package dependencies installed.')


def install_dependency(name):
    print('- Installing: ' + name, end='')
    installed = [p.key for p in pip.get_installed_distributions()]
    if name not in installed:
        pip.main(['install', name])
    print(' ... OK')


def get_resources(wait=False):
    print('Starting environment setup...')
##    install_drivers()
    install_dependencies()
    print('... Environment setup complete.')
    if wait:
        input('Press any key to exit...')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        get_resources()
    else:
        get_resources(wait=True)

