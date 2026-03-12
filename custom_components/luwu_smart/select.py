"""Select platform for Luwu Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    EMOTION_TRANSLATIONS,
    PUPPY_EMOTIONS,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart select entities based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([LuwuSmartEmotionSelect(coordinator)])


class LuwuSmartEmotionSelect(LuwuSmartEntity, SelectEntity):
    """Representation of a Luwu Smart emotion selector."""

    _attr_translation_key = "emotion"
    _attr_icon = "mdi:emoticon"

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
    ) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator, "emotion")
        self._attr_options = PUPPY_EMOTIONS
        self._current_emotion: str = "neutral"

    @property
    def current_option(self) -> str | None:
        """Return the current selected emotion."""
        return self._current_emotion

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        return {
            "emotion_name_zh": EMOTION_TRANSLATIONS.get(
                self._current_emotion, self._current_emotion
            ),
        }

    async def async_select_option(self, option: str) -> None:
        """Change the selected emotion."""
        if option not in PUPPY_EMOTIONS:
            _LOGGER.warning("Invalid emotion: %s", option)
            return
        
        _LOGGER.debug("Selecting emotion: %s", option)
        
        try:
            await self.coordinator.send_emotion(option)
            self._current_emotion = option
            self.async_write_ha_state()
        except Exception as err:
            _LOGGER.error("Failed to set emotion %s: %s", option, err)
