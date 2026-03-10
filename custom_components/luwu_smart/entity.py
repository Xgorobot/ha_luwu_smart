"""Base entity for Luwu Smart integration."""
from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import LuwuSmartDataUpdateCoordinator


class LuwuSmartEntity(CoordinatorEntity[LuwuSmartDataUpdateCoordinator]):
    """Base class for Luwu Smart entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        entity_key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entity_key = entity_key
        
        device_id = coordinator.device_info.get(
            "device_id", coordinator.config_entry.data[CONF_HOST]
        )
        
        self._attr_unique_id = f"{device_id}_{entity_key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer=MANUFACTURER,
            name=coordinator.device_info.get("name", "Luwu Smart Device"),
            model=coordinator.device_info.get("model", "Unknown"),
            sw_version=coordinator.device_info.get("sw_version"),
            hw_version=coordinator.device_info.get("hw_version"),
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("online", False)
        )
