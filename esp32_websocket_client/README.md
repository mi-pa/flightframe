# ESP32 WebSocket Client for MicroPython

This is a MicroPython application for ESP32 that connects to a WebSocket server and listens for incoming messages.

## Features

- **WiFi Connection**: Automatically connects to configured WiFi network
- **WebSocket Protocol**: Full WebSocket client implementation with proper handshake
- **Auto-reconnection**: Automatically reconnects if connection is lost
- **Configurable**: Easy configuration through config.py
- **Error Handling**: Robust error handling and connection recovery
- **Message Processing**: Extensible message handler for custom logic

## Requirements

- ESP32 board (ESP32, ESP32-S2, ESP32-S3, ESP32-C3, etc.)
- MicroPython firmware v1.19 or later with websocket module support
- WiFi network access
- WebSocket server to connect to

## File Structure

```
esp32_websocket_client/
├── boot.py               # Boot script example (for reference)
├── simple_example.py     # Simple standalone example
├── advanced_example.py   # Advanced example with GPIO control
├── test_server.py        # Test WebSocket server for development
└── README.md             # This file

Frozen modules (in ports/esp32/modules/):
├── websocket_client.py   # Main WebSocket client (frozen into firmware)
└── ws_config.py          # Configuration module (frozen into firmware)
```

## Installation

### Option 1: Build Firmware with Frozen Modules (Recommended)

For production use, the WebSocket client can be frozen into the firmware:

1. See `ports/esp32/BUILD_INSTRUCTIONS.md` for detailed build instructions
2. The modules will be built into the firmware and available immediately on boot
3. No need to upload Python files separately
4. Saves RAM and simplifies deployment

```bash
# Build MicroPython with frozen WebSocket client
cd ports/esp32
make submodules
make BOARD=ESP32_GENERIC

# Flash to your ESP32 device
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 erase
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 deploy
```

Then use in REPL:
```python
>>> import websocket_client
>>> websocket_client.main()
```

### Option 2: Upload Files Manually (Development)

For development and testing, you can upload the files manually:

Follow the official MicroPython ESP32 installation guide:
https://docs.micropython.org/en/latest/esp32/tutorial/intro.html

```bash
# Build standard MicroPython for ESP32
cd ports/esp32
make submodules
make BOARD=ESP32_GENERIC

# Flash to your ESP32 device
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 erase
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 deploy
```

### Upload Files to ESP32

You can use various tools to upload the Python files to your ESP32:

#### Using `mpremote` (recommended)

```bash
# Install mpremote
pip install mpremote

# Upload files
mpremote connect /dev/ttyUSB0 fs cp config.py :
mpremote connect /dev/ttyUSB0 fs cp main.py :
mpremote connect /dev/ttyUSB0 fs cp boot.py :
```

#### Using `ampy`

```bash
# Install ampy
pip install adafruit-ampy

# Upload files
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put main.py
ampy --port /dev/ttyUSB0 put boot.py
```

#### Using WebREPL

1. Enable WebREPL on your ESP32
2. Use the WebREPL client to upload files

## Configuration

Edit `config.py` to configure your WiFi and WebSocket server settings:

```python
# WiFi Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

# WebSocket Server Configuration
# Format: "ws://hostname:port/path" or "wss://hostname:port/path"
WS_SERVER = "ws://example.com:80"  # WebSocket server URL with port
WS_PATH = "/ws"  # Default path if not specified in WS_SERVER URL

# Connection Settings
RECONNECT_DELAY = 5  # Seconds to wait before reconnecting
MAX_RECONNECT_ATTEMPTS = 10  # Maximum number of reconnection attempts (0 = infinite)
```

### Configuration Options

