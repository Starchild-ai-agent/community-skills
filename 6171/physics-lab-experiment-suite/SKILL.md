---
name: "@6171/physics-lab-experiment-suite"
version: 1.0.0
description: "中学物理实验教学参赛方案套件。包含四个完整实验（单摆测g、声悬浮测声速、向心力定量演示仪、电磁阻尼定量研究），每套含固件源码、3D打印图纸、教学PPT、教学文稿、采购清单、调试手册、视频分镜脚本、模拟器。Use when a teacher/student needs a complete, classroom-ready physics experiment package for competition or teaching."
author: "tea@6171"
tags: [physics, education, experiment, arduino, esp32, esp8266, 3d-printing, teaching, competition]
metadata:
  starchild:
    emoji: "🔬"
    skillKey: physics-lab-experiment-suite
    requires:
      bins: [python3, tar]
      anyBins: [arduino-cli, arduino]
    install:
      - kind: pip
        package: pyserial
        bins: [python3]
      - kind: pip
        package: websockets
        bins: [python3]
user-invocable: true
---

# 🔬 物理实验参赛方案套件

四个完整的中小学实验教学方案，每套都是可交付的参赛材料包。用户只需说"我需要一个物理实验方案"或指定实验名称，你就能解包交付全套材料。

## 包含的实验

| 实验 | 资产包 | 大小 | 核心硬件 |
|------|--------|------|---------|
| **单摆测g** | `pendulum-g.tar.gz` | 454K | ESP8266 + 磁簧开关 |
| **声悬浮测声速** | `acoustic-levitation.tar.gz` | 1.3M | ESP8266 + 超声波换能器 |
| **向心力定量演示仪** | `centripetal-force.tar.gz` | 3.3M | ESP32 + 拉力传感器 |
| **电磁阻尼定量研究** | `electromagnetic-damping.tar.gz` | 235K | (原理分析型) |

## 交付流程

1. **用户指定实验** → 从 `assets/` 中解包对应 `.tar.gz` 到 `output/` 目录
2. **解包后检查目录结构** 确保完整（固件/文档/图纸/PPT/教学文稿/模拟器各一个）
3. **按需交付**：
   - 固件 → 读写 `.ino` 文件，引导用户用 arduino-cli 烧录
   - 3D图纸 → STL/SCAD 文件，说明打印参数
   - 教学文稿 + PPT → 可直接用于参赛提交
   - 运行模拟器 → 打开 `.html` 体验
4. **如果是打包请求** → 将整个 `output/` 目录 tar.gz 后用 `sessions_spawn` 推送到用户硬盘

## 常见问题

- **用户说"三大实验"** → 指单摆+声悬浮+向心力（电磁阻尼是方案B，通常算附加）
- **用户说"打包"** → 必须用 `write_local_file` 或 `sessions_spawn` 推送到用户本地，不能只说"打包好了"
- **固件选择** → 单摆/声悬浮用 ESP8266（Wemos D1 Mini），向心力用 ESP32（ESP32-DevKitC）
- **烧录端口** → macOS 上 `/dev/cu.usbserial-*`，端口号开机后可能变化，需用户确认
- **参赛材料标准** → 每套方案必须包含：装置图×4、电路图、固件、3D图纸、教学PPT、教学文稿、材料清单、采购清单、调试手册、视频脚本

## 解包命令

```bash
# 解包到 output/ 目录
tar xzf skills/physics-lab-experiment-suite/assets/<实验名>.tar.gz -C output/<实验名>/
```

## 各实验目录结构

```
pendulum-g/                   # 单摆测g
├── 固件/                     #  pendulum_g_esp8266.ino (有OLED版)
│                            #  pendulum_g_esp8266_nooled.ino (无OLED版)
├── 图纸/                     #  装置总图 / 电路原理图 / 原理示意图 / 测量方法 (SVG+PNG)
├── 文档/                     #  材料清单 / 采购清单 / 工艺步骤 / 调试手册 / 视频脚本
├── 教学文稿/                  #  PPT / 文稿
├── 工具/                     #  gen_buymenu.py, 模拟器HTML
├── PPT/
└── webapp/

acoustic-levitation/          # 声悬浮测声速
├── 固件/                     #  acoustic_levitation.ino
├── 图纸/                     #  装置/电路/驻波原理/测量方法
├── 文档/                     #  材料清单 / 采购清单 / 工艺步骤 / 调试手册 / 视频脚本
├── PPT/
├── 工具/
└── 教学文稿/

centripetal-force/            # 向心力定量演示仪
├── esp32_firmware/            #  centrifugal_force.ino
├── stl/                       #  旋转臂 / 滑块 3D打印模型
├── webapp/                    #  网页仪表盘
├── tools/                     #  Python工具
├── 接线图/ 工艺图/
├── PPT/ 教学文稿/
└── 文档/                     #  材料清单 / 视频脚本 / 分镜
```

## 资源

- `assets/` — 四个实验的 tar.gz 压缩包
- `scripts/` — 辅助脚本（批量解包、烧录引导等）
- `references/` — 参考文档（参赛标准、评分细则等）