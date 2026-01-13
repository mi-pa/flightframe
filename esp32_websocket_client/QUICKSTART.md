# ESP32 WebSocket Client - Quick Start Guide

## Quick Setup (3 Steps)

### 1. Flash MicroPython to ESP32
```bash
# Navigate to the MicroPython ESP32 port directory
cd ports/esp32

# Download submodules and build
make submodules
make

# Flash to your ESP32 device
make erase
make deploy
```

### 2. Configure WiFi and Server
Edit `config.py`:
```python
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourPassword"
WS_SERVER = "ws://192.168.1.100:8080"  # Your server IP with port
WS_PATH = "/ws"
```

### 3. Upload and Run
```bash
# Upload files to ESP32
mpremote connect /dev/ttyUSB0 fs cp config.py :
mpremote connect /dev/ttyUSB0 fs cp main.py :
mpremote connect /dev/ttyUSB0 fs cp boot.py :

# Connect and run
mpremote connect /dev/ttyUSB0
>>> import main
>>> main.main()
```

## Test with Local Server

1. Install test server dependencies:
```bash
pip install websockets
```

2. Run test server:
```bash
python test_server.py
```

3. Update ESP32 config to point to your computer's IP

## Common Issues

### "Failed to connect to WiFi"
- Check SSID and password spelling
- Ensure WiFi is 2.4GHz (not 5GHz)
- Move ESP32 closer to router

### "Connection refused" 
- Check server is running
- Verify server IP address
- Check firewall settings

### "Import error: websocket"
- MicroPython firmware needs websocket module
- Use standard ESP32 build (included by default)

### Device not found at /dev/ttyUSB0
- Try /dev/ttyUSB1 or check `ls /dev/tty*`
- On Mac: /dev/cu.usbserial-*
- On Windows: COM3, COM4, etc.
- Install CH340 or CP2102 drivers if needed

## Next Steps

1. Customize `handle_message()` in main.py for your application
2. Add sensors or actuators
3. Implement your business logic
4. Deploy to production with wss:// (secure WebSocket)

## Files Overview

- `main.py` - Main WebSocket client (start here)
- `config.py` - Configuration (edit this first)
- `boot.py` - Auto-start script (optional)
- `advanced_example.py` - Bi-directional communication example
- `test_server.py` - Python test server for development
- `README.md` - Full documentation

## Example: Control LED via WebSocket

Send from server:
```json
{"type": "led_control", "action": "on"}
{"type": "led_control", "action": "off"}
{"type": "led_control", "action": "toggle"}
```

See `advanced_example.py` for full implementation.
