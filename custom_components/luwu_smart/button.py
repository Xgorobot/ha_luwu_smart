"""Button platform for Luwu Smart integration."""
from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ACTION_TRANSLATIONS,
    DEFAULT_MOVE_SPEED,
    DEFAULT_MOVE_TIME,
    DOMAIN,
    MOVE_BACKWARD,
    MOVE_FORWARD,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_STOP,
    PUPPY_ACTIONS,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class LuwuSmartActionButtonDescription(ButtonEntityDescription):
    """Describes a Luwu Smart action button entity."""
    
    action: str


@dataclass(frozen=True, kw_only=True)
class LuwuSmartMoveButtonDescription(ButtonEntityDescription):
    """Describes a Luwu Smart move button entity."""
    
    vx: int = 0
    vyaw: int = 0


# Generate action button descriptions for all 12 actions
ACTION_BUTTON_DESCRIPTIONS: tuple[LuwuSmartActionButtonDescription, ...] = tuple(
    LuwuSmartActionButtonDescription(
        key=f"action_{action.lower()}",
        translation_key=f"action_{action.lower()}",
        action=action,
        icon=_get_action_icon(action),
    )
    for action in PUPPY_ACTIONS
)


def _get_action_icon(action: str) -> str:
    """Get icon for action."""
    icons = {
        "Wave": "mdi:hand-wave",
        "Sit": "mdi:seat",
        "Stretch": "mdi:yoga",
        "Naughty": "mdi:emoticon-tongue",
        "Swing": "mdi:swap-horizontal",
        "Lookup": "mdi:arrow-up-bold",
        "Rolling": "mdi:rotate-360",
        "Angry": "mdi:emoticon-angry",
        "Swimming": "mdi:swim",
        "Pee": "mdi:water",
        "Bouncing": "mdi:arrow-collapse-up",
        "Shaking": "mdi:vibrate",
        "Stop": "mdi:stop",
    }
    return icons.get(action, "mdi:dog")


# Move button descriptions
MOVE_BUTTON_DESCRIPTIONS: tuple[LuwuSmartMoveButtonDescription, ...] = (
    LuwuSmartMoveButtonDescription(
        key=f"move_{MOVE_FORWARD}",
        translation_key="move_forward",
        icon="mdi:arrow-up-bold",
        vx=DEFAULT_MOVE_SPEED,
        vyaw=0,
    ),
    LuwuSmartMoveButtonDescription(
        key=f"move_{MOVE_BACKWARD}",
        translation_key="move_backward",
        icon="mdi:arrow-down-bold",
        vx=-DEFAULT_MOVE_SPEED,
        vyaw=0,
    ),
    LuwuSmartMoveButtonDescription(
        key=f"move_{MOVE_LEFT}",
        translation_key="move_left",
        icon="mdi:rotate-left",
        vx=0,
        vyaw=DEFAULT_MOVE_SPEED,
    ),
    LuwuSmartMoveButtonDescription(
        key=f"move_{MOVE_RIGHT}",
        translation_key="move_right",
        icon="mdi:rotate-right",
        vx=0,
        vyaw=-DEFAULT_MOVE_SPEED,
    ),
    LuwuSmartMoveButtonDescription(
        key=f"move_{MOVE_STOP}",
        translation_key="move_stop",
        icon="mdi:stop",
        vx=0,
        vyaw=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart buttons based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities: list[ButtonEntity] = []
    
    # Add action buttons
    for description in ACTION_BUTTON_DESCRIPTIONS:
        entities.append(LuwuSmartActionButton(coordinator, description))
    
    # Add move buttons
    for description in MOVE_BUTTON_DESCRIPTIONS:
        entities.append(LuwuSmartMoveButton(coordinator, description))
    
    async_add_entities(entities)


class LuwuSmartActionButton(LuwuSmartEntity, ButtonEntity):
    """Representation of a Luwu Smart action button."""

    entity_description: LuwuSmartActionButtonDescription

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        description: LuwuSmartActionButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_icon = _get_action_icon(description.action)

    async def async_press(self) -> None:
        """Handle the button press."""
        action = self.entity_description.action
        _LOGGER.debug("Action button pressed: %s", action)
        
        try:
            await self.coordinator.send_action(action)
        except Exception as err:
            _LOGGER.error("Failed to send action %s: %s", action, err)


class LuwuSmartMoveButton(LuwuSmartEntity, ButtonEntity):
    """Representation of a Luwu Smart move button."""

    entity_description: LuwuSmartMoveButtonDescription

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        description: LuwuSmartMoveButtonDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        if description.icon:
            self._attr_icon = description.icon

    async def async_press(self) -> None:
        """Handle the button press."""
        desc = self.entity_description
        _LOGGER.debug(
            "Move button pressed: vx=%s, vyaw=%s",
            desc.vx,
            desc.vyaw,
        )
        
        try:
            await self.coordinator.send_move(
                vx=desc.vx,
                vyaw=desc.vyaw,
                time_ms=DEFAULT_MOVE_TIME,
            )
        except Exception as err:
            _LOGGER.error("Failed to send move command: %s", err)
