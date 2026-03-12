# Luwu Smart - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/LuwuDynamics/ha-luwu-smart.svg)](https://github.com/LuwuDynamics/ha-luwu-smart/releases)
[![License](https://img.shields.io/github/license/LuwuDynamics/ha-luwu-smart.svg)](LICENSE)

[English](#english) | [中文](#中文)

---

## English

### Overview

Luwu Smart is a Home Assistant custom integration for connecting and controlling RIG-Puppy robot dogs from Luwu Dynamics.

### Features

- **Robot Control**: 12 preset actions (Wave, Sit, Stretch, etc.) and movement control
- **Emotion Display**: 8 different emotions/expressions
- **Sensor Monitoring**: Device state, WiFi signal strength, battery, temperature
- **Camera Support**: Live snapshot capture
- **Laser Control**: On/off switch for laser pointer
- **Voice Automation**: Trigger HA automations via voice commands through the robot

### Installation

#### HACS (Recommended)

1. Open HACS in your Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/LuwuDynamics/ha-luwu-smart` with category "Integration"
6. Click "Install"
7. Restart Home Assistant

#### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/luwu_smart` folder to your `config/custom_components/` directory
3. Restart Home Assistant

### Configuration

1. Go to **Settings** > **Devices & Services**
2. Click **Add Integration**
3. Search for "Luwu Smart"
4. Enter your device's IP address (port default: 80)

### Supported Entities

| Platform | Description |
|----------|-------------|
| Sensor | Device State (idle/listening/speaking), WiFi RSSI |
| Camera | Snapshot from robot camera |
| Button | 12 Actions + 5 Movement controls |
| Switch | Laser on/off |
| Select | 8 Emotion expressions |

### Services

- `luwu_smart.send_command`: Send custom commands
- `luwu_smart.execute_action`: Execute preset actions
- `luwu_smart.set_emotion`: Change emotion/expression
- `luwu_smart.move_robot`: Control movement (vx, vyaw, duration)

### Voice Automation

The robot can trigger Home Assistant automations via voice. Configure automations like:

```yaml
automation:
  - alias: "Puppy Voice - Turn on office light"
    trigger:
      - platform: event
        event_type: luwu_smart_action
        event_data:
          action: "office_light_on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.office
```

---

## 中文

### 概述

Luwu Smart 是一个 Home Assistant 自定义集成，用于连接和控制陆吾智能的 RIG-Puppy 机器狗。

### 功能特点

- **机器人控制**：12 种预设动作（招手、坐下、伸展等）和移动控制
- **表情显示**：8 种不同的表情
- **传感器监控**：设备状态、WiFi 信号强度、电池、温度
- **摄像头支持**：实时快照捕获
- **激光控制**：激光笔开关
- **语音自动化**：通过机器人语音指令触发 HA 自动化

### 安装方法

#### HACS 安装（推荐）

1. 在 Home Assistant 中打开 HACS
2. 点击"集成"
3. 点击右上角的三个点
4. 选择"自定义存储库"
5. 添加 `https://github.com/LuwuDynamics/ha-luwu-smart`，类别选择"Integration"
6. 点击"安装"
7. 重启 Home Assistant

#### 手动安装

1. 从 GitHub 下载最新版本
2. 将 `custom_components/luwu_smart` 文件夹复制到 `config/custom_components/` 目录
3. 重启 Home Assistant

### 配置方法

1. 进入 **设置** > **设备与服务**
2. 点击 **添加集成**
3. 搜索 "Luwu Smart"
4. 输入设备的 IP 地址（端口默认：80）

### 支持的实体

| 平台 | 描述 |
|------|------|
| 传感器 | 设备状态（空闲/聆听中/说话中）、WiFi 信号强度 |
| 摄像头 | 机器人摄像头快照 |
| 按钮 | 12 个动作 + 5 个移动控制 |
| 开关 | 激光开/关 |
| 选择 | 8 种表情 |

### 服务

- `luwu_smart.send_command`：发送自定义命令
- `luwu_smart.execute_action`：执行预设动作
- `luwu_smart.set_emotion`：切换表情
- `luwu_smart.move_robot`：控制移动（前进速度、转向速度、持续时间）

### 语音自动化

机器人可以通过语音触发 Home Assistant 自动化。配置示例：

```yaml
automation:
  - alias: "Puppy语音-打开办公室灯"
    trigger:
      - platform: event
        event_type: luwu_smart_action
        event_data:
          action: "office_light_on"
    action:
      - service: light.turn_on
        target:
          entity_id: light.office
```

---

## Support

- [GitHub Issues](https://github.com/LuwuDynamics/ha-luwu-smart/issues)
- [Luwu Dynamics](https://www.luwudynamics.com)
