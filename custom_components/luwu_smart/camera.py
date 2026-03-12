"""Camera platform for Luwu Smart integration."""
from __future__ import annotations

import asyncio
import logging

import aiohttp

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import API_CAMERA_SNAPSHOT, DOMAIN
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

    _attr_translation_key = "camera"

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
    ) -> None:
        """Initialize the camera."""
        LuwuSmartEntity.__init__(self, coordinator, "camera")
        Camera.__init__(self)
        
        self._image: bytes | None = None
        self._session = async_get_clientsession(coordinator.hass)

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        url = f"{self.coordinator.base_url}{API_CAMERA_SNAPSHOT}"
        
        try:
            async with asyncio.timeout(10):
                async with self._session.get(
                    url, headers=self.coordinator.headers
                ) as response:
                    if response.status == 200:
                        self._image = await response.read()
                        return self._image
                    _LOGGER.warning(
                        "Failed to get camera image: HTTP %s", response.status
                    )
        except asyncio.TimeoutError:
            _LOGGER.warning("Timeout getting camera image")
        except aiohttp.ClientError as err:
            _LOGGER.warning("Error getting camera image: %s", err)
        
        return self._image
