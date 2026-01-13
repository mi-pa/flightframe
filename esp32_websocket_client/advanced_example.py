"""
Advanced WebSocket Client Example
This example demonstrates:
- Sending messages to the server
- Bi-directional communication
- JSON message handling
- GPIO control via WebSocket commands
"""

import network
import socket
import time
import json
import ubinascii
from ws_config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    WS_SERVER,
    WS_PATH
)

try:
    import websocket
    from machine import Pin
except ImportError as e:
    print(f"Import error: {e}")
    raise


def connect_wifi():
    """Connect to WiFi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to WiFi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        max_wait = 20
        while max_wait > 0 and not wlan.isconnected():
            max_wait -= 1
            print("Waiting for connection...")
            time.sleep(1)
    
    if wlan.isconnected():
        print("Connected to WiFi")
        print("Network config:", wlan.ifconfig())
        return wlan
    return None


def websocket_handshake(sock, host, path):
    """Perform WebSocket handshake."""
    key = ubinascii.b2a_base64(bytes([i & 0xff for i in range(16)])).strip()
    
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key.decode()}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    
    sock.send(request.encode())
    
    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(1024)
    
    if b"HTTP/1.1 101" not in response:
        raise Exception("WebSocket handshake failed")
    
    return True


def advanced_example():
    """Advanced WebSocket client with bi-directional communication."""
    print("=" * 50)
    print("Advanced ESP32 WebSocket Client Example")
    print("=" * 50)
    
    # Initialize LED (built-in LED is usually on Pin 2)
    led = Pin(2, Pin.OUT)
    led_state = False
    
    # Connect to WiFi
    wlan = connect_wifi()
    if not wlan:
        print("Failed to connect to WiFi")
        return
    
    # Parse server URL
    ws_url = WS_SERVER
    if ws_url.startswith("ws://"):
        host = ws_url[5:].split(':')[0].split('/')[0]
        if ':' in ws_url[5:]:
            port = int(ws_url[5:].split(':')[1].split('/')[0])
        else:
            port = 80
    else:
        host = ws_url.split(':')[0].split('/')[0]
        port = 80
    
    # Connect to WebSocket server
    print(f"Connecting to {host}:{port}{WS_PATH}")
    addr_info = socket.getaddrinfo(host, port)
    addr = addr_info[0][-1]
    
    sock = socket.socket()
    sock.connect(addr)
    print("TCP connection established")
    
    websocket_handshake(sock, host, WS_PATH)
    print("WebSocket handshake successful")
    
    ws = websocket.websocket(sock)
    
    # Send initial status message
    status_msg = json.dumps({
        "type": "status",
        "device": "ESP32",
        "led_state": led_state,
        "ip": wlan.ifconfig()[0]
    })
    ws.write(status_msg)
    print(f"Sent: {status_msg}")
    
    # Main communication loop
    print("Listening for commands...")
    try:
        while True:
            # Read message from server
            data = ws.read()
            
            if data:
                message = data.decode('utf-8') if isinstance(data, bytes) else data
                print(f"Received: {message}")
                
                try:
                    # Parse JSON command
                    cmd = json.loads(message)
                    
                    if cmd.get("type") == "led_control":
                        # Control LED based on command
                        action = cmd.get("action")
                        if action == "on":
                            led.on()
                            led_state = True
                            print("LED turned ON")
                        elif action == "off":
                            led.off()
                            led_state = False
                            print("LED turned OFF")
                        elif action == "toggle":
                            led_state = not led_state
                            led.value(led_state)
                            print(f"LED toggled to {'ON' if led_state else 'OFF'}")
                        
                        # Send response
                        response = json.dumps({
                            "type": "led_status",
                            "state": led_state
                        })
                        ws.write(response)
                        print(f"Sent: {response}")
                    
                    elif cmd.get("type") == "ping":
                        # Respond to ping
                        response = json.dumps({
                            "type": "pong",
                            "timestamp": time.time()
                        })
                        ws.write(response)
                        print(f"Sent: {response}")
                    
                except json.JSONDecodeError:
                    print("Invalid JSON received")
                except Exception as e:
                    print(f"Error processing command: {e}")
            
            time.sleep(0.1)  # Small delay to prevent CPU hogging
            
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ws.close()
        wlan.disconnect()
        print("Disconnected")


if __name__ == "__main__":
    advanced_example()
