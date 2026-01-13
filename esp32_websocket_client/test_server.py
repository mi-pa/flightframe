"""
Example WebSocket Test Server
Run this on your computer to test the ESP32 WebSocket client.

Requirements:
    pip install websockets

Usage:
    python test_server.py
"""

import asyncio
import websockets
import json
from datetime import datetime


async def handle_client(websocket, path):
    """Handle WebSocket client connection."""
    client_address = websocket.remote_address
    print(f"[{datetime.now()}] Client connected from {client_address}")
    
    try:
        # Send welcome message
        welcome = json.dumps({
            "type": "welcome",
            "message": "Connected to test WebSocket server",
            "timestamp": datetime.now().isoformat()
        })
        await websocket.send(welcome)
        
        # Send periodic messages
        message_count = 0
        
        async def send_periodic_messages():
            nonlocal message_count
            while True:
                await asyncio.sleep(5)
                message_count += 1
                data = json.dumps({
                    "type": "periodic",
                    "message": f"Periodic message #{message_count}",
                    "timestamp": datetime.now().isoformat()
                })
                await websocket.send(data)
                print(f"[{datetime.now()}] Sent periodic message #{message_count} to {client_address}")
        
        # Start periodic message task
        periodic_task = asyncio.create_task(send_periodic_messages())
        
        # Listen for messages from client
        async for message in websocket:
            print(f"[{datetime.now()}] Received from {client_address}: {message}")
            
            # Echo the message back
            response = json.dumps({
                "type": "echo",
                "original": message,
                "timestamp": datetime.now().isoformat()
            })
            await websocket.send(response)
            print(f"[{datetime.now()}] Sent echo response to {client_address}")
            
    except websockets.exceptions.ConnectionClosed:
        print(f"[{datetime.now()}] Client {client_address} disconnected")
    except Exception as e:
        print(f"[{datetime.now()}] Error with client {client_address}: {e}")
    finally:
        if 'periodic_task' in locals():
            periodic_task.cancel()


async def main():
    """Start the WebSocket server."""
    host = "0.0.0.0"
    port = 8080
    
    print("=" * 60)
    print("WebSocket Test Server")
    print("=" * 60)
    print(f"Starting server on ws://{host}:{port}")
    print("Waiting for ESP32 clients to connect...")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    async with websockets.serve(handle_client, host, port):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
