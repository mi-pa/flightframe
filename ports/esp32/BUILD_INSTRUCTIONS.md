# Building ESP32 Firmware with Custom WebSocket Client

This guide explains how to build a custom ESP32 firmware .bin file with the WebSocket client frozen into the firmware.

## Prerequisites

1. **ESP-IDF toolchain** - Install the Espressif IoT Development Framework
2. **Build tools** - GCC, make, git
3. **Python 3** - For build scripts

## Setup

### 1. Install ESP-IDF

```bash
# Clone ESP-IDF (MicroPython uses a specific version)
git clone -b v5.0.4 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32
. ./export.sh
```

### 2. Install MicroPython build dependencies

```bash
pip install pyelftools
```

## Building the Firmware

### 1. Navigate to ESP32 port directory

```bash
cd ports/esp32
```

### 2. Initialize submodules (if not already done)

```bash
make submodules
```

### 3. Build the firmware

For a basic ESP32:
```bash
make BOARD=ESP32_GENERIC
```

For ESP32 with SPIRAM:
```bash
make BOARD=ESP32_GENERIC_SPIRAM
```

For other boards (e.g., ESP32-S3):
```bash
make BOARD=ESP32_GENERIC_S3
```

### 4. Locate the firmware

After successful build, the firmware will be at:
```
build-ESP32_GENERIC/firmware.bin
```

Or for other boards:
```
build-<BOARD_NAME>/firmware.bin
```

## Flashing the Firmware

### Using make deploy

```bash
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 deploy
```

Replace `/dev/ttyUSB0` with your device port (e.g., `COM3` on Windows).

### Using esptool.py manually

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 build-ESP32_GENERIC/firmware.bin
```

## Frozen Modules

The following modules are frozen into the firmware and available on boot:

- **websocket_client** - Main WebSocket client implementation (formerly `main.py`)
- **ws_config** - WebSocket configuration module (formerly `config.py`)

These modules are compiled into the firmware and do not need to be uploaded separately.

## Configuration

Since `ws_config` is frozen into the firmware, you'll need to:

1. Edit `ports/esp32/modules/ws_config.py` before building
2. Set your WiFi credentials and WebSocket server settings
3. Rebuild the firmware with your custom configuration

Alternatively, you can override the configuration at runtime by creating a custom `ws_config.py` on the device filesystem, which will take precedence over the frozen module.

## Using the WebSocket Client

### From REPL

After flashing the firmware, connect to the REPL and run:

```python
>>> import websocket_client
>>> websocket_client.main()
```

### Auto-start on boot

Create a `boot.py` file on the device:

```python
import gc
from websocket_client import main

# Auto-start the WebSocket client
main()

gc.collect()
```

Upload this file using `mpremote` or `ampy`:

```bash
mpremote connect /dev/ttyUSB0 fs cp boot.py :
```

## Example Usage

### Basic connection

```python
from websocket_client import connect_wifi, websocket_listen

# Connect to WiFi
connect_wifi()

# Start listening for WebSocket messages
websocket_listen()
```

### Custom message handler

```python
from websocket_client import connect_wifi, connect_websocket, parse_ws_url
from ws_config import WS_SERVER, WS_PATH

def my_handler(message):
    print(f"Got message: {message}")
    # Your custom logic here

# Connect to WiFi
connect_wifi()

# Parse and connect to WebSocket
host, port, path, secure = parse_ws_url(WS_SERVER)
if path == "/":
    path = WS_PATH
ws = connect_websocket(host, port, path)

# Listen for messages with custom handler
while True:
    data = ws.read()
    if data:
        my_handler(data.decode('utf-8') if isinstance(data, bytes) else data)
```

## Troubleshooting

### Build errors

If you encounter build errors:

1. Make sure ESP-IDF is properly installed and sourced:
   ```bash
   . ~/esp-idf/export.sh
   ```

2. Verify submodules are initialized:
   ```bash
   make submodules
   ```

3. Clean and rebuild:
   ```bash
   make clean
   make BOARD=ESP32_GENERIC
   ```

### Module import errors

If you get "ImportError: no module named websocket_client":

1. Verify the firmware was built with the modules in `ports/esp32/modules/`
2. Check that `websocket_client.py` and `ws_config.py` are present in `ports/esp32/modules/`
3. Rebuild the firmware to include these modules

### WebSocket connection issues

1. Verify WiFi credentials in `ws_config.py`
2. Ensure WebSocket server is accessible from the ESP32
3. Check firewall settings
4. Test with a simple WebSocket echo server

## Advanced Configuration

### Custom board configuration

If you have a custom board, create a board definition in `boards/` and build with:

```bash
make BOARD=YOUR_CUSTOM_BOARD
```

### Enabling additional features

Edit `mpconfigboard.h` in your board directory to enable/disable features:

```c
#define MICROPY_PY_WEBSOCKET (1)  // Enable websocket support
```

### Optimizing firmware size

To reduce firmware size, you can disable unused modules by editing the board configuration.

## Additional Resources

- [MicroPython ESP32 Documentation](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [ESP-IDF Programming Guide](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [MicroPython Forum](https://forum.micropython.org/)

## Example Build Workflow

```bash
# 1. Clone and setup
git clone https://github.com/mi-pa/flightframe.git
cd flightframe
git submodule update --init --recursive

# 2. Install ESP-IDF
git clone -b v5.0.4 --recursive https://github.com/espressif/esp-idf.git ~/esp-idf
cd ~/esp-idf
./install.sh esp32
. ./export.sh

# 3. Configure WebSocket settings
cd /path/to/flightframe/ports/esp32
nano modules/ws_config.py  # Edit your settings

# 4. Build firmware
make submodules
make BOARD=ESP32_GENERIC

# 5. Flash to device
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 erase
make BOARD=ESP32_GENERIC PORT=/dev/ttyUSB0 deploy

# 6. Test
screen /dev/ttyUSB0 115200
# In REPL:
>>> import websocket_client
>>> websocket_client.main()
```

## Notes

- The frozen modules (`websocket_client` and `ws_config`) are compiled into the firmware and loaded from flash, saving RAM
- Any `.py` file in `ports/esp32/modules/` will be frozen into the firmware during build
- To update the frozen modules, you must rebuild and reflash the firmware
- Runtime Python files uploaded to the filesystem take precedence over frozen modules
