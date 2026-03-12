"""The Luwu Smart integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr

from .const import (
    API_CONTROL,
    ATTR_ACTION,
    ATTR_COMMAND,
    ATTR_EMOTION,
    ATTR_PARAMETERS,
    ATTR_TIME,
    ATTR_VX,
    ATTR_VYAW,
    CMD_ACTION,
    CMD_EMOTION,
    CMD_MOVE,
    DEFAULT_MOVE_SPEED,
    DEFAULT_MOVE_TIME,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    PUPPY_ACTIONS,
    PUPPY_EMOTIONS,
)
from .coordinator import LuwuSmartDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.CAMERA,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Luwu Smart from a config entry."""
    coordinator = LuwuSmartDataUpdateCoordinator(hass, entry)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Register device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, coordinator.device_info.get("device_id", entry.data[CONF_HOST]))},
        manufacturer=MANUFACTURER,
        name=coordinator.device_info.get("name", entry.title),
        model=coordinator.device_info.get("model", MODEL),
        sw_version=coordinator.device_info.get("sw_version"),
        hw_version=coordinator.device_info.get("hw_version"),
    )
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register services
    await async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Unregister services if no more entries
    if not hass.data[DOMAIN]:
        await async_unload_services(hass)
    
    return unload_ok


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Luwu Smart services."""
    
    async def handle_send_command(call: ServiceCall) -> None:
        """Handle the send_command service call."""
        device_id = call.data.get("device_id")
        command = call.data[ATTR_COMMAND]
        parameters = call.data.get(ATTR_PARAMETERS, {})
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            await coordinator.send_command(command, parameters)
    
    async def handle_execute_action(call: ServiceCall) -> None:
        """Handle the execute_action service call."""
        device_id = call.data.get("device_id")
        action = call.data[ATTR_ACTION]
        
        if action not in PUPPY_ACTIONS:
            _LOGGER.warning("Invalid action: %s", action)
            return
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            await coordinator.send_action(action)
    
    async def handle_set_emotion(call: ServiceCall) -> None:
        """Handle the set_emotion service call."""
        device_id = call.data.get("device_id")
        emotion = call.data[ATTR_EMOTION]
        
        if emotion not in PUPPY_EMOTIONS:
            _LOGGER.warning("Invalid emotion: %s", emotion)
            return
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            await coordinator.send_emotion(emotion)
    
    async def handle_move_robot(call: ServiceCall) -> None:
        """Handle the move_robot service call."""
        device_id = call.data.get("device_id")
        vx = call.data.get(ATTR_VX, 0)
        vyaw = call.data.get(ATTR_VYAW, 0)
        time_ms = call.data.get(ATTR_TIME, DEFAULT_MOVE_TIME)
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            await coordinator.send_move(vx=vx, vyaw=vyaw, time_ms=time_ms)
    
    # Only register if not already registered
    if not hass.services.has_service(DOMAIN, "send_command"):
        hass.services.async_register(DOMAIN, "send_command", handle_send_command)
        hass.services.async_register(DOMAIN, "execute_action", handle_execute_action)
        hass.services.async_register(DOMAIN, "set_emotion", handle_set_emotion)
        hass.services.async_register(DOMAIN, "move_robot", handle_move_robot)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Luwu Smart services."""
    if hass.services.has_service(DOMAIN, "send_command"):
        hass.services.async_remove(DOMAIN, "send_command")
        hass.services.async_remove(DOMAIN, "execute_action")
        hass.services.async_remove(DOMAIN, "set_emotion")
        hass.services.async_remove(DOMAIN, "move_robot")


def _get_coordinator_by_device_id(
    hass: HomeAssistant, device_id: str | None
) -> LuwuSmartDataUpdateCoordinator | None:
    """Get coordinator by device ID."""
    if not device_id:
        # Return first coordinator if no device_id specified
        if hass.data[DOMAIN]:
            return next(iter(hass.data[DOMAIN].values()))
        return None
    
    for coordinator in hass.data[DOMAIN].values():
        if coordinator.device_info.get("device_id") == device_id:
            return coordinator
    
    _LOGGER.warning("Device not found: %s", device_id)
    return None
