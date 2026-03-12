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
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    SENSOR_BATTERY,
    SENSOR_STATE,
    SENSOR_TEMPERATURE,
    SENSOR_WIFI_RSSI,
)
from .coordinator import LuwuSmartDataUpdateCoordinator
from .entity import LuwuSmartEntity


@dataclass(frozen=True, kw_only=True)
class LuwuSmartSensorEntityDescription(SensorEntityDescription):
    """Describes a Luwu Smart sensor entity."""
    
    value_key: str  # Key in coordinator data


SENSOR_DESCRIPTIONS: tuple[LuwuSmartSensorEntityDescription, ...] = (
    LuwuSmartSensorEntityDescription(
        key=SENSOR_STATE,
        translation_key="state",
        icon="mdi:dog",
        value_key="state",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_WIFI_RSSI,
        translation_key="wifi_rssi",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:wifi",
        value_key="wifi_rssi",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_BATTERY,
        translation_key="battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="battery",
    ),
    LuwuSmartSensorEntityDescription(
        key=SENSOR_TEMPERATURE,
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="temperature",
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
    
    for description in SENSOR_DESCRIPTIONS:
        # Skip battery and temperature if they return -1 (not available)
        if description.value_key in ("battery", "temperature"):
            value = coordinator.data.get(description.value_key) if coordinator.data else None
            if value is None or value == -1:
                continue
        entities.append(LuwuSmartSensor(coordinator, description))
    
    # Always add state and wifi_rssi sensors
    if not any(e.entity_description.key == SENSOR_STATE for e in entities):
        entities.append(
            LuwuSmartSensor(
                coordinator,
                next(d for d in SENSOR_DESCRIPTIONS if d.key == SENSOR_STATE),
            )
        )
    if not any(e.entity_description.key == SENSOR_WIFI_RSSI for e in entities):
        entities.append(
            LuwuSmartSensor(
                coordinator,
                next(d for d in SENSOR_DESCRIPTIONS if d.key == SENSOR_WIFI_RSSI),
            )
        )
    
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
        
        value = self.coordinator.data.get(self.entity_description.value_key)
        
        # Return None for unavailable values (-1)
        if value == -1:
            return None
        
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        attrs: dict[str, Any] = {}
        
        if self.entity_description.key == SENSOR_STATE:
            # Add state translation
            state_translations = {
                "idle": "空闲",
                "listening": "聆听中",
                "speaking": "说话中",
            }
            if self.coordinator.data:
                state = self.coordinator.data.get("state")
                if state:
                    attrs["state_zh"] = state_translations.get(state, state)
        
        return attrs
