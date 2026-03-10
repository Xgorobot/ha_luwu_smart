"""Switch platform for Luwu Smart integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    API_CONTROL,
    DOMAIN,
    SWITCH_AUTO_MODE,
    SWITCH_POWER,
    SWITCH_VOICE,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LuwuSmartSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Luwu Smart switch entity."""
    
    command_on: str
    command_off: str
    state_key: str


SWITCH_DESCRIPTIONS: tuple[LuwuSmartSwitchEntityDescription, ...] = (
    LuwuSmartSwitchEntityDescription(
        key=SWITCH_POWER,
        translation_key="power",
        icon="mdi:power",
        command_on="power_on",
        command_off="power_off",
        state_key="power",
    ),
    LuwuSmartSwitchEntityDescription(
        key=SWITCH_AUTO_MODE,
        translation_key="auto_mode",
        icon="mdi:robot",
        command_on="auto_mode_on",
        command_off="auto_mode_off",
        state_key="auto_mode",
    ),
    LuwuSmartSwitchEntityDescription(
        key=SWITCH_VOICE,
        translation_key="voice",
        icon="mdi:microphone",
        command_on="voice_on",
        command_off="voice_off",
        state_key="voice",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart switches based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        LuwuSmartSwitch(coordinator, description)
        for description in SWITCH_DESCRIPTIONS
    ]
    
    async_add_entities(entities)


class LuwuSmartSwitch(LuwuSmartEntity, SwitchEntity):
    """Representation of a Luwu Smart switch."""

    entity_description: LuwuSmartSwitchEntityDescription

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        description: LuwuSmartSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if not self.coordinator.data:
            return None
        
        status = self.coordinator.data.get("status", {})
        return status.get(self.entity_description.state_key, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug(
            "Turning on switch: %s, command: %s",
            self.entity_description.key,
            self.entity_description.command_on,
        )
        
        try:
            await self.coordinator.send_command(
                API_CONTROL,
                self.entity_description.command_on,
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to turn on %s: %s",
                self.entity_description.key,
                err,
            )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug(
            "Turning off switch: %s, command: %s",
            self.entity_description.key,
            self.entity_description.command_off,
        )
        
        try:
            await self.coordinator.send_command(
                API_CONTROL,
                self.entity_description.command_off,
            )
            await self.coordinator.async_request_refresh()
        except Exception as err:
            _LOGGER.error(
                "Failed to turn off %s: %s",
                self.entity_description.key,
                err,
            )
