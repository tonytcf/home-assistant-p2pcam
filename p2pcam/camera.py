import logging
from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import DOMAIN, CONF_DEVICE_ID, CONF_PASSWORD, CONF_IP_ADDRESS, CONF_PORT, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

try:
    from p2p_camera import P2PClient, ConnectionError as P2PConnectionError
except ImportError:
    P2PClient = None

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """通过配置项初始化摄像头实体"""
    if not P2PClient:
        _LOGGER.error("p2p-camera library not installed. Cannot setup camera.")
        return

    # 创建数据协调器（处理定期更新）
    coordinator = P2PCamCoordinator(hass, entry.data)
    await coordinator.async_config_entry_first_refresh()

    # 添加摄像头实体
    async_add_entities([P2PCamDevice(coordinator, entry)], True)

class P2PCamCoordinator(DataUpdateCoordinator):
    """管理摄像头数据更新"""
    def __init__(self, hass, config):
        super().__init__(
            hass,
            _LOGGER,
            name=f"P2P Camera {config[CONF_DEVICE_ID]}",
            update_interval=30  # 30秒更新一次
        )
        self.config = config
        self.client = None  # P2P客户端实例

    async def _async_update_data(self):
        """获取最新帧数据"""
        try:
            if not self.client:
                # 初始化客户端（同步操作放到线程池）
                self.client = await self.hass.async_add_executor_job(
                    P2PClient,
                    self.config[CONF_DEVICE_ID],
                    self.config[CONF_PASSWORD],
                    self.config.get(CONF_IP_ADDRESS),
                    self.config.get(CONF_PORT, DEFAULT_PORT)
                )
                await self.hass.async_add_executor_job(self.client.connect)
                _LOGGER.info("Connected to P2P camera")

            # 获取一帧图像（JPEG格式）
            frame = await self.hass.async_add_executor_job(self.client.get_frame)
            if not frame:
                raise UpdateFailed("Failed to get frame from camera")
            return frame

        except P2PConnectionError:
            # 连接失败时重置客户端，下次尝试重连
            self.client = None
            raise UpdateFailed("Lost connection to camera. Will retry.")
        except Exception as e:
            raise UpdateFailed(f"Update failed: {str(e)}")

class P2PCamDevice(Camera):
    """P2P摄像头实体"""
    def __init__(self, coordinator, config_entry):
        super().__init__()
        self.coordinator = coordinator
        self._config_entry = config_entry
        self._attr_name = config_entry.title
        self._attr_unique_id = config_entry.data[CONF_DEVICE_ID]
        # 支持的功能（如移动侦测，根据设备实际能力添加）
        self._attr_supported_features = CameraEntityFeature.STREAM

    @property
    def available(self):
        """设备是否可用"""
        return self.coordinator.last_update_success

    async def async_camera_image(self, width=None, height=None):
        """返回最新图像帧"""
        return self.coordinator.data

    async def async_added_to_hass(self):
        """注册协调器更新回调"""
        self.async_on_remove(
            self.coordinator.async_add_listener(self.async_write_ha_state)
        )

    async def async_stream_source(self):
        """返回流地址（如果设备支持RTSP）"""
        # 若P2P设备支持RTSP，可在此返回RTSP URL
        # 例如：return f"rtsp://{self._config_entry.data[CONF_IP_ADDRESS]}:554/stream"
        return None