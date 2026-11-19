"""PB25 sensor platform."""

from __future__ import annotations

import logging
import math
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PB25DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="mode",
        name="PB25 Driftsläge",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="ttop",
        name="PB25 Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Flame",
        name="PB25 Flamma",
    ),
    SensorEntityDescription(
        key="glow",
        name="PB25 Tändning",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="alarm1",
        name="PB25 Larmstatus",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="alarm2",
        name="PB25 Larmtext",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="tRoom",
        name="PB25 Rumstemp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="amps",
        name="PB25 Ström",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)

# Suggested object IDs preserve the entity IDs used by the current local version.
ENTITY_OBJECT_IDS = {
    "mode": "pb25_driftslage",
    "ttop": "pb25_temperature",
    "Flame": "pb25_flamma",
    "glow": "pb25_tandning",
    "alarm1": "pb25_larmstatus",
    "alarm2": "pb25_larmtext",
    "tRoom": "pb25_rumstemp",
    "amps": "pb25_strom",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PB25 sensors."""
    coordinator: PB25DataUpdateCoordinator = entry.runtime_data

    async_add_entities(
        PB25Sensor(coordinator, entry, description)
        for description in SENSORS
    )


class PB25Sensor(CoordinatorEntity[PB25DataUpdateCoordinator], SensorEntity):
    """A sensor backed by the PB25 coordinator."""

    entity_description: SensorEntityDescription
    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: PB25DataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._key = description.key
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = description.name
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name=f"PB25 ({coordinator.host})",
            manufacturer="KMP AB",
            model="PB25",
        )

    @property
    def suggested_object_id(self) -> str | None:
        """Suggest a stable initial entity ID while allowing registry edits."""
        return ENTITY_OBJECT_IDS.get(self._key)

    @property
    def native_value(self) -> str | float | None:
        """Return the current PB25 value."""
        raw_value: Any = self.coordinator.data.get(self._key)

        if raw_value is None:
            return None

        if self.entity_description.native_unit_of_measurement:
            if isinstance(raw_value, bool):
                _LOGGER.warning("PB25 returned a boolean for numeric field %s", self._key)
                return None
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                _LOGGER.warning(
                    "Non-numeric PB25 value for field %s: %r",
                    self._key,
                    raw_value,
                )
                return None

            if not math.isfinite(value):
                _LOGGER.warning(
                    "Non-finite PB25 value for field %s: %r",
                    self._key,
                    raw_value,
                )
                return None
            return value

        return str(raw_value)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the PB25 key and raw field value for existing templates."""
        return {
            "pb25_key": self._key,
            "raw": self.coordinator.data.get(self._key),
        }
