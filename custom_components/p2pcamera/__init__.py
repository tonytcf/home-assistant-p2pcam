"""P2P摄像头集成初始化"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
from .const import DOMAIN, PTZ_DIRECTIONS, DEFAULT_TRAVEL_TIME, CONF_DEVICE_ID
from .p2p_client import P2PClient

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["camera"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """初始化配置项"""
    # 创建P2P客户端
    p2p_client = P2PClient(
        entry.data[CONF_DEVICE_ID],
        entry.data.get("username"),
        entry.data.get("password")
    )
    await p2p_client.connect()

    # 存储客户端实例
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "client": p2p_client,
        "config": entry.data
    }

    # 注册PTZ服务
    async def handle_ptz_service(call: ServiceCall):
        """处理PTZ服务调用"""
        entity_ids = call.data.get("entity_id")
        movement = call.data["movement"]
        travel_time = call.data.get("travel_time", DEFAULT_TRAVEL_TIME)

        if movement not in PTZ_DIRECTIONS:
            _LOGGER.error(f"Invalid PTZ direction: {movement}")
            return

        # 查找目标实体并执行PTZ
        for entity_id in entity_ids:
            entity = hass.states.get(entity_id)
            if not entity or entity.domain != "camera" or DOMAIN not in entity.attributes.get("friendly_name", ""):
                continue
            # 获取实体对应的摄像头实例
            for camera in hass.data[DOMAIN][entry.entry_id].get("cameras", []):
                if camera.entity_id == entity_id:
                    await camera.async_ptz(movement, travel_time)
                    break

    hass.services.async_register(DOMAIN, "ptz", handle_ptz_service)

    # 加载摄像头平台
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """卸载集成"""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        # 移除服务
        hass.services.async_remove(DOMAIN, "ptz")
    return unload_ok