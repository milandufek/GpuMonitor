import os
import time
from datetime import datetime
from optparse import OptionParser
from platform import system
import subprocess

import requests

"""
    Monitoring GPU and graphical card memory using nvidia-smi binary.
    
    Params:
        -p  => period in sec
        -u  => URL to send the stats byt get method
"""

DEFAULT_URL = 'https://localhost:8000'
SCRIPT_DIR = r'C:\run'


def get_gpu_info():
    try:
        smi_path = r'C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe'
        info = os.popen("\"" + smi_path + "\"" + " --query-gpu=utilization.gpu,utilization.memory --format=csv") \
            .read().split('\n')
        parse_info = info[1].replace('%', '').split(',')
        return parse_info[0].strip(), parse_info[1].strip()
    except IndexError:
        print('Error: Cannot get GPU info')
        return -1


def access_url(url_, gpu_val, gmem_val):
    try:
        resp = requests.get(f'{url_}?cpu={gpu_val}&ram={gmem_val}')
        if resp.status_code == 200:
            script = os.path.join(SCRIPT_DIR, resp.content.decode('UTF-8').strip())
            run_script(script)
        return 0
    except requests.exceptions.ConnectionError:
        print(f'Error: Cannot access URL ({url_})')
        return -1


def run_script(path):
    if os.path.isfile(path):
        rc = subprocess.call(path)
        print('RC', rc)
        return rc
    return -1


if system() != 'Windows':
    exit(1)

op = OptionParser()
op.add_option('-p', '--period', dest='period', type=int, default=30, help='Period in sec')
op.add_option('-u', '--url', dest='url', default=DEFAULT_URL, help='URL')
option, _ = op.parse_args()
refresh = option.period
url = option.url

while True:
    gpu_load, gmem_load = get_gpu_info()
    print(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: GPU={gpu_load}%\t GMEM={gmem_load}%')
    access_url(url, gpu_load, gmem_load)
    time.sleep(refresh)
