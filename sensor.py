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
    PERCENTAGE,
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
        name="Driftsläge",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="ttop",
        name="Temperatur",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Flame",
        name="Flamma",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="glow",
        name="Tändning",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="alarm1",
        name="Larmstatus",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="alarm2",
        name="Larmtext",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SensorEntityDescription(
        key="tRoom",
        name="Rumstemp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="xFan",
        name="Förbränningsfläkt",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="cFan",
        name="Konvektionsfläkt",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="amps",
        name="Ström",
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
    "xFan": "pb25_forbranningsflakt",
    "cFan": "pb25_konvektionsflakt",
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
    _attr_has_entity_name = True

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
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.host)},
            name="PB25",
            manufacturer="KMP AB",
            model="PB25",
        )

    @property
    def suggested_object_id(self) -> str | None:
        """Suggest a stable initial entity ID while allowing registry edits."""
        return ENTITY_OBJECT_IDS.get(self._key)

    @property
    def native_value(self) -> str | float | None:
        """Return a numeric value as a number and preserve textual status values."""
        raw_value: Any = self.coordinator.data.get(self._key)

        if raw_value is None:
            return None

        if isinstance(raw_value, bool):
            if self.entity_description.native_unit_of_measurement:
                _LOGGER.warning(
                    "PB25 returned a boolean for numeric field %s",
                    self._key,
                )
                return None
            return str(raw_value)

        try:
            numeric_value = float(raw_value)
        except (TypeError, ValueError):
            if self.entity_description.native_unit_of_measurement:
                _LOGGER.warning(
                    "Non-numeric PB25 value for field %s: %r",
                    self._key,
                    raw_value,
                )
                return None
            return str(raw_value)

        if not math.isfinite(numeric_value):
            _LOGGER.warning(
                "Non-finite PB25 value for field %s: %r",
                self._key,
                raw_value,
            )
            return None

        return numeric_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the PB25 key and a type-normalized field value."""
        raw_value: Any = self.coordinator.data.get(self._key)

        if raw_value is not None and not isinstance(raw_value, bool):
            try:
                numeric_value = float(raw_value)
            except (TypeError, ValueError):
                pass
            else:
                raw_value = (
                    numeric_value if math.isfinite(numeric_value) else None
                )

        return {
            "pb25_key": self._key,
            "raw": raw_value,
        }
