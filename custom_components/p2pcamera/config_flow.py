"""配置流程"""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_DEVICE_ID, CONF_USERNAME, CONF_PASSWORD, CONF_STREAM_URL

class P2PCameraFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """P2P摄像头配置流程"""

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # 简单验证（实际需根据摄像头型号调整）
            if not user_input.get(CONF_DEVICE_ID):
                errors[CONF_DEVICE_ID] = "missing_device_id"
            else:
                # 检查设备是否已配置
                await self.async_set_unique_id(user_input[CONF_DEVICE_ID])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"P2P Camera ({user_input[CONF_DEVICE_ID]})",
                    data=user_input
                )

        # 配置表单
        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID, msg="设备ID"): str,
            vol.Optional(CONF_USERNAME, msg="用户名"): str,
            vol.Optional(CONF_PASSWORD, msg="密码"): str,
            vol.Optional(CONF_STREAM_URL, msg="RTSP流地址"): str,
        })
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )