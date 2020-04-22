#! /usr/bin/python
'''

安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev

安装python插件
pip install pybluez

'''

import json
import time
import sys
import bluetooth

mac = str(sys.argv[1]).upper()

name = bluetooth.lookup_name(mac)
if name == None:
    name = ''

# 输出信息
print(json.dumps({
    'scan_time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
    'name': name
}))