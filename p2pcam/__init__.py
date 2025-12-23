import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """支持旧版yaml配置（可选）"""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """通过配置项初始化集成"""
    try:
        # 存储配置到hass数据
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = entry.data

        # 转发到camera组件
        await hass.config_entries.async_forward_entry_setup(entry, "camera")
        _LOGGER.info(f"P2P Camera integration setup for {entry.data['device_id']}")
        return True
    except Exception as e:
        _LOGGER.exception(f"Failed to setup entry: {str(e)}")
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸载集成"""
    try:
        unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "camera")
        if unload_ok:
            hass.data[DOMAIN].pop(entry.entry_id)
            _LOGGER.info(f"Unloaded P2P Camera {entry.data['device_id']}")
        return unload_ok
    except Exception as e:
        _LOGGER.error(f"Error unloading entry: {str(e)}")
        return False