"""Constants for the PB25 integration."""

from datetime import timedelta

from homeassistant.const import Platform

DOMAIN = "pb25"
PLATFORMS: list[Platform] = [Platform.SENSOR]

CONF_SCAN_INTERVAL = "scan_interval"
DEFAULT_SCAN_INTERVAL = 30
UPDATE_TIMEOUT = 10
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=DEFAULT_SCAN_INTERVAL)
