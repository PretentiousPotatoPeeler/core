"""SmartHab configuration flow."""
import logging

import pysmarthab
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

# pylint: disable=unused-import
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SmartHabConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """SmartHab config flow."""

    def _show_setup_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""

        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL, default=user_input.get(CONF_EMAIL, "")
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is None:
            return self._show_setup_form(user_input, None)

        username = user_input[CONF_EMAIL]
        password = user_input[CONF_PASSWORD]

        # Check if already configured
        if self.unique_id is None:
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()

        # Setup connection with SmartHab API
        hub = pysmarthab.SmartHab()

        try:
            await hub.async_login(username, password)

            # Verify that passed in configuration works
            if hub.is_logged_in():
                return self.async_create_entry(
                    title=username, data={CONF_EMAIL: username, CONF_PASSWORD: password}
                )

            errors["base"] = "wrong_login"
        except pysmarthab.RequestFailedException:
            _LOGGER.exception("Error while trying to reach SmartHab API")
            errors["base"] = "service"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected error during login")
            errors["base"] = "unknown_error"

        return self._show_setup_form(user_input, errors)

    async def async_step_import(self, user_input):
        """Handle import from legacy config."""
        return await self.async_step_user(user_input)
