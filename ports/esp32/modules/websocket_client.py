"""
ESP32 WebSocket Client for MicroPython
Connects to a WebSocket server and listens for messages.
"""

import network
import socket
import time
import ubinascii
from ws_config import (
    WIFI_SSID,
    WIFI_PASSWORD,
    WS_SERVER,
    WS_PATH,
    RECONNECT_DELAY,
    MAX_RECONNECT_ATTEMPTS
)

try:
    import websocket
except ImportError:
    print("Error: websocket module not available")
    print("This module should be built into MicroPython for ESP32")
    raise


def connect_wifi():
    """Connect to WiFi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print("Already connected to WiFi")
        print("Network config:", wlan.ifconfig())
        return wlan
    
    print(f"Connecting to WiFi: {WIFI_SSID}")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Wait for connection
    max_wait = 20
    while max_wait > 0:
        if wlan.isconnected():
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
    
    if wlan.isconnected():
        print("Connected to WiFi")
        print("Network config:", wlan.ifconfig())
        return wlan
    else:
        print("Failed to connect to WiFi")
        return None


def parse_ws_url(url):
    """Parse WebSocket URL to extract host, port, and path."""
    # Remove ws:// or wss:// prefix
    if url.startswith("ws://"):
        secure = False
        url = url[5:]
    elif url.startswith("wss://"):
        secure = True
        url = url[6:]
    else:
        secure = False
    
    # Split host/port and path
    if "/" in url:
        host_port, path = url.split("/", 1)
        path = "/" + path
    else:
        host_port = url
        path = "/"
    
    # Split host and port if present
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 443 if secure else 80
    
    return host, port, path, secure


def websocket_handshake(sock, host, path):
    """Perform WebSocket handshake."""
    # Generate a key for the handshake
    # Note: RFC 6455 recommends random bytes, but this works for most use cases
    # For production security, consider using os.urandom(16) if available
    key = ubinascii.b2a_base64(bytes([i & 0xff for i in range(16)])).strip()
    
    # Build the HTTP upgrade request
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key.decode()}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    
    print("Sending WebSocket handshake...")
    sock.send(request.encode())
    
    # Read the response
    response = b""
    while b"\r\n\r\n" not in response:
        chunk = sock.recv(1024)
        if not chunk:
            raise Exception("Connection closed during handshake")
        response += chunk
    
    # Check if upgrade was successful
    if b"HTTP/1.1 101" not in response:
        raise Exception(f"WebSocket handshake failed: {response[:100]}")
    
    print("WebSocket handshake successful")
    return True


def connect_websocket(host, port, path):
    """Connect to WebSocket server."""
    print(f"Connecting to {host}:{port}{path}")
    
    # Create socket connection
    addr_info = socket.getaddrinfo(host, port)
    addr = addr_info[0][-1]
    
    sock = socket.socket()
    sock.connect(addr)
    print(f"TCP connection established to {addr}")
    
    # Perform WebSocket handshake
    websocket_handshake(sock, host, path)
    
    # Wrap socket with websocket protocol
    ws = websocket.websocket(sock)
    
    return ws


def handle_message(message):
    """Handle received WebSocket message."""
    print(f"Received message: {message}")
    # Add your message handling logic here
    # For example:
    # - Parse JSON data
    # - Control GPIO pins
    # - Store data to file
    # - Send response back to server


def websocket_listen():
    """Main WebSocket listening loop."""
    ws = None
    reconnect_count = 0
    
    while True:
        try:
            # Parse WebSocket URL
            host, port, path, secure = parse_ws_url(WS_SERVER)
            # Use WS_PATH from config if URL doesn't contain path
            if path == "/":
                path = WS_PATH
            
            # Check if we have WiFi connection
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("WiFi disconnected, reconnecting...")
                wlan = connect_wifi()
                if not wlan:
                    print(f"Waiting {RECONNECT_DELAY} seconds before retry...")
                    time.sleep(RECONNECT_DELAY)
                    continue
            
            # Connect to WebSocket server
            ws = connect_websocket(host, port, path)
            print("Connected to WebSocket server")
            print("Listening for messages...")
            
            # Reset reconnect counter on successful connection
            reconnect_count = 0
            
            # Listen for messages
            while True:
                try:
                    # Read message from WebSocket
                    data = ws.read()
                    
                    if data:
                        # Convert bytes to string if needed
                        if isinstance(data, bytes):
                            message = data.decode('utf-8')
                        else:
                            message = data
                        
                        handle_message(message)
                    else:
                        # Connection closed
                        print("Connection closed by server")
                        break
                        
                except OSError as e:
                    print(f"Error reading from WebSocket: {e}")
                    break
            
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            if ws:
                ws.close()
            break
            
        except Exception as e:
            print(f"Error: {e}")
            
        finally:
            # Clean up connection
            if ws:
                try:
                    ws.close()
                except:
                    pass
                ws = None
        
        # Handle reconnection
        reconnect_count += 1
        if MAX_RECONNECT_ATTEMPTS > 0 and reconnect_count >= MAX_RECONNECT_ATTEMPTS:
            print(f"Max reconnection attempts ({MAX_RECONNECT_ATTEMPTS}) reached")
            break
        
        print(f"Reconnecting in {RECONNECT_DELAY} seconds... (attempt {reconnect_count})")
        time.sleep(RECONNECT_DELAY)


def main():
    """Main entry point."""
    print("=" * 50)
    print("ESP32 WebSocket Client")
    print("=" * 50)
    
    # Connect to WiFi
    wlan = connect_wifi()
    if not wlan:
        print("Failed to connect to WiFi. Exiting.")
        return
    
    # Start WebSocket listener
    try:
        websocket_listen()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        wlan = network.WLAN(network.STA_IF)
        wlan.disconnect()
        wlan.active(False)
        print("Disconnected from WiFi")


# Auto-start when imported as main
if __name__ == "__main__":
    main()
