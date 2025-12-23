"""P2P摄像头实体"""
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN, DEFAULT_NAME, CONF_STREAM_URL
from .p2p_client import P2PClient

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """初始化摄像头实体"""
    p2p_client = hass.data[DOMAIN][entry.entry_id]["client"]
    async_add_entities([P2PCamera(p2p_client, entry.data)], True)

class P2PCamera(Camera):
    def __init__(self, p2p_client: P2PClient, config):
        super().__init__()
        self._p2p_client = p2p_client
        self._device_id = config["device_id"]
        self._name = config.get("name", DEFAULT_NAME)
        self._stream_url = config.get(CONF_STREAM_URL)
        self._attr_unique_id = f"p2pcamera_{self._device_id}"

    @property
    def name(self):
        """实体名称"""
        return self._name

    async def async_camera_image(self, width=None, height=None):
        """获取单帧图像（可选实现）"""
        # 如需支持快照，可通过P2P客户端获取图像二进制数据
        return None

    async def stream_source(self):
        """视频流地址"""
        # 优先使用配置的流地址，否则从P2P客户端获取
        if self._stream_url:
            return self._stream_url
        return await self._p2p_client.get_stream_url()

    @property
    def supported_features(self):
        """支持的功能（这里关联PTZ服务）"""
        return 0  # 如需原生支持，可扩展CameraEntityFeature

    async def async_ptz(self, direction, travel_time):
        """调用PTZ控制（供服务调用）"""
        return await self._p2p_client.ptz_control(direction, travel_time)