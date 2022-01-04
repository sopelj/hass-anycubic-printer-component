"""Test component setup."""
from unittest import mock

from homeassistant import config_entries

from custom_components.anycubic import config_flow


async def test_flow_user_init(hass, enable_custom_integrations):
    """Test the initialization of the form in the first step of the config flow."""
    result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    expected = {
        "data_schema": config_flow.CONFIG_SCHEMA,
        "description_placeholders": None,
        "errors": {},
        "flow_id": mock.ANY,
        "handler": "anycubic",
        "step_id": "user",
        "type": "form",
        "last_step": None,
    }
    assert expected == result


async def test_flow_user_step_no_input(hass, enable_custom_integrations):
    """Test appropriate error when no input is provided."""
    _result = await hass.config_entries.flow.async_init(
        config_flow.DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        _result["flow_id"], user_input={"ip_address": "", "port": 6000}
    )
    assert {"base": "invalid_ip"} == result["errors"]
