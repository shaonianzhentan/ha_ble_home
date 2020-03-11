import os, time, re, uuid, logging, json, datetime, threading, bluetooth
from homeassistant.helpers.event import track_time_interval, async_call_later
from homeassistant.components.http import HomeAssistantView

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_ble_home'
VERSION = '1.0'
# 定时器时间
TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=12)

def setup(hass, config):
    cfg = config[DOMAIN]
              
    _LOGGER.info('''
-------------------------------------------------------------------

    蓝牙在家【作者QQ：635147515】
    版本：''' + VERSION + '''    
    项目地址：https://github.com/shaonianzhentan/ha_ble_home
    
-------------------------------------------------------------------''')
    
    ble = BleScan(hass, cfg)
    track_time_interval(hass, ble.interval, TIME_BETWEEN_UPDATES)    
        
    return True

class BleScan():

    def __init__(self, hass, cfg):
        self.thread = None
        self.hass = hass
        self.cfg = cfg

    def scan(self):
        hass = self.hass
        li = self.cfg
        while True:
            # 读取设备信息
            for key in li:
                state = hass.states.get(key)
                if state is not None:
                    mac = li[key].upper()
                    ble_name = bluetooth.lookup_name(mac)
                    if ble_name is not None:
                        # 这里改变实体状态
                        hass.states.set(key, 'home')
                    else:
                        _LOGGER.info("没有找到蓝牙设备【" + mac + "】")
            time.sleep(1)

    def interval(self, now):
        _LOGGER.info('开始扫描')
        if self.thread != None:
            self.thread.join()

        self.thread = threading.Thread(target=self.scan, args=())
        self.thread.start()   
