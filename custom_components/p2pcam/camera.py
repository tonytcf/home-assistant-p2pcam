import logging

import voluptuous as vol

from homeassistant.const import CONF_NAME, CONF_HOST, CONF_IP_ADDRESS
from homeassistant.components.camera import Camera, PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_HORIZONTAL_FLIP = 'horizontal_flip'
CONF_VERTICAL_FLIP = 'vertical_flip'
CONF_TIMESTAMP = 'timestamp'

DEFAULT_NAME = 'p2pcam'
DEFAULT_HORIZONTAL_FLIP = 0
DEFAULT_VERTICAL_FLIP = 0
DEFAULT_TIMESTAMP = 0

REQUIREMENTS = ['opencv-python==4.0.0.21']

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_HOST): cv.string,
    vol.Optional(CONF_IP_ADDRESS): cv.string,
    vol.Optional(CONF_HORIZONTAL_FLIP, default=DEFAULT_HORIZONTAL_FLIP):
        vol.All(vol.Coerce(int), vol.Range(min=0, max=1)),
    vol.Optional(CONF_VERTICAL_FLIP, default=DEFAULT_VERTICAL_FLIP):
        vol.All(vol.Coerce(int), vol.Range(min=0, max=1)),
    vol.Optional(CONF_TIMESTAMP, default=DEFAULT_TIMESTAMP):
        vol.All(vol.Coerce(int), vol.Range(min=0, max=1)),
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the P2P Camera platform."""
    async_add_entities([P2PCam(hass, config)])


class P2PCam(Camera):
    """Representation of a P2P Camera."""

    def __init__(self, hass, config):
        """Initialize the camera."""
        super().__init__()
        import p2pcam as p2pcam_req

        self._name = config.get(CONF_NAME)
        self._host_ip = config.get(CONF_HOST)
        self._target_ip = config.get(CONF_IP_ADDRESS)

        self.camera = p2pcam_req.P2PCam(self._host_ip, self._target_ip)
        self.camera.horizontal_flip = bool(config.get(CONF_HORIZONTAL_FLIP))
        self.camera.vertical_flip = bool(config.get(CONF_VERTICAL_FLIP))  # 修正重复赋值问题
        self.camera.addTimeStamp = bool(config.get(CONF_TIMESTAMP))

    async def async_camera_image(self):
        """Return a still image response from the camera."""
        return await self.hass.async_add_executor_job(
            self.camera.retrieveImage
        )

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name
