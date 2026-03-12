"""Constants for the Luwu Smart integration."""
from __future__ import annotations

from typing import Final

# Integration domain
DOMAIN: Final = "luwu_smart"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_DEVICE_ID: Final = "device_id"
CONF_TOKEN: Final = "token"
CONF_HA_TOKEN: Final = "ha_token"  # HA long-lived access token for device to call HA

# Default values
DEFAULT_PORT: Final = 80
DEFAULT_NAME: Final = "RIG-Puppy"
DEFAULT_SCAN_INTERVAL: Final = 30

# Device info
MANUFACTURER: Final = "陆吾智能"
MANUFACTURER_EN: Final = "Luwu Dynamics"
MODEL: Final = "LULU-ESP32S3"

# Platforms
PLATFORMS: Final = ["sensor", "camera", "button", "switch", "select"]

# API endpoints
API_STATUS: Final = "/api/status"
API_CONTROL: Final = "/api/control"
API_SENSORS: Final = "/api/sensors"
API_CAMERA_SNAPSHOT: Final = "/api/camera/snapshot"
API_TTS: Final = "/api/tts"
API_HA_CONFIG: Final = "/api/ha_config"  # Send HA config to device

# Commands
CMD_MOVE: Final = "move"
CMD_ACTION: Final = "action"
CMD_EMOTION: Final = "emotion"
CMD_LASER: Final = "laser"

# Puppy actions (12 actions)
PUPPY_ACTIONS: Final = [
    "Wave",
    "Sit", 
    "Stretch",
    "Naughty",
    "Swing",
    "Lookup",
    "Rolling",
    "Angry",
    "Swimming",
    "Pee",
    "Bouncing",
    "Shaking",
    "Stop",
]

# Puppy emotions (8 emotions)
PUPPY_EMOTIONS: Final = [
    "neutral",
    "happy",
    "sad",
    "angry",
    "surprised",
    "sleepy",
    "excited",
    "confused",
]

# Movement directions
MOVE_FORWARD: Final = "forward"
MOVE_BACKWARD: Final = "backward"
MOVE_LEFT: Final = "left"
MOVE_RIGHT: Final = "right"
MOVE_STOP: Final = "stop"

# Default movement parameters
DEFAULT_MOVE_SPEED: Final = 50
DEFAULT_MOVE_TIME: Final = 500

# Sensor types
SENSOR_STATE: Final = "state"
SENSOR_WIFI_RSSI: Final = "wifi_rssi"
SENSOR_BATTERY: Final = "battery"
SENSOR_TEMPERATURE: Final = "temperature"

# Device states
STATE_IDLE: Final = "idle"
STATE_LISTENING: Final = "listening"
STATE_SPEAKING: Final = "speaking"

# Attributes
ATTR_COMMAND: Final = "command"
ATTR_PARAMETERS: Final = "parameters"
ATTR_ACTION: Final = "action"
ATTR_EMOTION: Final = "emotion"
ATTR_VX: Final = "vx"
ATTR_VYAW: Final = "vyaw"
ATTR_TIME: Final = "time"

# Action name translations (for display)
ACTION_TRANSLATIONS: Final = {
    "Wave": "招手",
    "Sit": "坐下",
    "Stretch": "伸展",
    "Naughty": "调皮",
    "Swing": "摇摆",
    "Lookup": "抬头",
    "Rolling": "打滚",
    "Angry": "生气",
    "Swimming": "游泳",
    "Pee": "撒尿",
    "Bouncing": "蹦跳",
    "Shaking": "抖动",
    "Stop": "停止",
}

# Emotion translations (for display)
EMOTION_TRANSLATIONS: Final = {
    "neutral": "正常",
    "happy": "开心",
    "sad": "伤心",
    "angry": "生气",
    "surprised": "惊讶",
    "sleepy": "困倦",
    "excited": "兴奋",
    "confused": "困惑",
}
