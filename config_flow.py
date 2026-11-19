"""Config flow for PB25."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import normalize_host


class PB25ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a PB25 config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle setup from the UI."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                host = normalize_host(user_input[CONF_HOST])
            except ValueError:
                errors["base"] = "invalid_host"
            else:
                await self.async_set_unique_id(host.casefold())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"PB25 ({host})",
                    data={
                        CONF_HOST: host,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(int, vol.Range(min=1, max=3600)),
                }
            ),
            errors=errors,
        )

    async def async_step_import(
        self,
        import_config: dict[str, Any],
    ):
        """Import an existing YAML configuration."""
        try:
            host = normalize_host(import_config[CONF_HOST])
        except ValueError:
            return self.async_abort(reason="invalid_host")

        await self.async_set_unique_id(host.casefold())
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=f"PB25 ({host})",
            data={
                CONF_HOST: host,
                CONF_SCAN_INTERVAL: import_config.get(
                    CONF_SCAN_INTERVAL,
                    DEFAULT_SCAN_INTERVAL,
                ),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> PB25OptionsFlow:
        """Return the options flow."""
        return PB25OptionsFlow()


class PB25OptionsFlow(OptionsFlowWithReload):
    """Handle PB25 options."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Manage the polling interval."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(
                CONF_SCAN_INTERVAL,
                DEFAULT_SCAN_INTERVAL,
            ),
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=current_interval,
                ): vol.All(int, vol.Range(min=1, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
