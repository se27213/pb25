"""Data coordinator for PB25."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any
from urllib.parse import urlsplit

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN, UPDATE_TIMEOUT

_LOGGER = logging.getLogger(__name__)


def normalize_host(host: str) -> str:
    """Validate and normalize the bare host value used by the original integration."""
    host = host.strip()
    if not host or any(character.isspace() for character in host) or "://" in host:
        raise ValueError("Enter a hostname or IP address, optionally with a port")

    try:
        parsed = urlsplit(f"http://{host}")
        if (
            parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in ("", "/")
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Enter a hostname or IP address, optionally with a port")
        parsed.port  # Validate the port, if supplied.
    except ValueError as err:
        raise ValueError(
            "Enter a hostname or IP address, optionally with a port"
        ) from err

    return parsed.netloc


class PB25DataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch and store data from a PB25 device."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        scan_interval: int,
        config_entry: ConfigEntry | None = None,
    ) -> None:
        """Initialize the coordinator."""
        self.host = normalize_host(host)
        self.session = async_get_clientsession(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
            config_entry=config_entry,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and parse the documented-by-existing-code PB25 endpoint."""
        url = f"http://{self.host}/data.html"

        try:
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=UPDATE_TIMEOUT),
            ) as response:
                response.raise_for_status()
                response_text = await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeError) as err:
            raise UpdateFailed(f"Error fetching data from PB25: {err}") from err

        decoder = json.JSONDecoder()
        offset = 0
        while (start := response_text.find("{", offset)) != -1:
            try:
                data, end = decoder.raw_decode(response_text, start)
            except json.JSONDecodeError:
                offset = start + 1
                continue

            if isinstance(data, dict):
                return data
            offset = end

        raise UpdateFailed("No JSON object found in PB25 response")
