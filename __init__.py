import aiohttp
import async_timeout
import logging
import re
import json  # Importera json-biblioteket
import asyncio  # Importera asyncio-biblioteket
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import discovery
from homeassistant.const import CONF_HOST
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from datetime import timedelta

DOMAIN = "pb25"
PLATFORMS = ["sensor"]

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Optional('scan_interval', default=30): vol.All(int, vol.Range(min=1)),  # Default to 30 seconds
    })
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    """Set up the PB25 integration."""
    _LOGGER.debug("Setting up PB25 integration")
    conf = config.get(DOMAIN)
    if conf is None:
        _LOGGER.error("No configuration found for PB25")
        return False

    host = conf[CONF_HOST]
    scan_interval = conf.get('scan_interval', 30)  # Default to 30 seconds

    _LOGGER.debug(f"PB25 host: {host}, scan_interval: {scan_interval}")

    session = aiohttp.ClientSession()

    async def async_update_data():
        """Fetch data from PB25."""
        try:
            _LOGGER.debug("Fetching data from PB25")
            async with async_timeout.timeout(10):
                response = await session.get(f'http://{host}/data.html')
                text = await response.text()  # Read the response as text

                # Extract JSON from the text if possible
                try:
                    # Assume the JSON data is directly in the response body
                    data = re.search(r'{.*}', text)
                    if data:
                        json_text = data.group(0)
                        _LOGGER.debug(f"Extracted JSON text: {json_text}")
                        parsed_data = json.loads(json_text)
                        _LOGGER.debug(f"Data received from PB25: {parsed_data}")
                        return parsed_data
                    else:
                        _LOGGER.error("No JSON data found in response")
                        raise UpdateFailed("No JSON data found in response")
                except ValueError as e:
                    _LOGGER.error(f"Failed to parse JSON from response: {e}")
                    raise UpdateFailed(f"Failed to parse JSON from response: {e}")

        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error(f"Error fetching data: {err}")
            raise UpdateFailed(f"Error fetching data: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="PB25",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            discovery.async_load_platform(hass, platform, DOMAIN, {}, config)
        )

    return True

