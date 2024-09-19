# Real-Time Server Monitoring

## 🚀 Features

### 📊 Real-Time Data
- Live system metrics from client servers.

### 🔄 Dynamic Updates
- Real-time terminal table updates using `rich`.

### 🎨 Color-Coded Status
- Green for connected servers, red for disconnected ones.

### 🔌 Port Management
- Handles server reconnects with varying ports.

## 🛠️ Requirements

- **Python 3.x**
- **`rich`** library (for terminal display)

## 📝 Installation

### 1. Clone the Repository


git clone https://github.com/Mouhcine-ESSAFI/Salvia-RTM.git
cd your-repository 

### 2. Set Up a Virtual Environment

python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install rich

### ⚙️ Usage
#### 1. Start the Central Server
python central-server.py

#### 2. Run the Client Server
Update CENTRAL_SERVER_HOST and CENTRAL_SERVER_PORT in client-server.py, then:

python client-server.py

## 🔧 Configuration
HOST: IP address for the central server (default: 0.0.0.0).
PORT: Port for the central server (default: 65432).
DISCONNECT_THRESHOLD: Time in seconds to mark a server as disconnected.

## 📫 Contact
For questions or issues, messafi1337@gmail.com
