# This file is executed on every boot (including wake-boot from deepsleep)
import gc

# Import the WebSocket client main function
try:
    from main import main
    # Uncomment the line below to auto-start the WebSocket client on boot
    # main()
except ImportError as e:
    print(f"Error importing main: {e}")
    print("Make sure main.py and config.py are present on the device")

gc.collect()
