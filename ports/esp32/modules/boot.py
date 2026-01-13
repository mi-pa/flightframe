# This file is executed on every boot (including wake-boot from deepsleep)
import gc
import network
import time
import machine

def check_wifi_configured():
    """Check if WiFi credentials are configured"""
    try:
        import ws_config
        if ws_config.WIFI_SSID == "YOUR_WIFI_SSID" or not ws_config.WIFI_SSID:
            return False
        return True
    except: 
        return False

def connect_wifi():
    """Connect to WiFi using saved credentials"""
    import ws_config
    
    sta = network.WLAN(network. STA_IF)
    sta.active(True)
    
    if not sta.isconnected():
        print(f'Connecting to {ws_config. WIFI_SSID}.. .')
        sta.connect(ws_config.WIFI_SSID, ws_config.WIFI_PASSWORD)
        
        timeout = 20
        while not sta.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if sta.isconnected():
            print('Connected!  Network config:', sta.ifconfig())
            return True
        else:
            print('Failed to connect to WiFi')
            return False
    return True

def main():
    """Main boot sequence"""
    # Check if we need to enter provisioning mode
    # Hold a button on boot to force provisioning (optional)
    # For example, GPIO 0 (BOOT button on many ESP32 boards)
    # button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
    # force_provisioning = button.value() == 0
    
    force_provisioning = False  # Set to True to force provisioning mode
    
    if not check_wifi_configured() or force_provisioning:
        print("WiFi not configured. Starting provisioning mode...")
        from wifi_provisioning import start_provisioning
        start_provisioning()
    else:
        if connect_wifi():
            print("Starting main application...")
            # Import and start your main application here
            # import main
            # main.start()
        else:
            print("Failed to connect.  Starting provisioning mode...")
            from wifi_provisioning import start_provisioning
            start_provisioning()

# Run main sequence
main()



# Import the WebSocket client main function
# Note: websocket_client and ws_config are frozen into the firmware
try:
    from websocket_client import main
    # Uncomment the line below to auto-start the WebSocket client on boot
    main()
except ImportError as e:
    print(f"Error importing websocket_client: {e}")
    print("Make sure the firmware includes the frozen websocket_client module")

gc.collect()
