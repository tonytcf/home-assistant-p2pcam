"""P2P Camera Integration for Home Assistant."""
from homeassistant.core import Config, HomeAssistant
from homeassistant.helpers.typing import ConfigType

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the P2P Camera component."""
    return True
