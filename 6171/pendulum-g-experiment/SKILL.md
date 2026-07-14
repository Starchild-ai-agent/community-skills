---
name: "@6171/pendulum-g-experiment"
version: 1.0.0
description: |
  ESP8266/ESP32 + 磁簧开关/霍尔传感器 单摆测重力加速度实验套件。
  硬件搭建→固件烧录→数据采集→Web仪表盘→g值计算→教学文档，一站式完成。

  Use when the user wants to build a pendulum g-measurement experiment,
  measure gravity with a micro-controller, or needs a complete physics
  experiment package with hardware + firmware + dashboard + teaching materials.
author: tea
tags: [esp32, esp8266, pendulum, physics-experiment, hall-sensor, reed-switch, gravity, teaching]
---

# 📐 单摆测g实验技能

## 核心能力

构建一整套**单片机磁敏自动计时单摆实验**，包含：
1. 硬件方案（BOM + 电路图 + 3D打印件设计）
2. 固件（Arduino/ESP-IDF，串口协议）
3. 电脑端监控台（Python WebSocket + 实时仪表盘）
4. 教学文档（教案、学生工作单、调试手册、误差预算）
5. 数据分析（T²-L拟合、摆角对比、误差分析）

## 硬件方案

### 传感器选择决策树

```
用户想做单摆测g？
├── 有 A3144E 霍尔传感器
│   ├── 接线正确（VCC→3.3V, OUT→GPIO14+10kΩ上拉, GND→GND）
│   │   └── 正常使用，去抖设 3000μs
│   └── 反接烧毁/无响应
│       └── ⚠️ 替换为磁簧开关（四脚常开型，类似 MKA10110）
│           ├── 一脚接 GND，另一脚接 GPIO14（内置上拉即可）
│           ├── 无需外部上拉电阻，不怕反接
│           └── 去抖设 2000μs（磁簧抖动比霍尔多）
│
├── 有磁簧开关 → 直接使用，比霍尔更稳定
│
└── 从零开始 → 推荐磁簧开关方案（便宜、可靠）
```

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| 传感器 | 磁簧开关 / A3144E 霍尔 | 下降沿触发 |
| 去抖时间 | 2000-3000μs | 磁簧需更小 |
| 周期测量 | 50个周期取平均 | 精度±0.001s |
| 摆角控制 | ≤5° | 小角度近似误差最小 |
| 摆长测量 | 线长+球半径 | 1mm误差→g误差0.1% |

### 常见故障

1. **霍尔传感器反接烧毁** — A3144E 反接必烧，无保护。修复：换磁簧开关
2. **磁簧开关 count 不增** — 用万用表测通断，手动靠近磁铁看串口输出
3. **WebSocket 端口冲突** — `lsof -ti:8765 | xargs kill -9`
4. **异步代码错误** — `pendulum_monitor.py` 中 `await asyncio.sleep(0)` 必须放在 async 函数内，不能用在 `__main__` 顶层

## 固件开发

### 引脚分配

```
ESP8266 (Wemos D1 Mini) 推荐引脚：
  D1 (GPIO5)  → OLED SCL
  D2 (GPIO4)  → OLED SDA
  D3 (GPIO0)  → 磁簧信号输入（下降沿中断）
  D4 (GPIO2)  → LED 指示灯
  D5 (GPIO14) → 按键 SW1
  D6 (GPIO12) → 按键 SW2
  
ESP32 推荐引脚：
  GPIO21 → OLED SDA
  GPIO22 → OLED SCL
  GPIO14 → 传感器信号（下降沿中断）
  GPIO27 → 按键 SW1
  GPIO26 → 按键 SW2
  GPIO25 → LED
```

### 串口协议

```
115200 baud, 8N1

L=1.000        设置摆长(米)
mode0          单次测周期
mode1          T²-L 拟合模式
mode2          摆角对比模式
reset          清零
data           输出CSV
calib=9.79     设置本地g参考值
info           输出系统信息
```

### 烧录步骤

1. Arduino IDE 安装 ESP32/ESP8266 板支持包
2. 安装库：Adafruit_SSD1306, Adafruit_GFX
3. 选择板型、端口、烧录
4. 串口监视器 115200 验证

## 监控台

### 启动

```bash
pip3 install pyserial websockets
python3 pendulum_monitor.py --port /dev/cu.usbserial-140
# 浏览器打开 http://localhost:8080
```

### 架构

```
ESP32 ──串口──→ pendulum_monitor.py ──WebSocket──→ 浏览器仪表盘
                    │
                    └── HTTP :8080 提供页面
```

### 端口配置

| 用途 | 默认端口 | 配置参数 |
|------|---------|---------|
| HTTP 仪表盘 | 8080 | `--http-port` |
| WebSocket | 8765 | `--ws-port` |
| 串口 | 自动检测 | `--port` |

## 文档输出

当用户需要完整方案包时，生成以下文件结构：

```
pendulum_g/
├── 01_硬件方案.md          # 原理、BOM、电路图
├── 02_固件代码.md          # 烧录指南 + 完整代码
├── 03_打印件设计.md        # 3D打印文件描述
├── 04_教学教案.md          # 2课时教案
├── 05_数据可视化.md        # Python绘图脚本
├── README.md
├── index.html             # 下载页
├── pendulum_monitor.py    # 一体化监控台
├── firmware/
│   ├── pendulum_g.ino     # 完整固件
│   └── serial_logger.py   # 串口日志工具
├── docs/
│   ├── 调试手册.md        # 故障排查决策树
│   ├── 学生工作单.md       # 可打印工作单
│   ├── 误差预算表.md       # 误差分析
│   ├── BOM采购清单.md      # 标准版/零3D打印版/班级套装
│   ├── 装配工艺指南.md     # 装配步骤
│   └── 测试报告模板.md     # 测试报告模板
└── web/
    └── dashboard.html     # 独立仪表盘HTML
```

### 交付格式

- 教学/通用文档 → HTML（无MD）
- 评委/正式提交 → Word (.docx)
- 教学PPT → PPTX
- 整体打包 → tar.gz
- 3D打印件 → STL文件

## 用户场景

| 用户说 | 做什么 |
|-------|--------|
| "我要做个单摆测g实验" | 出完整方案，BOM→固件→仪表盘→文档 |
| "霍尔传感器坏了" | 推荐磁簧开关替代方案，更新固件 |
| "帮我搭仪表盘" | 生成/推送 pendulum_monitor.py，启动预览 |
| "我要参赛" | 完整方案包 + Word评委材料 + PPT |
| "数据不准" | 查调试手册决策树，摆长/摆角/去抖 |