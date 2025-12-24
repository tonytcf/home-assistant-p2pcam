import logging
import asyncio
from datetime import datetime

import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
)
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

# 配置项定义
CONF_HORIZONTAL_FLIP = 'horizontal_flip'
CONF_VERTICAL_FLIP = 'vertical_flip'
CONF_TIMESTAMP = 'timestamp'
CONF_PORT = 'port'
CONF_TIMEOUT = 'timeout'

# 默认值
DEFAULT_NAME = 'p2pcam'
DEFAULT_HORIZONTAL_FLIP = False
DEFAULT_VERTICAL_FLIP = False
DEFAULT_TIMESTAMP = False
DEFAULT_PORT = 8000
DEFAULT_TIMEOUT = 10  # 秒

# 平台配置 schema（严格验证）
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,  # 设备唯一标识（如UID），改为必填
    vol.Optional(CONF_IP_ADDRESS): cv.string,  # 可选IP地址（用于本地连接）
    vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    vol.Optional(CONF_USERNAME): cv.string,  # 部分设备需要认证
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_HORIZONTAL_FLIP, default=DEFAULT_HORIZONTAL_FLIP): cv.boolean,
    vol.Optional(CONF_VERTICAL_FLIP, default=DEFAULT_VERTICAL_FLIP): cv.boolean,
    vol.Optional(CONF_TIMESTAMP, default=DEFAULT_TIMESTAMP): cv.boolean,
    vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """初始化摄像头平台"""
    _LOGGER.debug("正在设置P2P摄像头平台")
    async_add_entities([P2PCam(hass, config)], True)


class P2PCam(Camera):
    """P2P摄像头实体类"""

    def __init__(self, hass, config):
        super().__init__()
        self.hass = hass
        self._name = config[CONF_NAME]
        self._host = config[CONF_HOST]  # 设备UID/主机名
        self._ip_address = config.get(CONF_IP_ADDRESS)
        self._port = config[CONF_PORT]
        self._username = config.get(CONF_USERNAME)
        self._password = config.get(CONF_PASSWORD)
        self._horizontal_flip = config[CONF_HORIZONTAL_FLIP]
        self._vertical_flip = config[CONF_VERTICAL_FLIP]
        self._timestamp = config[CONF_TIMESTAMP]
        self._timeout = config[CONF_TIMEOUT]
        self._camera = None  # P2P摄像头实例
        self._last_image = None  # 缓存最后一帧图像
        self._available = False  # 设备在线状态

    async def async_added_to_hass(self):
        """实体添加到HASS时初始化连接"""
        await super().async_added_to_hass()
        await self._async_init_camera()

    async def _async_init_camera(self):
        """异步初始化摄像头连接"""
        try:
            import p2pcam as p2pcam_req  # 延迟导入，避免启动时阻塞

            # 初始化摄像头
            self._camera = p2pcam_req.P2PCam(
                uid=self._host,
                ip=self._ip_address,
                port=self._port,
                timeout=self._timeout
            )

            # 处理认证
            if self._username and self._password:
                auth_success = await self.hass.async_add_executor_job(
                    self._camera.login,
                    self._username,
                    self._password
                )
                if not auth_success:
                    _LOGGER.error(f"摄像头 {self._name} 认证失败")
                    return

            # 应用图像配置
            self._camera.horizontal_flip = self._horizontal_flip
            self._camera.vertical_flip = self._vertical_flip
            self._camera.add_timestamp = self._timestamp

            # 测试连接
            test_frame = await self.hass.async_add_executor_job(
                self._camera.retrieveImage
            )
            if test_frame:
                self._available = True
                self._last_image = test_frame
                _LOGGER.info(f"摄像头 {self._name} 初始化成功")
            else:
                _LOGGER.error(f"摄像头 {self._name} 无法获取图像")

        except ImportError:
            _LOGGER.error("未找到p2pcam库，请确保已安装")
        except Exception as e:
            _LOGGER.error(f"摄像头初始化失败: {str(e)}", exc_info=True)

    async def async_camera_image(self, width=None, height=None):
        """获取摄像头图像（带重试机制）"""
        if not self._available or not self._camera:
            await self._async_init_camera()  # 尝试重新连接
            return self._last_image

        try:
            # 使用线程池执行同步操作，避免阻塞事件循环
            image = await asyncio.wait_for(
                self.hass.async_add_executor_job(self._camera.retrieveImage),
                timeout=self._timeout
            )
            if image:
                self._last_image = image
                self._available = True
                return image
            else:
                _LOGGER.warning(f"摄像头 {self._name} 未返回图像")
                self._available = False

        except asyncio.TimeoutError:
            _LOGGER.error(f"获取图像超时（{self._timeout}秒）")
            self._available = False
        except Exception as e:
            _LOGGER.error(f"获取图像失败: {str(e)}")
            self._available = False

        return self._last_image  # 返回缓存的最后一帧

    @property
    def name(self):
        """返回实体名称"""
        return self._name

    @property
    def available(self):
        """返回设备在线状态"""
        return self._available

    @property
    def device_info(self):
        """设备信息（用于HASS设备注册表）"""
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._name,
            "manufacturer": "P2P Camera",
            "model": "Generic P2P Camera",
        }

    @property
    def should_poll(self):
        """启用轮询（根据需要调整间隔，默认30秒）"""
        return True

    async def async_update(self):
        """定期更新设备状态（可选：主动检查连接）"""
        if not self._available:
            await self._async_init_camera()