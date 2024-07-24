from homeassistant.helpers.entity import Entity

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the PB25 sensors."""
    coordinator = hass.data["pb25"]

    # Create sensor entities for each relevant piece of data
    sensors = [
        PB25Sensor(coordinator, "ttop", "Temperature", "°C"),
        PB25Sensor(coordinator, "Flame", "Flamma", None),
        PB25Sensor(coordinator, "mode", "Läge", None),
        PB25Sensor(coordinator, "alarm2", "Larmtext", None),
        PB25Sensor(coordinator, "alarm1", "Larmstatus", None),  # No unit of measurement for text
        PB25Sensor(coordinator, "glow", "Tändning", None),  # No unit of measurement for text
        # Add other sensors here
    ]

    async_add_entities(sensors)

class PB25Sensor(Entity):
    """Representation of a PB25 sensor."""

    def __init__(self, coordinator, sensor_type, name, unit_of_measurement):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._sensor_type = sensor_type
        self._name = name
        self._unit_of_measurement = unit_of_measurement
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"PB25 {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._coordinator.data is None:
            return None

        # Fetch value from the coordinator's data
        value = self._coordinator.data.get(self._sensor_type)

        if value is None:
            return None

        # Handle numerical values
        if self._unit_of_measurement:
            try:
                # Try to convert to float if a unit of measurement is defined
                return float(value)
            except ValueError:
                # If conversion fails, log an error and return None
                _LOGGER.error(f"Unable to convert value '{value}' for sensor '{self._name}' to float.")
                return None
        else:
            # Return text values as is
            return str(value)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement for the sensor."""
        return self._unit_of_measurement

    async def async_update(self):
        """Update the sensor state."""
        await self._coordinator.async_request_refresh()

