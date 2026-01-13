# This file is executed on every boot (including wake-boot from deepsleep)
import gc

# Import the WebSocket client main function
# Note: websocket_client and ws_config are frozen into the firmware
try:
    from websocket_client import main
    # Uncomment the line below to auto-start the WebSocket client on boot
    # main()
except ImportError as e:
    print(f"Error importing websocket_client: {e}")
    print("Make sure the firmware includes the frozen websocket_client module")

gc.collect()
