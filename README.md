# 蓝牙在家
在HA里使用的蓝牙检测是否在家

# 安装依赖
```
安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev

安装python插件
pip install pybluez

```

# 使用方式

```
# 设备实体: 蓝牙MAC地址
ha_ble_home:
  'person.xiaobai': 'A8:9C:ED:F0:E2:97'

```