import socket
import json
import threading
import time
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Configuration
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 65432      # Port to listen on
DISCONNECT_THRESHOLD = 5  # Time in seconds to mark a server as disconnected

# Global list to store server status
server_status_list = {}

console = Console()

def display_server_status():
    """
    Continuously updates the terminal with the current status of all connected servers.
    """
    with Live(console=console, refresh_per_second=1) as live:
        while True:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("IP Address")
            table.add_column("Port")
            table.add_column("CPU Usage (%)")
            table.add_column("Memory Used (GB)")
            table.add_column("Memory Available (GB)")
            table.add_column("Disk Used (GB)")
            table.add_column("Disk Free (GB)")
            table.add_column("Network Sent (MB)")
            table.add_column("Network Received (MB)")
            table.add_column("Timestamp")

            current_time = time.time()

            # Remove old entries (i.e., disconnected servers)
            for key in list(server_status_list.keys()):
                last_update_time = server_status_list[key]['timestamp_received']
                last_update_time = time.mktime(time.strptime(last_update_time, '%Y-%m-%d %H:%M:%S'))
                
                if current_time - last_update_time > DISCONNECT_THRESHOLD:
                    row_color = "red"
                else:
                    row_color = "green"

                table.add_row(
                    server_status_list[key]['address'],
                    str(server_status_list[key]['port']),
                    f"{server_status_list[key]['status_info']['cpu_usage']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['memory']['used']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['memory']['available']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['disk']['used']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['disk']['free']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['network']['sent']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['network']['received']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    server_status_list[key]['timestamp_received'],
                    style=row_color
                )

            live.update(table)

def handle_client_connection(conn, addr):
    """
    Handles communication with a connected client, updates the server status list.
    """
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(4096)  # Adjust buffer size if needed
            if not data:
                break
            try:
                status_info = json.loads(data.decode('utf-8'))
                status = {
                    'address': addr[0],
                    'port': addr[1],
                    'status_info': status_info,
                    'timestamp_received': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                # Update or append status info
                server_status_list[(addr[0], addr[1])] = status

            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON data: {e}")

def start_central_server():
    """
    Starts the central server, listening for incoming client connections.
    """
    # Start a separate thread to display server status
    threading.Thread(target=display_server_status, daemon=True).start()

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
