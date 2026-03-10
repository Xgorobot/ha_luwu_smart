# Luwu Smart - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/LuwuDynamics/ha-luwu-smart.svg)](https://github.com/LuwuDynamics/ha-luwu-smart/releases)
[![License](https://img.shields.io/github/license/LuwuDynamics/ha-luwu-smart.svg)](LICENSE)

[English](#english) | [中文](#中文)

---

## English

### Overview

Luwu Smart is a Home Assistant custom integration for connecting and controlling embodied intelligence devices from Luwu Dynamics (陆吾智能).

### Features

- **Robot Control**: Move forward, backward, turn, grab, release, and navigate home
- **Sensor Monitoring**: Battery level, temperature, humidity, distance sensors
- **Camera Support**: Live video streaming and snapshot capture
- **Automation Ready**: Full integration with Home Assistant automations and scripts

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
4. Enter your device's IP address and port
5. (Optional) Enter API token if authentication is required

### Supported Entities

| Platform | Description |
|----------|-------------|
| Sensor | Battery, Temperature, Humidity, Distance, Status |
| Camera | Live video stream and snapshots |
| Button | Movement controls (Forward, Backward, Left, Right, Stop, Grab, Release, Home) |
| Switch | Power, Auto Mode, Voice Control |

### Services

- `luwu_smart.send_command`: Send custom commands to the device
- `luwu_smart.move_robot`: Control robot movement with direction and speed
- `luwu_smart.execute_action`: Execute predefined actions

---

## 中文

### 概述

陆吾智能是一个 Home Assistant 自定义集成，用于连接和控制陆吾智能的具身智能设备。

### 功能特点

- **机器人控制**：前进、后退、转向、抓取、释放和返航
- **传感器监控**：电池电量、温度、湿度、距离传感器
- **摄像头支持**：实时视频流和快照捕获
- **自动化就绪**：完全支持 Home Assistant 自动化和脚本

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
3. 搜索"Luwu Smart"
4. 输入设备的 IP 地址和端口
5. （可选）如果需要认证，请输入 API 令牌

### 支持的实体

| 平台 | 描述 |
|------|------|
| 传感器 | 电池、温度、湿度、距离、状态 |
| 摄像头 | 实时视频流和快照 |
| 按钮 | 移动控制（前进、后退、左转、右转、停止、抓取、释放、回家） |
| 开关 | 电源、自动模式、语音控制 |

### 服务

- `luwu_smart.send_command`：向设备发送自定义命令
- `luwu_smart.move_robot`：控制机器人移动方向和速度
- `luwu_smart.execute_action`：执行预定义动作

---

## Support

- [GitHub Issues](https://github.com/LuwuDynamics/ha-luwu-smart/issues)
- [Luwu Dynamics Website](https://www.luwudynamics.com)
