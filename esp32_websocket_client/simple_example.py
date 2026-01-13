"""
Simple WebSocket Client Example
A minimal example to get started with ESP32 WebSocket client.
"""

import network
import socket
import time

try:
    import websocket
    import ubinascii
except ImportError:
    print("Error: Required modules not available")
    print("Ensure you're running on MicroPython with websocket support")
    raise

# Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
SERVER_HOST = "example.com"
SERVER_PORT = 80
WS_PATH = "/ws"


def connect_wifi():
    """Connect to WiFi."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to WiFi: {WIFI_SSID}")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        while not wlan.isconnected():
            time.sleep(1)
    
    print("Connected!")
    print("IP:", wlan.ifconfig()[0])
    return wlan


def websocket_connect():
    """Connect to WebSocket server."""
    # Create socket
    addr = socket.getaddrinfo(SERVER_HOST, SERVER_PORT)[0][-1]
    sock = socket.socket()
    sock.connect(addr)
    print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")
    
    # WebSocket handshake
    key = ubinascii.b2a_base64(bytes(range(16))).strip()
    request = (
        f"GET {WS_PATH} HTTP/1.1\r\n"
        f"Host: {SERVER_HOST}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key.decode()}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    sock.send(request.encode())
    
    # Wait for handshake response
    response = b""
    while b"\r\n\r\n" not in response:
        response += sock.recv(1024)
    
    print("WebSocket handshake complete!")
    
    # Create WebSocket object
    ws = websocket.websocket(sock)
    return ws


def main():
    """Main function."""
    print("=" * 40)
    print("Simple ESP32 WebSocket Client")
    print("=" * 40)
    
    # Connect to WiFi
    connect_wifi()
    
    # Connect to WebSocket
    ws = websocket_connect()
    
    # Listen for messages
    print("Listening for messages...")
    while True:
        try:
            data = ws.read()
            if data:
                message = data.decode('utf-8') if isinstance(data, bytes) else data
                print(f"Received: {message}")
        except KeyboardInterrupt:
            print("\nStopping...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    
    ws.close()
    print("Done!")


if __name__ == "__main__":
    main()
