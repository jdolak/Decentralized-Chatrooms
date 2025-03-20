# Decentralized Chat Application

This project implements a distributed, decentralized, messaging system using a ring structure. The application allows nodes to join a network, send chat messages, and relay information across the network without requiring a centralized server. Each node in the network communicates with its predecessor and successor to form a resilient ring topology.

## Authors
- [Jachob Dolak](https://github.com/jdolak/)
- [Lang Li](https://github.com/easyrider11)

## How to Run the Application

### Prerequisites

- Python 3.12+

### Installation

1. Clone the repository and cd into it:
```bash
git clone git@github.com:jdolak/distsys-project.git
cd distsys-project
```

### Running the Application

1. Start a node:
```bash
python ./src/main.py
```
2. Type username when prompted:
```
Enter username: jdolak
```
4. Type `/join <address>:<port>` with the address of a node you would like to connect to:
```
[general] Message: /join student10:9123
```
5. Start chatting, just type and hit enter:
```
[general] Message: hello world!
```

## Features

- **Ring-based Peer-to-Peer Communication**: Nodes connect in a circular topology to ensure all messages can propagate across the network.
- **Decentralized Architecture**: No central server; each node is responsible for its own communication and message forwarding.
- **Dynamic Node Joining**: Nodes can dynamically join the ring and update the network's topology.
- **Message Relaying**: Messages are forwarded across the ring to ensure delivery to all participants.


## System Architecture

### Components

1. **Node**: Represents a participant in the ring. Each node has knowledge of its predecessor and successor.
2. **Networking**:
   - Responsible for sending and receiving messages (RPCs).
   - Ensures messages are relayed correctly across the ring.
3. **User Interface (UI)**:
   - Provides a terminal-based interface for users to send and view messages.
4. **Files**:
   - Handles logging and persistence of messages locally.

### Message Flow

1. **Sending a Message**:
   - The user inputs a message.
   - The message is sent to the next node in the ring.
   - Each node relays the message until it reaches all participants.

2. **Receiving a Message**:
   - Nodes listen for incoming messages from their predecessor.
   - Messages are parsed, processed, and added to the local message store.

### Example Workflow

1. **Node A** starts the application and listens for connections.
2. **Node B** starts the application and joins the ring by providing Node A's address.
3. **Node A** sends a message, which is relayed to **Node B**.
4. New nodes can continue joining the ring and participate in the chat.


## Code Overview

- **`node.py`**:
  - Defines the `Chatnode` class for managing a node's state and connections.
  - Handles joining the ring and sending/receiving messages.

- **`networking.py`**:
  - Implements low-level networking functions such as sending and receiving RPCs.
  - Processes and forwards messages across the ring.

- **`ui.py`**:
  - Provides a terminal-based interface for interacting with the system.

- **`files.py`**:
  - Manages message persistence and logging.


## Contributing

Contributions are welcome! If you'd like to improve this project, please:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.
