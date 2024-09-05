import socket
import psutil
import json
import time
import platform

# Configuration
CENTRAL_SERVER_HOST = '192.168.1.19'  # Replace with the central server's IP address
CENTRAL_SERVER_PORT = 65432                 # Port on which the central server is listening

def gather_system_info():
    # Calculate uptime in days, hours, minutes, and seconds
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_days = int(uptime_seconds // (24 * 3600))
    uptime_hours = int((uptime_seconds % (24 * 3600)) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime_seconds = int(uptime_seconds % 60)

    return {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory': {
            'used': psutil.virtual_memory().used / (1024 ** 3),  # Convert bytes to GB
            'available': psutil.virtual_memory().available / (1024 ** 3)  # Convert bytes to GB
        },
        'disk': {
            'used': psutil.disk_usage('/').used / (1024 ** 3),  # Convert bytes to GB
            'free': psutil.disk_usage('/').free / (1024 ** 3)   # Convert bytes to GB
        },
        'network': {
            'sent': psutil.net_io_counters().bytes_sent / (1024 ** 2),  # Convert bytes to MB
            'received': psutil.net_io_counters().bytes_recv / (1024 ** 2)  # Convert bytes to MB
        },
        'system_info': {
            'hostname': platform.node(),
            'uptime': {
                'days': uptime_days,
                'hours': uptime_hours,
                'minutes': uptime_minutes,
                'seconds': uptime_seconds
            }
        }
    }

def send_status_update():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((CENTRAL_SERVER_HOST, CENTRAL_SERVER_PORT))
                print(f"Connected to server at {CENTRAL_SERVER_HOST}:{CENTRAL_SERVER_PORT}")

                while True:
                    # Gather and send system information
                    system_info = gather_system_info()
                    s.sendall(json.dumps(system_info).encode('utf-8'))
                    # print(f"Sent data: {system_info}")
                    # time.sleep(10)  # Adjust frequency as needed

        except (ConnectionError, socket.error) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    send_status_update()
