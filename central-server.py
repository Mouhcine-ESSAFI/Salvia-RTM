import socket
import json
import threading
import os
import time

# Configuration
HOST = '127.0.0.2'  # Listen on all network interfaces
PORT = 65432      # Port to listen on
STATUS_FILE = '/home/mouhcine/Desktop/RTM/client_info.json'  # Path to save the status data

def save_status_info(status_info):
    # Initialize data if file does not exist or is empty
    if os.path.exists(STATUS_FILE):
        if os.path.getsize(STATUS_FILE) > 0:
            with open(STATUS_FILE, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print("Error reading JSON file. Initializing new data.")
                    data = []  # Handle invalid JSON
        else:
            data = []  # File is empty
    else:
        data = []

    # Append new status info
    data.append(status_info)

    # Save updated data to JSON file
    with open(STATUS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Status info saved: {status_info}")

def handle_client_connection(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(4096)  # Adjust buffer size if needed
            if not data:
                break
            try:
                status_info = json.loads(data.decode('utf-8'))
                print(f"Status info from {addr}: {status_info}")

                # Save status info to JSON file
                save_status_info({
                    'address': addr[0],  # Only save IP address
                    'port': addr[1],     # Save port number
                    'status_info': status_info,
                    'timestamp_received': time.strftime('%Y-%m-%d %H:%M:%S')
                })
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON data: {e}")

def start_central_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Central server started. Listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_central_server()
