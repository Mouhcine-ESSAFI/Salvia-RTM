import socket
import json
import threading
import time
import os
import signal
import shutil
from rich.console import Console
from rich.table import Table
from rich.live import Live

# Configuration
HOST = '0.0.0.0'
PORT = 65432
DISCONNECT_THRESHOLD = 5  # Seconds to mark a server as disconnected
SERVER_LIST_FILE = '/home/salvia/Salvia-RTM/server_list.json'

# Global list to store server status
server_status_list = {}
shutdown_event = threading.Event()  # Event to signal shutdown
save_lock = threading.Lock()  # Lock for safe file writing
console = Console()

def convert_keys_to_strings(d):
    new_dict = {}
    for key, value in d.items():
        new_key = str(key)
        new_dict[new_key] = value
    return new_dict

def convert_keys_to_tuples(d):
    new_dict = {}
    for key, value in d.items():
        new_key = eval(key)
        new_dict[new_key] = value
    return new_dict

def load_server_list(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return convert_keys_to_tuples(data)
        except json.JSONDecodeError:
            return {}
    return {}

def save_server_list(file_path):
    try:
        data = convert_keys_to_strings(server_status_list)

        # Create a backup only if the main file exists
        if os.path.exists(file_path):
            backup_path = file_path + ".bak"
            shutil.copy(file_path, backup_path)  # Create backup

        # Save the server list
        with save_lock:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)
    except (IOError, json.JSONDecodeError):
        pass  # Silently ignore any save-related errors

def clear_terminal():
    os.system('clear')

def display_server_status():
    """
    Continuously updates the terminal with the current status of all connected servers.
    """
    clear_terminal()  # Clear the terminal once before displaying the table

    with Live(console=console, refresh_per_second=1) as live:
        while not shutdown_event.is_set():  # Continue displaying until shutdown_event is set
            table = Table(show_header=True, header_style="bold white")
            table.add_column("Hostname", style="white")
            table.add_column("IP Address", style="white")
            table.add_column("Port", style="white")
            table.add_column("CPU Usage (%)", style="white")
            table.add_column("Memory Used (GB)", style="bold white")
            table.add_column("Memory Available (GB)", style="white")
            table.add_column("Disk Used (GB)", style="white")
            table.add_column("Disk Free (GB)", style="white")
            table.add_column("Network Sent (MB)", style="white")
            table.add_column("Network Received (MB)", style="white")
            table.add_column("Timestamp", style="white")

            current_time = time.time()

            for key in list(server_status_list.keys()):
                last_update_time = server_status_list[key]['timestamp_received']
                last_update_time = time.mktime(time.strptime(last_update_time, '%Y-%m-%d %H:%M:%S'))

                # Check if server has been disconnected (based on last update time)
                if current_time - last_update_time > DISCONNECT_THRESHOLD:
                    row_color = "bright_red"
                else:
                    row_color = "bright_green"

                # Add rows to the table with the hostname and server information
                table.add_row(
                    server_status_list[key]['status_info']['system_info']['hostname'],  # Hostname
                    server_status_list[key]['address'],  # IP Address
                    str(server_status_list[key]['port']),  # Port
                    f"{server_status_list[key]['status_info']['cpu_usage']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['memory']['used']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['memory']['available']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['disk']['used']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['disk']['free']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['network']['sent']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    f"{server_status_list[key]['status_info']['network']['received']:.2f}" if server_status_list[key]['status_info'] else "N/A",
                    server_status_list[key]['timestamp_received'],
                    style=row_color  # Set row color based on connection status
                )

            live.update(table)


def handle_client_connection(conn, addr):
    with conn:
        while True:
            data = conn.recv(4096)
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

                existing_key = None
                for key in server_status_list.keys():
                    if server_status_list[key]['address'] == addr[0]:
                        existing_key = key
                        break

                if existing_key:
                    server_status_list[existing_key] = status
                else:
                    server_status_list[(addr[0], addr[1])] = status

                save_server_list(SERVER_LIST_FILE)
            except json.JSONDecodeError:
                pass  # Silently ignore JSON decode errors

def periodic_save(interval=60):
    while not shutdown_event.is_set():
        time.sleep(interval)
        save_server_list(SERVER_LIST_FILE)

def shutdown(signal_received, frame):
    clear_terminal()
    shutdown_event.set()
    save_server_list(SERVER_LIST_FILE)
    exit(0)

def start_central_server():
    global server_status_list
    server_status_list = load_server_list(SERVER_LIST_FILE)
    signal.signal(signal.SIGINT, shutdown)
    threading.Thread(target=display_server_status, daemon=True).start()
    threading.Thread(target=periodic_save, daemon=True).start()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()

            while True:
                conn, addr = s.accept()
                client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
                client_thread.start()

    except KeyboardInterrupt:
        pass  # Silently ignore keyboard interrupt for graceful shutdown

if __name__ == "__main__":
    start_central_server()
