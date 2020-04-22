import os, time, re, uuid, logging, json, datetime, threading, bluetooth, ctypes, inspect
from homeassistant.helpers.event import track_time_interval, async_call_later
from homeassistant.components.http import HomeAssistantView

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_ble_home'
VERSION = '1.1'
# 定时器时间
TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=60)

def setup(hass, config):
    cfg = config[DOMAIN]
              
    _LOGGER.info('''
-------------------------------------------------------------------

    蓝牙在家【作者QQ：635147515】
    版本：''' + VERSION + '''    
    项目地址：https://github.com/shaonianzhentan/ha_ble_home
    
-------------------------------------------------------------------''')
    
    ble = BleScan(hass, cfg)
    hass.data[DOMAIN] = ble

    # 如果HA关闭，则中止扫描
    def homeassistant_stop_event(event):
        ble.is_stop = True

    hass.bus.listen("homeassistant_stop", homeassistant_stop_event)

    track_time_interval(hass, ble.interval, TIME_BETWEEN_UPDATES)    
        
    return True

class BleScan():

    def __init__(self, hass, cfg):
        self.thread = None
        self.hass = hass
        self.cfg = cfg
        self.is_stop = False
        # 初始化计数器
        self.counter = {}
        for key in cfg:
            self.counter[key] = 0
        _LOGGER.debug('初始化蓝牙扫描器')

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
                        hass.states.set(key, 'home', attributes=state.attributes)
                        _LOGGER.debug("【" + ble_name + "】【" + mac + "】检测在家")
                        self.counter[key] = 0
                        time.sleep(10)
                    else:
                        self.counter[key] += 1
                        _LOGGER.debug("【" + mac + "】没有找到蓝牙设备")
                        if self.counter[key] > 6:
                            # 60秒检测不在家，则设置为不在家
                            self.counter[key] = 0
                            hass.states.set(key, 'not_home', attributes=state.attributes)
                            _LOGGER.debug("【" + key + "】检测不在家")
                        # 当没有检测到，1秒钟再检测
                        time.sleep(1)

    def interval(self, now):
        

        if self.thread is not None:
            _LOGGER.debug('终止线程')
            try:
                stop_thread(self.thread)
                self.thread = None
                time.sleep(3)
            except Exception as ex:
                print(ex)

        if self.is_stop == True:
            return

        _LOGGER.debug('开始扫描')
        self.thread = threading.Thread(target=self.scan, args=())
        self.thread.start()   


def _async_raise(tid, exctype):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)