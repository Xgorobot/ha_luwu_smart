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
    API_SENSORS,
    API_STATUS,
    API_WEBSOCKET,
    CONF_TOKEN,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_STATE_CHANGED,
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
        self._websocket: aiohttp.ClientWebSocketResponse | None = None
        self._ws_task: asyncio.Task | None = None
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
    def ws_url(self) -> str:
        """Return the WebSocket URL."""
        return f"ws://{self._host}:{self._port}{API_WEBSOCKET}"

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
                
                # Update device info
                self._device_info = {
                    "device_id": status_data.get("device_id", self._host),
                    "name": status_data.get("name", "Luwu Smart Device"),
                    "model": status_data.get("model", "Unknown"),
                    "sw_version": status_data.get("firmware_version", "Unknown"),
                    "hw_version": status_data.get("hardware_version", "Unknown"),
                }
                
                return {
                    "status": status_data,
                    "sensors": sensor_data,
                    "online": True,
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
        self, endpoint: str, command: str, parameters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Send a command to the device."""
        url = f"{self.base_url}{endpoint}"
        payload = {"command": command}
        if parameters:
            payload["parameters"] = parameters
        
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

    async def async_start_websocket(self) -> None:
        """Start the WebSocket connection for real-time updates."""
        if self._ws_task is not None:
            return
        
        self._ws_task = self.hass.async_create_task(self._websocket_handler())

    async def async_stop_websocket(self) -> None:
        """Stop the WebSocket connection."""
        if self._ws_task is not None:
            self._ws_task.cancel()
            self._ws_task = None
        
        if self._websocket is not None:
            await self._websocket.close()
            self._websocket = None

    async def _websocket_handler(self) -> None:
        """Handle WebSocket connection and messages."""
        retry_delay = 5
        
        while True:
            try:
                _LOGGER.debug("Connecting to WebSocket: %s", self.ws_url)
                
                async with self._session.ws_connect(
                    self.ws_url, headers=self.headers
                ) as ws:
                    self._websocket = ws
                    _LOGGER.info("WebSocket connected to %s", self._host)
                    retry_delay = 5  # Reset retry delay on successful connection
                    
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            try:
                                data = msg.json()
                                await self._handle_ws_message(data)
                            except ValueError:
                                _LOGGER.warning("Invalid JSON in WebSocket message")
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            _LOGGER.error("WebSocket error: %s", ws.exception())
                            break
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            _LOGGER.info("WebSocket closed")
                            break
                            
            except aiohttp.ClientError as err:
                _LOGGER.warning("WebSocket connection failed: %s", err)
            except asyncio.CancelledError:
                _LOGGER.debug("WebSocket handler cancelled")
                break
            
            self._websocket = None
            _LOGGER.debug("Reconnecting WebSocket in %s seconds", retry_delay)
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)  # Exponential backoff, max 60s

    async def _handle_ws_message(self, data: dict[str, Any]) -> None:
        """Handle incoming WebSocket message."""
        event_type = data.get("event")
        
        if event_type == EVENT_STATE_CHANGED:
            # Update coordinator data with new state
            _LOGGER.debug("State changed event: %s", data)
            await self.async_request_refresh()
        else:
            _LOGGER.debug("Unknown WebSocket event: %s", event_type)
