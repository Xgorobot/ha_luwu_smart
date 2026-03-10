"""Camera platform for Luwu Smart integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API_CAMERA, DOMAIN
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart camera based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([LuwuSmartCamera(coordinator)])


class LuwuSmartCamera(LuwuSmartEntity, Camera):
    """Representation of a Luwu Smart camera."""

    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_translation_key = "camera"

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
    ) -> None:
        """Initialize the camera."""
        LuwuSmartEntity.__init__(self, coordinator, "camera")
        Camera.__init__(self)
        
        self._attr_name = "Camera"
        self._attr_is_streaming = True
        self._attr_is_recording = False
        self._image: bytes | None = None
        self._session = async_get_clientsession(coordinator.hass)

    @property
    def frame_interval(self) -> float:
        """Return the interval between frames of the MJPEG stream."""
        return 0.1  # 10 FPS

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        url = f"{self.coordinator.base_url}{API_CAMERA}/snapshot"
        
        params: dict[str, Any] = {}
        if width:
            params["width"] = width
        if height:
            params["height"] = height
        
        try:
            async with asyncio.timeout(10):
                async with self._session.get(
                    url, headers=self.coordinator.headers, params=params
                ) as response:
                    if response.status == 200:
                        self._image = await response.read()
                        return self._image
                    _LOGGER.warning(
                        "Failed to get camera image: %s", response.status
                    )
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout getting camera image")
        except aiohttp.ClientError as err:
            _LOGGER.warning("Error getting camera image: %s", err)
        
        return self._image

    async def stream_source(self) -> str | None:
        """Return the stream source URL."""
        return f"{self.coordinator.base_url}{API_CAMERA}/stream"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs: dict[str, Any] = {}
        
        if self.coordinator.data:
            status = self.coordinator.data.get("status", {})
            camera_info = status.get("camera", {})
            
            attrs["resolution"] = camera_info.get("resolution")
            attrs["fps"] = camera_info.get("fps")
            attrs["recording"] = camera_info.get("recording", False)
        
        return attrs
