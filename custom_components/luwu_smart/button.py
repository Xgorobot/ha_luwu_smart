"""Button platform for Luwu Smart integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ACTION_GRAB,
    ACTION_HOME,
    ACTION_MOVE_BACKWARD,
    ACTION_MOVE_FORWARD,
    ACTION_RELEASE,
    ACTION_STOP,
    ACTION_TURN_LEFT,
    ACTION_TURN_RIGHT,
    API_CONTROL,
    DOMAIN,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LuwuSmartButtonEntityDescription(ButtonEntityDescription):
    """Describes a Luwu Smart button entity."""
    
    command: str
    icon: str | None = None


BUTTON_DESCRIPTIONS: tuple[LuwuSmartButtonEntityDescription, ...] = (
    LuwuSmartButtonEntityDescription(
        key=ACTION_MOVE_FORWARD,
        translation_key="move_forward",
        command=ACTION_MOVE_FORWARD,
        icon="mdi:arrow-up-bold",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_MOVE_BACKWARD,
        translation_key="move_backward",
        command=ACTION_MOVE_BACKWARD,
        icon="mdi:arrow-down-bold",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_TURN_LEFT,
        translation_key="turn_left",
        command=ACTION_TURN_LEFT,
        icon="mdi:rotate-left",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_TURN_RIGHT,
        translation_key="turn_right",
        command=ACTION_TURN_RIGHT,
        icon="mdi:rotate-right",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_STOP,
        translation_key="stop",
        command=ACTION_STOP,
        icon="mdi:stop",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_GRAB,
        translation_key="grab",
        command=ACTION_GRAB,
        icon="mdi:hand-back-left",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_RELEASE,
        translation_key="release",
        command=ACTION_RELEASE,
        icon="mdi:hand-back-left-outline",
    ),
    LuwuSmartButtonEntityDescription(
        key=ACTION_HOME,
        translation_key="home",
        command=ACTION_HOME,
        icon="mdi:home",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart buttons based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        LuwuSmartButton(coordinator, description)
        for description in BUTTON_DESCRIPTIONS
    ]
    
    async_add_entities(entities)


class LuwuSmartButton(LuwuSmartEntity, ButtonEntity):
    """Representation of a Luwu Smart button."""

    entity_description: LuwuSmartButtonEntityDescription

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        description: LuwuSmartButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        
        if description.icon:
            self._attr_icon = description.icon

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.debug(
            "Button pressed: %s, sending command: %s",
            self.entity_description.key,
            self.entity_description.command,
        )
        
        try:
            await self.coordinator.send_command(
                API_CONTROL,
                self.entity_description.command,
            )
        except Exception as err:
            _LOGGER.error(
                "Failed to send command %s: %s",
                self.entity_description.command,
                err,
            )
