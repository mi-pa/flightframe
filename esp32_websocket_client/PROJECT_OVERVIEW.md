# ESP32 WebSocket Client - Project Overview

## What This Project Does

This is a complete MicroPython application for ESP32 microcontrollers that:

1. **Connects to WiFi** - Automatically connects to your configured WiFi network
2. **Establishes WebSocket Connection** - Connects to a WebSocket server using the standard WebSocket protocol
3. **Listens for Messages** - Continuously listens for incoming messages from the server
4. **Handles Reconnection** - Automatically reconnects if the connection is lost
5. **Extensible** - Easy to customize for your specific use case

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    ESP32                         │
│  ┌──────────────────────────────────────────┐  │
│  │         MicroPython Runtime               │  │
│  │  ┌────────────────────────────────────┐  │  │
│  │  │     WebSocket Client App           │  │  │
│  │  │  • WiFi Connection                 │  │  │
│  │  │  • WebSocket Protocol Handler      │  │  │
│  │  │  • Message Processor               │  │  │
│  │  │  • Auto-reconnection Logic         │  │  │
│  │  └────────────────────────────────────┘  │  │
│  │                                            │  │
│  │  Built-in Modules:                        │  │
│  │  • network  - WiFi connectivity          │  │
│  │  • socket   - TCP/IP communication       │  │
│  │  • websocket - WebSocket protocol        │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
                      │
                      │ WiFi
                      ▼
        ┌─────────────────────────┐
        │    WiFi Router/AP       │
        └─────────────────────────┘
                      │
                      │ Internet/LAN
                      ▼
        ┌─────────────────────────┐
        │   WebSocket Server      │
        │   • Node.js             │
        │   • Python              │
        │   • Go                  │
        │   • Any WS server       │
        └─────────────────────────┘
```

## Files Explained

### Core Files

#### `config.py`
Configuration file containing:
- WiFi credentials (SSID and password)
- WebSocket server details (URL, port, path)
- Connection settings (reconnect delay, max attempts)

**Important**: Edit this file before running the client!

#### `main.py`
Main application file that implements:
- WiFi connection logic
- WebSocket handshake
- Message receiving loop
- Error handling and reconnection
- Message handler (customize this for your needs)

This is the main entry point for the application.

#### `boot.py`
Boot script that runs when ESP32 starts. By default, it:
- Performs garbage collection
- Imports main.py (but doesn't auto-start)
- Can be modified to auto-start the WebSocket client

### Example Files

#### `simple_example.py`
Minimal example showing the basics:
- How to connect to WiFi
- How to establish a WebSocket connection
- How to receive messages
- Good starting point for learning

#### `advanced_example.py`
Advanced example demonstrating:
- Bi-directional communication (send and receive)
- JSON message parsing
- GPIO control via WebSocket commands
- LED control example
- Status reporting back to server

#### `test_server.py`
Python WebSocket test server for development:
- Accepts WebSocket connections
- Sends periodic test messages
- Echoes received messages
- Useful for testing without a real server

### Documentation

#### `README.md`
Complete documentation including:
- Feature overview
- Requirements
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting
- Security considerations

#### `QUICKSTART.md`
Quick start guide with:
- 3-step setup process
- Common commands
- Quick troubleshooting
- Essential information only

## Use Cases

### IoT Sensor Data Collection
```python
# In handle_message():
def handle_message(message):
    # Receive configuration or commands
    if message == "READ_SENSOR":
        # Read sensor and send back
        from machine import ADC
        sensor = ADC(Pin(34))
        value = sensor.read()
        ws.write(json.dumps({"sensor": value}))
```

### Remote Device Control
```python
# In handle_message():
def handle_message(message):
    cmd = json.loads(message)
    if cmd["device"] == "relay":
        relay = Pin(25, Pin.OUT)
        relay.value(cmd["state"])
```

### Real-time Monitoring
```python
# Receive alerts and status updates
def handle_message(message):
    data = json.loads(message)
    if data["type"] == "alert":
        # Flash LED, sound buzzer, etc.
        pass
```

### Home Automation
```python
# Control smart home devices
def handle_message(message):
    cmd = json.loads(message)
    if cmd["action"] == "lights_on":
        # Turn on lights
        pass
```

## WebSocket Protocol Implementation

The client implements the WebSocket protocol (RFC 6455):

1. **Connection Phase**
   - TCP socket connection to server
   - HTTP Upgrade request with WebSocket headers
   - Server responds with 101 Switching Protocols
   
2. **Communication Phase**
   - Messages are framed according to WebSocket spec
   - Supports text and binary frames
   - Handles control frames (ping, pong, close)
   
3. **Disconnection Phase**
   - Graceful close with close frame
   - Automatic reconnection on unexpected disconnect

## Customization Guide

### 1. Customize Message Handling

Edit the `handle_message()` function in `main.py`:

```python
def handle_message(message):
    # Your custom logic here
    print(f"Received: {message}")
    
    # Parse JSON
    import json
    data = json.loads(message)
    
    # Control hardware
    if data.get("led") == "on":
        from machine import Pin
        Pin(2, Pin.OUT).on()
```

### 2. Add Sensors

```python
from machine import Pin, ADC

# Read temperature sensor
temp_sensor = ADC(Pin(34))
temperature = temp_sensor.read()

# Send to server
ws.write(json.dumps({"temperature": temperature}))
```

### 3. Add Bi-directional Communication

```python
# Send periodic status updates
import time

last_send = time.time()
while True:
    # Receive messages
    data = ws.read()
    handle_message(data)
    
    # Send status every 10 seconds
    if time.time() - last_send > 10:
        status = {"uptime": time.time(), "heap": gc.mem_free()}
        ws.write(json.dumps(status))
        last_send = time.time()
```

## Performance Considerations

- **Memory**: ESP32 has limited RAM (typically 320KB)
- **Message Size**: Keep messages under a few KB
- **Frequency**: Don't send/receive too rapidly
- **Garbage Collection**: Call `gc.collect()` periodically

## Security Best Practices

1. **Use WSS (Secure WebSocket)** in production
2. **Don't hardcode credentials** - use secure storage
3. **Validate incoming messages** - check format and content
4. **Implement authentication** - verify server identity
5. **Use strong WiFi encryption** - WPA2/WPA3

## Deployment Checklist

- [ ] Test with local WebSocket server first
- [ ] Verify all configuration values
- [ ] Test reconnection behavior
- [ ] Monitor memory usage
- [ ] Implement proper error handling
- [ ] Add logging/debugging as needed
- [ ] Test on target hardware
- [ ] Use secure connection (wss://) in production
- [ ] Implement authentication if needed
- [ ] Document your customizations

## Troubleshooting Common Issues

### Connection Fails Immediately
- Check WiFi credentials
- Verify server URL and port
- Ensure server is running
- Check firewall rules

### Memory Errors
- Reduce message size
- Call `gc.collect()` more frequently
- Simplify message processing

### Connection Drops Frequently
- Check WiFi signal strength
- Verify server stability
- Adjust RECONNECT_DELAY
- Check for interference

### Handshake Fails
- Verify WebSocket path
- Check server WebSocket support
- Ensure proper HTTP headers

## Further Reading

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Quick Reference](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [ESP-IDF Documentation](https://docs.espressif.com/projects/esp-idf/)

## Support and Contribution

For issues, questions, or contributions:
1. Check existing documentation
2. Review examples in this directory
3. Test with the provided test server
4. Consult MicroPython forums and community

## License

This code follows the MicroPython project's MIT License.
