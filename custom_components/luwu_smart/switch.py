"""Switch platform for Luwu Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart switches based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([LuwuSmartLaserSwitch(coordinator)])


class LuwuSmartLaserSwitch(LuwuSmartEntity, SwitchEntity):
    """Representation of a Luwu Smart laser switch."""

    _attr_translation_key = "laser"
    _attr_icon = "mdi:laser-pointer"

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, "laser")
        self._is_on: bool = False

    @property
    def is_on(self) -> bool:
        """Return true if the laser is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the laser on."""
        _LOGGER.debug("Turning laser on")
        
        try:
            await self.coordinator.send_laser(True)
            self._is_on = True
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to turn on laser: %s", err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the laser off."""
        _LOGGER.debug("Turning laser off")
        
        try:
            await self.coordinator.send_laser(False)
            self._is_on = False
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to turn off laser: %s", err)