- **WIFI_SSID**: Your WiFi network name
- **WIFI_PASSWORD**: Your WiFi password
- **WS_SERVER**: WebSocket server URL (ws:// for unsecured, wss:// for secured)
  - Format: `ws://hostname:port` or `ws://hostname:port/path`
  - Port is optional (defaults to 80 for ws://, 443 for wss://)
  - Examples: `ws://192.168.1.100:8080`, `wss://secure.example.com`
- **WS_PATH**: The path to the WebSocket endpoint (used if not in WS_SERVER URL)
- **RECONNECT_DELAY**: Time in seconds to wait before attempting to reconnect
- **MAX_RECONNECT_ATTEMPTS**: Maximum reconnection attempts (set to 0 for infinite retries)

## Usage

### Manual Start

Connect to your ESP32 via serial terminal:

```bash
# Using screen
screen /dev/ttyUSB0 115200

# Using picocom
picocom -b 115200 /dev/ttyUSB0

# Using miniterm
miniterm.py /dev/ttyUSB0 115200
```

Then in the MicroPython REPL:

```python
>>> import main
>>> main.main()
```

### Auto-start on Boot

To automatically start the WebSocket client when the ESP32 boots, edit `boot.py` and uncomment the line:

```python
# main()  # Uncomment this line
```

to:

```python
main()  # Now it will auto-start
```

Then reset the ESP32.

## Customizing Message Handling

The `handle_message()` function in `main.py` is called whenever a message is received. Customize it for your use case:

```python
def handle_message(message):
    """Handle received WebSocket message."""
    print(f"Received message: {message}")
    
    # Example: Parse JSON data
    try:
        import json
        data = json.loads(message)
        
        # Control an LED based on received data
        if data.get('action') == 'led_on':
            from machine import Pin
            led = Pin(2, Pin.OUT)
            led.on()
        elif data.get('action') == 'led_off':
            from machine import Pin
            led = Pin(2, Pin.OUT)
            led.off()
            
    except Exception as e:
        print(f"Error handling message: {e}")
```

## Testing WebSocket Server

For testing purposes, you can use a simple WebSocket echo server. Here's an example using Python:

```python
# test_server.py
import asyncio
import websockets

async def echo(websocket, path):
    print(f"Client connected from {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(echo, "0.0.0.0", 8080):
        print("WebSocket server started on ws://0.0.0.0:8080")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

Run it with:
```bash
pip install websockets
python test_server.py
```

Then configure your ESP32 to connect to this server.

## Troubleshooting

### WiFi Connection Issues

- Verify SSID and password are correct
- Check that your ESP32 is in range of the WiFi network
- Ensure the WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)

### WebSocket Connection Issues

- Verify the server URL and port are correct
- Ensure the WebSocket server is running and accessible
- Check firewall settings on the server
- Test the WebSocket server with another client first

### Module Import Errors

- Ensure your MicroPython firmware includes the `websocket` module
- ESP32 builds should include this by default
- If missing, you may need to build a custom firmware

### Memory Issues

- ESP32 has limited RAM, so handle large messages carefully
- Use `gc.collect()` to free memory when needed
- Consider processing messages in chunks for large data

## Example Output

```
==================================================
ESP32 WebSocket Client
==================================================
Connecting to WiFi: MyNetwork
Waiting for connection...
Connected to WiFi
Network config: ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')
Connecting to example.com:80/ws
TCP connection established to ('93.184.216.34', 80)
Sending WebSocket handshake...
WebSocket handshake successful
Connected to WebSocket server
Listening for messages...
Received message: Hello from server!
Received message: {"action": "update", "value": 42}
```

## Security Considerations

- **Plain WebSocket (ws://)**: Data is sent unencrypted. Use only for testing or on secure networks.
- **Secure WebSocket (wss://)**: For production, use wss:// with TLS/SSL encryption.
- **Credentials**: Never hardcode sensitive credentials. Consider using secure storage or configuration files not tracked in version control.

## License

This code is provided as part of the MicroPython project and follows the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Resources

- [MicroPython ESP32 Quick Reference](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [MicroPython Network Module](https://docs.micropython.org/en/latest/library/network.html)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [MicroPython Forum](https://forum.micropython.org/)
