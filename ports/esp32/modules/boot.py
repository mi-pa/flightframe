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
    
    sta = network.WLAN(network.STA_IF)
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
    force_provisioning = False
    
    if not check_wifi_configured() or force_provisioning:
        print("WiFi not configured. Starting provisioning mode...")
        from wifi_provisioning import start_provisioning
        start_provisioning()
    else:
        if connect_wifi():
            print("Starting main application...")
            # ✅ WebSocket-Client NUR starten wenn WiFi verbunden ist
            try:
                from websocket_client import main as ws_main
                ws_main()
            except ImportError as e:
                print(f"Error importing websocket_client: {e}")
        else:
            print("Failed to connect.  Starting provisioning mode...")
            from wifi_provisioning import start_provisioning
            start_provisioning()

    gc.collect()


