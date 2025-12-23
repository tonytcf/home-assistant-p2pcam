import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from .const import DOMAIN, CONF_DEVICE_ID, CONF_PASSWORD, CONF_IP_ADDRESS

class P2PCamConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # 验证设备信息（此处简化，实际需调用P2P库测试连接）
            try:
                # 假设存在验证函数
                # await validate_p2p_connection(user_input[CONF_DEVICE_ID], user_input[CONF_PASSWORD])
                return self.async_create_entry(
                    title=user_input.get("name", DEFAULT_NAME),
                    data=user_input
                )
            except Exception:
                errors["base"] = "connection_failed"

        data_schema = vol.Schema({
            vol.Required(CONF_DEVICE_ID): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Optional(CONF_IP_ADDRESS): str,
            vol.Optional("name", default=DEFAULT_NAME): str
        })

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=errors
        )