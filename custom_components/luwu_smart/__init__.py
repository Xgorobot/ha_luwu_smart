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
    ATTR_COMMAND,
    ATTR_DIRECTION,
    ATTR_DURATION,
    ATTR_PARAMETERS,
    ATTR_SPEED,
    DOMAIN,
    MANUFACTURER,
    PLATFORMS,
)
from .coordinator import LuwuSmartDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS_LIST: list[Platform] = [
    Platform.SENSOR,
    Platform.CAMERA,
    Platform.BUTTON,
    Platform.SWITCH,
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
        model=coordinator.device_info.get("model", "Luwu Smart Device"),
        sw_version=coordinator.device_info.get("sw_version"),
        hw_version=coordinator.device_info.get("hw_version"),
    )
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)
    
    # Start WebSocket connection for real-time updates
    await coordinator.async_start_websocket()
    
    # Register services
    await async_setup_services(hass)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Stop WebSocket
    await coordinator.async_stop_websocket()
    
    # Unload platforms
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS_LIST):
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
            await coordinator.send_command(API_CONTROL, command, parameters)
    
    async def handle_move_robot(call: ServiceCall) -> None:
        """Handle the move_robot service call."""
        device_id = call.data.get("device_id")
        direction = call.data[ATTR_DIRECTION]
        speed = call.data.get(ATTR_SPEED, 50)
        duration = call.data.get(ATTR_DURATION)
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            parameters = {"speed": speed}
            if duration:
                parameters["duration"] = duration
            await coordinator.send_command(API_CONTROL, f"move_{direction}", parameters)
    
    async def handle_execute_action(call: ServiceCall) -> None:
        """Handle the execute_action service call."""
        device_id = call.data.get("device_id")
        action = call.data.get("action")
        parameters = call.data.get(ATTR_PARAMETERS, {})
        
        coordinator = _get_coordinator_by_device_id(hass, device_id)
        if coordinator:
            await coordinator.send_command(API_CONTROL, action, parameters)
    
    # Only register if not already registered
    if not hass.services.has_service(DOMAIN, "send_command"):
        hass.services.async_register(DOMAIN, "send_command", handle_send_command)
        hass.services.async_register(DOMAIN, "move_robot", handle_move_robot)
        hass.services.async_register(DOMAIN, "execute_action", handle_execute_action)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload Luwu Smart services."""
    if hass.services.has_service(DOMAIN, "send_command"):
        hass.services.async_remove(DOMAIN, "send_command")
        hass.services.async_remove(DOMAIN, "move_robot")
        hass.services.async_remove(DOMAIN, "execute_action")


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
