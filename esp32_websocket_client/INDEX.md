# ESP32 WebSocket Client - File Index

## 📚 Documentation (Read These First)

### 🚀 [QUICKSTART.md](QUICKSTART.md)
**Start here!** 3-step quick setup guide
- Flash MicroPython
- Configure and upload
- Run the client

### 📖 [README.md](README.md)
Complete documentation with:
- Features and requirements
- Detailed installation
- Configuration options
- Usage instructions
- Troubleshooting guide

### 🏗️ [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
Architecture and design:
- How it works
- Architecture diagram
- Use cases and examples
- Customization guide
- Security best practices

---

## 💻 Core Application Files

### Production: Frozen Modules (in ports/esp32/modules/)

#### ⚙️ [ports/esp32/modules/ws_config.py](../ports/esp32/modules/ws_config.py)
**Edit this before building firmware!** Configuration file:
```python
WIFI_SSID = "YOUR_WIFI_SSID"       # ← Change these
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
WS_SERVER = "ws://example.com"
```

#### 🎯 [ports/esp32/modules/websocket_client.py](../ports/esp32/modules/websocket_client.py)
Main WebSocket client (frozen into firmware):
- WiFi connection
- WebSocket handshake
- Message receiving loop
- Auto-reconnection
- **Usage**: `import websocket_client; websocket_client.main()`

### Development: Example Files (in esp32_websocket_client/)

### ⚙️ [config.py](config.py)
Standalone configuration file for manual testing:
```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
WS_SERVER = "ws://example.com"
```

### 🎯 [main.py](main.py)
Standalone version for manual upload:
- Same functionality as websocket_client.py
- Use when not building custom firmware
- **Start point**: Run `import main; main.main()`

### 🔄 [boot.py](boot.py)
Boot script example:
- Shows how to auto-start on boot
- Works with frozen modules
- Copy to ESP32 filesystem if needed

---

## 📝 Example Files

### 1️⃣ [simple_example.py](simple_example.py)
**Beginner-friendly** minimal example:
- Basic WiFi connection
- Simple WebSocket setup
- Message receiving
- ~80 lines of code
- **Best for**: Learning the basics

### 2️⃣ [advanced_example.py](advanced_example.py)
**Advanced features** example:
- Bi-directional communication
- JSON message handling
- LED control via WebSocket
- Status reporting
- **Best for**: Production projects

### 🖥️ [test_server.py](test_server.py)
Python WebSocket test server:
- Run on your computer
- Test without real server
- Sends periodic messages
- Echo functionality
- **Usage**: `python test_server.py`

---

## 🗂️ Other Files

### [.gitignore](.gitignore)
Git ignore patterns:
- Local config files
- Python cache
- IDE files

---

## 📋 Quick Decision Tree

### "I want to..."

#### 🎓 **Learn how WebSocket works**
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run [simple_example.py](simple_example.py)
3. Experiment with [test_server.py](test_server.py)

#### 🚀 **Get started quickly**
1. [QUICKSTART.md](QUICKSTART.md) ← Follow this
2. Edit [config.py](config.py)
3. Run [main.py](main.py)

#### 🔧 **Build a real application**
1. Read [README.md](README.md)
2. Study [advanced_example.py](advanced_example.py)
3. Customize [main.py](main.py)
4. Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)

#### 🐛 **Troubleshoot issues**
1. Check [README.md](README.md) → Troubleshooting section
2. Review [QUICKSTART.md](QUICKSTART.md) → Common Issues
3. Test with [test_server.py](test_server.py)

#### 📚 **Understand architecture**
1. Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
2. Look at code in [main.py](main.py)
3. Compare [simple_example.py](simple_example.py) vs [advanced_example.py](advanced_example.py)

---

## 🎯 Recommended Learning Path

### Level 1: Beginner
```
QUICKSTART.md → simple_example.py → test_server.py
```

### Level 2: Intermediate
```
README.md → main.py + config.py → Run on ESP32
```

### Level 3: Advanced
```
PROJECT_OVERVIEW.md → advanced_example.py → Customize for your needs
```

---

## 📊 File Sizes & Complexity

| File | Lines | Complexity | Purpose |
|------|-------|------------|---------|
| `simple_example.py` | ~80 | ⭐ Low | Learning |
| `main.py` | ~250 | ⭐⭐ Medium | Production |
| `advanced_example.py` | ~180 | ⭐⭐⭐ High | Features |
| `config.py` | ~10 | ⭐ Low | Settings |
| `boot.py` | ~15 | ⭐ Low | Auto-start |
| `test_server.py` | ~90 | ⭐⭐ Medium | Testing |

---

## ✅ Setup Checklist

- [ ] Read QUICKSTART.md
- [ ] Flash MicroPython to ESP32
- [ ] Edit config.py with WiFi credentials
- [ ] Upload files to ESP32
- [ ] Test with test_server.py (optional)
- [ ] Run main.py
- [ ] Customize handle_message() for your needs

---

## 🔗 External Resources

- [MicroPython Docs](https://docs.micropython.org/)
- [ESP32 Quick Reference](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [WebSocket RFC](https://tools.ietf.org/html/rfc6455)

---

## 💡 Tips

- **Start simple**: Use simple_example.py first
- **Test locally**: Run test_server.py before connecting to real server
- **Read errors**: MicroPython gives helpful error messages
- **Check basics**: WiFi credentials, server URL, firewall
- **Use REPL**: Test code interactively in MicroPython REPL

---

## 🆘 Getting Help

1. Check documentation in this directory
2. Review the examples
3. Test with the test server
4. Search MicroPython forums
5. Check ESP32/MicroPython GitHub issues

---

**Happy coding! 🎉**
