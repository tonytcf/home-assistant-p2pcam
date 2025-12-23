"""常量定义"""
DOMAIN = "p2pcamera"
DEFAULT_NAME = "P2P Camera"

# 配置项
CONF_DEVICE_ID = "device_id"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_STREAM_URL = "stream_url"  # 可选：RTSP流地址

# PTZ相关
PTZ_DIRECTIONS = [
    "up", "down", "left", "right",
    "top_left", "top_right",
    "bottom_left", "bottom_right"
]
DEFAULT_TRAVEL_TIME = 0.125