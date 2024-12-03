#!/usr/bin/env python3

import json
import socket
from tools import LOG
from networking import send_rpc, receive_rpc, parse_rpc


class Chatnode:
    def __init__(self, username) -> None:
        """
        Initialize the chat node with username and sockets.
        """
        self.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_prev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the previous socket to a random available port
        self.socket_prev.bind(('', 0))
        self.socket_prev_port = self.socket_prev.getsockname()[1]

        self.username = username
        self.messages = []
        self.hostname = socket.gethostname() 
        self.addr = f"{socket.gethostname()}:{self.socket_prev_port}"
        self.no_neighbor = True


    def start_listening(self):
        """
        Start listening for incoming connections on the previous socket.
        """
        self.socket_prev.listen(5)
        LOG.info(f"{self.username} is listening on port {self.socket_prev_port}")

        while True:
            conn, addr = self.socket_prev.accept()
            LOG.info(f"Connection accepted from {addr}")

            try:
                while (data := receive_rpc(conn)):
                    if data:
                        parse_rpc(data, self, conn)
            except Exception as e:
                LOG.error(f"Error handling connection: {e}")


def join_node(node: Chatnode, next_node_address: str) -> bool:
    """
    Connect the current node to the next node in the ring.
    """
    try:
        next_host, next_port = next_node_address.split(":")
        LOG.info((next_host, int(next_port)))
        node.socket_next.connect((next_host, int(next_port)))
        LOG.info(f"{node.username} connected to next node at {next_host}:{next_port}")

        # Notify the next node to update its predecessor
        rpc = json.dumps({
            "method": "update-prev",
            "host": node.hostname,
            "listing_port": node.socket_prev_port,
            "username" : node.username
        })
        send_rpc(node.socket_next, rpc)
        send_chat(node, f"{node.username} has joined...")
        LOG.info("Sent update-prev RPC to next node.")
        node.no_neighbor = False
    except Exception as e:
        LOG.error(f"Failed to join ring {next_node_address}: {e}")
        return 1
    return 0


def send_chat(node: Chatnode, chat_msg: str):
    """
    Sends a chat message to the next node in the ring.
    """
    try:
        rpc = json.dumps({
            "method": "new-msg",
            "user": node.username,
            "content": chat_msg
        })
        send_rpc(node.socket_next, rpc)
        LOG.info(f"Message sent from {node.username}: {chat_msg}")
    except Exception as e:
        LOG.error(f"Failed to send message: {e}")


def get_new_messages(node: Chatnode):
    """
    Retrieve new messages from the previous node in the ring.
    """
    try:
        parse_rpc(receive_rpc(node.socket_prev), node, node.socket_prev)
    except Exception as e:
        #LOG.error(f"Error receiving new messages: {e}")
        pass


if __name__ == '__main__':
    # Example initialization
    username = input("Enter username: ")
    chatnode = Chatnode(username)

    # Start listening in a separate thread or process
    import threading
    listener_thread = threading.Thread(target=chatnode.start_listening, daemon=True)
    listener_thread.start()

    # Connect to the ring and start interacting
    next_node = input("Enter next node address (host:port): ")
    if join_node(chatnode, next_node):
        LOG.info(f"{username} successfully joined the ring.")
    else:
        LOG.error(f"Failed to join the ring. Exiting.")