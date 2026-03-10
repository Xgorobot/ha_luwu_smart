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

# Default values
DEFAULT_PORT: Final = 8080
DEFAULT_NAME: Final = "Luwu Smart Device"
DEFAULT_SCAN_INTERVAL: Final = 30

# Device info
MANUFACTURER: Final = "陆吾智能"
MANUFACTURER_EN: Final = "Luwu Dynamics"

# Platforms
PLATFORMS: Final = ["sensor", "camera", "button", "switch"]

# Sensor types
SENSOR_BATTERY: Final = "battery"
SENSOR_TEMPERATURE: Final = "temperature"
SENSOR_HUMIDITY: Final = "humidity"
SENSOR_DISTANCE: Final = "distance"
SENSOR_STATUS: Final = "status"

# Robot actions
ACTION_MOVE_FORWARD: Final = "move_forward"
ACTION_MOVE_BACKWARD: Final = "move_backward"
ACTION_TURN_LEFT: Final = "turn_left"
ACTION_TURN_RIGHT: Final = "turn_right"
ACTION_STOP: Final = "stop"
ACTION_GRAB: Final = "grab"
ACTION_RELEASE: Final = "release"
ACTION_HOME: Final = "home"

# Switch types
SWITCH_POWER: Final = "power"
SWITCH_AUTO_MODE: Final = "auto_mode"
SWITCH_VOICE: Final = "voice"

# WebSocket events
EVENT_STATE_CHANGED: Final = "state_changed"
EVENT_CONNECTED: Final = "connected"
EVENT_DISCONNECTED: Final = "disconnected"

# API endpoints
API_STATUS: Final = "/api/status"
API_CONTROL: Final = "/api/control"
API_SENSORS: Final = "/api/sensors"
API_CAMERA: Final = "/api/camera"
API_WEBSOCKET: Final = "/ws"

# Attributes
ATTR_COMMAND: Final = "command"
ATTR_PARAMETERS: Final = "parameters"
ATTR_SPEED: Final = "speed"
ATTR_DIRECTION: Final = "direction"
ATTR_DURATION: Final = "duration"
