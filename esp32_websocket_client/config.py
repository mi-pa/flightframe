# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# WebSocket Server Configuration
# Format: "ws://hostname:port/path" or "wss://hostname:port/path"
# Port is optional (defaults to 80 for ws://, 443 for wss://)
# Examples:
#   WS_SERVER = "ws://192.168.1.100:8080/ws"
#   WS_SERVER = "ws://example.com/websocket"
#   WS_SERVER = "wss://secure.example.com/api/ws"
WS_SERVER = "ws://example.com:80"
WS_PATH = "/ws"  # Default path if not specified in WS_SERVER URL

# Connection Settings
RECONNECT_DELAY = 5  # Seconds to wait before reconnecting
MAX_RECONNECT_ATTEMPTS = 10  # Maximum number of reconnection attempts (0 = infinite)
