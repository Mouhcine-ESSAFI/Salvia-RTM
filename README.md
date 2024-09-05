Real-Time Server Monitoring
Monitor and visualize real-time system metrics from multiple client servers. This project includes a central server that collects data and displays it in a terminal-based table with dynamic updates and color-coded statuses.

🚀 Features
Real-Time Data: Live system metrics from client servers.
Dynamic Updates: Real-time terminal table updates using rich.
Color-Coded Status: Green for connected servers, red for disconnected ones.
Port Management: Handles server reconnects with varying ports.
🛠️ Requirements
Python 3.x
rich library (for terminal display)
📝 Installation
Clone the Repository

bash
Copier le code
git clone https://github.com/yourusername/your-repository.git
cd your-repository
Set Up a Virtual Environment

bash
Copier le code
python3 -m venv venv
source venv/bin/activate
Install Dependencies

bash
Copier le code
pip install rich
⚙️ Usage
Start the Central Server

bash
Copier le code
python central-server.py
Run the Client Server

Update CENTRAL_SERVER_HOST and CENTRAL_SERVER_PORT in client-server.py, then:

bash
Copier le code
python client-server.py
🔧 Configuration
HOST: IP address for the central server (default: 0.0.0.0).
PORT: Port for the central server (default: 65432).
DISCONNECT_THRESHOLD: Time in seconds to mark a server as disconnected.

📫 Contact
For questions or issues, please reach out to messafi@1337.gmail.com
