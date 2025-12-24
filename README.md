# P2P Camera Integration

A Home Assistant integration for P2P cameras using the `p2pcam` library.

## Installation

1. 通过HACS添加自定义仓库：
   - 仓库URL: [你的GitHub仓库地址]
   - 类别: Integration

2. 安装后重启Home Assistant

## Configuration

在`configuration.yaml`中添加：

```yaml
camera:
  - platform: p2pcam
    name: "My P2P Camera"  # 可选，默认p2pcam
    host: "camera_host"    # 摄像头主机地址（可选）
    ip_address: "192.168.1.100"  # 摄像头IP地址（可选）
    horizontal_flip: 0     # 0=关闭, 1=开启（可选）
    vertical_flip: 0       # 0=关闭, 1=开启（可选）
    timestamp: 0           # 0=关闭, 1=开启时间戳（可选）
