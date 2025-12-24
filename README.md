camera:
  - platform: p2pcam
    name: "客厅P2P摄像头"
    host: "ABC123456789"  # 设备UID（必填）
    ip_address: "192.168.1.100"  # 可选，本地IP
    port: 8000
    username: "admin"
    password: "123456"
    horizontal_flip: false
    vertical_flip: true
    timestamp: true
    timeout: 15
