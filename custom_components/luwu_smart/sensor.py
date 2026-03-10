"""Sensor platform for Luwu Smart integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    UnitOfLength,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SENSOR_BATTERY,
    SENSOR_DISTANCE,
    SENSOR_HUMIDITY,
    SENSOR_STATUS,
    SENSOR_TEMPERATURE,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity


@dataclass(frozen=True, kw_only=True)
class LuwuSmartSensorEntityDescription(SensorEntityDescription):
    """Describes a Luwu Smart sensor entity."""
    
    value_fn: str  # Key path in sensor data


SENSOR_DESCRIPTIONS: tuple[LuwuSmartSensorEntityDescription, ...] = (
    LuwuSmartSensorEntityDescription(
        key=SENSOR_BATTERY,
        translation_key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="battery",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_TEMPERATURE,
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="temperature",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_HUMIDITY,
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="humidity",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_DISTANCE,
        translation_key="distance",
        native_unit_of_measurement=UnitOfLength.CENTIMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn="distance",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_STATUS,
        translation_key="status",
        device_class=None,
        value_fn="status",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Luwu Smart sensors based on a config entry."""
    coordinator: LuwuSmartDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities: list[LuwuSmartSensor] = []
    
    # Get available sensors from device data
    sensor_data = coordinator.data.get("sensors", {}) if coordinator.data else {}
    status_data = coordinator.data.get("status", {}) if coordinator.data else {}
    
    for description in SENSOR_DESCRIPTIONS:
        # Check if this sensor is available from the device
        if description.value_fn in sensor_data or description.value_fn in status_data:
            entities.append(LuwuSmartSensor(coordinator, description))
    
    # If no sensors found, add default ones
    if not entities:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(LuwuSmartSensor(coordinator, description))
    
    async_add_entities(entities)


class LuwuSmartSensor(LuwuSmartEntity, SensorEntity):
    """Representation of a Luwu Smart sensor."""

    entity_description: LuwuSmartSensorEntityDescription

    def __init__(
        self,
        coordinator: LuwuSmartDataUpdateCoordinator,
        description: LuwuSmartSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        # Try to get value from sensors first, then status
        sensors = self.coordinator.data.get("sensors", {})
        status = self.coordinator.data.get("status", {})
        
        value = sensors.get(self.entity_description.value_fn)
        if value is None:
            value = status.get(self.entity_description.value_fn)
        
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs: dict[str, Any] = {}
        
        if self.coordinator.data:
            sensors = self.coordinator.data.get("sensors", {})
            # Add any related attributes
            if self.entity_description.key == SENSOR_STATUS:
                attrs["last_action"] = sensors.get("last_action")
                attrs["error_code"] = sensors.get("error_code")
        
        return attrs
