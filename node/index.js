const path = require('path')
const fs = require('fs')
const YAML = require('yaml')
const HomeAssistant = require('homeassistant');
const { PythonShell } = require('python-shell')

// 蓝牙检测
class DeviceTracker {

    constructor({ device, mac }) {
        this.device = device
        this.mac = mac
        console.log('设备：', device, '，MAC地址：', mac)
        this.update()
    }

    set_state(state) {
        let arr = this.device.split('.')
        hass.states.get(arr[0], arr[1]).then(res => {
            res['state'] = state
            hass.states.update(arr[0], arr[1], res);
        })
        console.log(new Date().toLocaleString(), this.device, state)
    }

    update() {
        PythonShell.run(path.resolve(__dirname, 'ble.py'), { args: [this.mac] }, (err, results) => {
            let time = 5000
            if (!err) {
                try {
                    let obj = JSON.parse(results[0])
                    // console.log(obj)
                    if (obj.name) {
                        // 设置在家
                        this.set_state('home')
                        this.count = 0
                        // 20秒检测
                        time = 20000
                    } else {
                        // 如果超过十次没有找到设备，则判断不在家
                        if (this.count > 10) {
                            // 设置不在家
                            this.set_state('not_home')
                            this.count = 0
                        }
                        // 如果没有检测到人，则计数加1
                        this.count += 1
                    }
                } catch{ }
            } else {
                console.log('出现错误：', err)
            }
            // 超时更新
            setTimeout(() => this.update(), time)
        });
    }
}

// 读取配置
const file = fs.readFileSync('./config.yaml', 'utf8')
const config = YAML.parse(file)
// 读取URL
let url = new URL(config.url)

const hass = new HomeAssistant({
    host: `${url.protocol}//${url.hostname}`,
    port: url.port,
    token: config.token,
    ignoreCert: false
});

let devices = config.ha_ble_home
let arr = []
Object.keys(devices).forEach(k => {
    arr.push(new DeviceTracker({ device: k, mac: devices[k] }))
})
