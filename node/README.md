# 蓝牙在家
在HA里使用的蓝牙检测是否在家

# 安装依赖
```
安装对应依赖
sudo apt-get install bluetooth libbluetooth-dev pkg-config libboost-python-dev libboost-thread-dev libglib2.0-dev python-dev

安装python插件
pip install pybluez

```
# 修改配置

打开`config.yaml`文件

```yaml
url: HomeAssistant访问链接
token: HomeAssistant长令牌
ha_ble_home:
  '设备实体ID': 'MAC地址'
  'person.xiaobai': 'A8:9C:ED:F0:E2:97'
```

# 使用方式

```bash

# 切换到node目录
cd ha_ble_home/node

# 安装依赖包
npm i

# 运行
npm start

```