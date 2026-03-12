"""Data update coordinator for Luwu Smart integration."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_CONTROL,
    API_SENSORS,
    API_STATUS,
    ATTR_COMMAND,
    ATTR_PARAMETERS,
    CMD_ACTION,
    CMD_EMOTION,
    CMD_LASER,
    CMD_MOVE,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class LuwuSmartDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching Luwu Smart device data."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        self.config_entry = config_entry
        self._host = config_entry.data[CONF_HOST]
        self._port = config_entry.data.get(CONF_PORT, DEFAULT_PORT)
        self._token = config_entry.data.get(CONF_TOKEN)
        self._session = async_get_clientsession(hass)
        self._device_info: dict[str, Any] = {}
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    @property
    def base_url(self) -> str:
        """Return the base URL for API requests."""
        return f"http://{self._host}:{self._port}"

    @property
    def headers(self) -> dict[str, str]:
        """Return headers for API requests."""
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return self._device_info

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            async with asyncio.timeout(10):
                # Get device status
                status_data = await self._fetch_status()
                
                # Get sensor data
                sensor_data = await self._fetch_sensors()
                
                # Update device info from status response
                self._device_info = {
                    "device_id": status_data.get("device_id", self._host),
                    "name": status_data.get("name", "RIG-Puppy"),
                    "model": status_data.get("model", "LULU-ESP32S3"),
                    "sw_version": status_data.get("firmware_version"),
                    "hw_version": status_data.get("hardware_version"),
                }
                
                return {
                    "status": status_data,
                    "sensors": sensor_data,
                    "online": True,
                    # Extract commonly used values
                    "state": status_data.get("state", "idle"),
                    "wifi_rssi": status_data.get("wifi_rssi"),
                    "battery": sensor_data.get("battery", -1),
                    "temperature": sensor_data.get("temperature", -1),
                }
        except asyncio.TimeoutError as err:
            raise UpdateFailed(f"Timeout communicating with device: {err}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _fetch_status(self) -> dict[str, Any]:
        """Fetch device status."""
        url = f"{self.base_url}{API_STATUS}"
        async with self._session.get(url, headers=self.headers) as response:
            response.raise_for_status()
            return await response.json()

    async def _fetch_sensors(self) -> dict[str, Any]:
        """Fetch sensor data."""
        url = f"{self.base_url}{API_SENSORS}"
        try:
            async with self._session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError:
            _LOGGER.debug("Sensor endpoint not available")
            return {}

    async def send_command(
        self, command: str, parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a control command to the device."""
        url = f"{self.base_url}{API_CONTROL}"
        payload: dict[str, Any] = {ATTR_COMMAND: command}
        if parameters:
            payload[ATTR_PARAMETERS] = parameters
        
        _LOGGER.debug("Sending command: %s with parameters: %s", command, parameters)
        
        try:
            async with asyncio.timeout(10):
                async with self._session.post(
                    url, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    return await response.json()
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout sending command: %s", err)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Error sending command: %s", err)
            raise

    async def send_action(self, action: str) -> dict[str, Any]:
        """Send an action command."""
        return await self.send_command(CMD_ACTION, {"action": action})

    async def send_emotion(self, emotion: str) -> dict[str, Any]:
        """Send an emotion command."""
        return await self.send_command(CMD_EMOTION, {"emotion": emotion})

    async def send_move(
        self, vx: int = 0, vyaw: int = 0, time_ms: int = 500
    ) -> dict[str, Any]:
        """Send a move command."""
        return await self.send_command(
            CMD_MOVE, {"vx": vx, "vyaw": vyaw, "time": time_ms}
        )

    async def send_laser(self, on: bool) -> dict[str, Any]:
        """Send a laser command."""
        return await self.send_command(CMD_LASER, {"on": on})
