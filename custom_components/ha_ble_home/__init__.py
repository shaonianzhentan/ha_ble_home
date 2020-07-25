import os, time, re, uuid, logging, json, datetime, threading, ctypes, inspect, socket
from homeassistant.helpers.event import track_time_interval, async_call_later
from homeassistant.components.http import HomeAssistantView

# 获取MAC地址
def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return "-".join([mac[e:e+2] for e in range(0,11,2)])

# 获取IP
def get_ip():
    return socket.gethostbyname(socket.gethostname())

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_ble_home'
VERSION = '1.2'
URL = '/' + DOMAIN +'-api-' + get_mac_address()
# 定时器时间
TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=60)

def setup(hass, config):
    cfg = config[DOMAIN]
    
    # 判断是否支持蓝牙设备
    IS_BLE = '不支持'
    val = os.system('hciconfig name')
    # 支持蓝牙设备（val=256表示未找到）
    if val == 0:
        IS_BLE = '支持蓝牙'
        ble = BleScan(hass, cfg)
        hass.data[DOMAIN] = ble
        # 如果HA关闭，则中止扫描
        def homeassistant_stop_event(event):
            ble.is_stop = True

        hass.bus.listen("homeassistant_stop", homeassistant_stop_event)

        track_time_interval(hass, ble.interval, TIME_BETWEEN_UPDATES)    
    else:
        # 没有蓝牙设备，使用API监听
        hass.http.register_view(HassGateView)
              
    _LOGGER.info('''
-------------------------------------------------------------------

    蓝牙在家【作者QQ：635147515】
    版本：''' + VERSION + '''
    支持蓝牙：''' + IS_BLE + '''
    API地址：''' + 'http://' + get_ip() + ':8123' + URL + '''
    项目地址：https://github.com/shaonianzhentan/ha_ble_home
    
-------------------------------------------------------------------''')
    return True

class HassGateView(HomeAssistantView):

    url = URL
    name = DOMAIN
    requires_auth = False
    
    async def post(self, request):
        hass = request.app["hass"]
        res = await request.json()
        if 'entity_id' in res and 'state' in res:
            # 实体ID
            _entity_id = res['entity_id']
            # 实体状态
            _state = res['state']
            # 获取当前实体
            state = hass.states.get(_entity_id)
            if state is not None:                
                # 这里改变实体状态
                hass.states.async_set(_entity_id, _state, attributes=state.attributes)
                return self.json({'code':0, 'msg': '【' + state.attributes['friendly_name'] + '】状态设置成功'})

        return self.json({'code':1, 'msg': '参数不正确'})

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
        import bluetooth
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