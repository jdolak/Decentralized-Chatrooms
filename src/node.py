#!/usr/bin/env python3

import json
import socket
from tools import LOG
from networking import send_rpc, receive_rpc, parse_rpc
import select


class Chatnode:
    def __init__(self, username) -> None:
        """
        Initialize the chat node with username and sockets.
        """
        self.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_prev_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_prev_c = 0
        self.socket_prev_incoming = []
        self.socket_curr_c = 0

        # Bind the previous socket to a random available port
        self.socket_prev_s.bind(('', 0))
        self.socket_prev_s_port = self.socket_prev_s.getsockname()[1]

        self.username = username
        self.messages = []
        self.hostname = socket.gethostname() 
        self.addr = f"{socket.gethostname()}:{self.socket_prev_s_port}"
        self.no_neighbor = True

        self.prev_user = ""
        self.next_user = ""

        self.channel_curr = "general"
        self.subscribed_channels = set(["general", "system"])

        self.node_directory = []

    def start_listening(self):
        """
        Start listening for incoming connections on the previous socket.
        """

        self.socket_prev_s.listen()

        LOG.info(f"{self.username} is listening on port {self.socket_prev_s_port}")

        while True:
            try:
                if select.select([self.socket_prev_s],[],[],0)[0]:
                    LOG.debug(f"socket availible")
                    tmp_socket, addr = self.socket_prev_s.accept()
                    tmp_socket.setblocking(False)
                    self.socket_prev_incoming.insert(0,tmp_socket)
                    LOG.info(f"Connection accepted from {addr}")
            except Exception as e:
                LOG.error(f"error accepting socket : {e}")

            try:
                self.socket_prev_incoming = list(filter(lambda x: x.fileno() > 0, self.socket_prev_incoming))

                for client in select.select(self.socket_prev_incoming, [],[],0)[0]:
                    self.socket_curr_c = client

                    try: 
                        data = receive_rpc(client)
                        if data:
                            parse_rpc(data, self, client)
                    except Exception as e:
                        LOG.error(f"Error handling RPC : {e}")
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

        node.socket_prev_incoming.insert(0, node.socket_next)

        # Notify the next node to update its predecessor
        rpc = json.dumps({
            "method": "update-prev",
            "host": node.hostname,
            "listing_port": node.socket_prev_s_port,
            "user" : node.username
        })
        send_rpc(node.socket_next, rpc)
        LOG.info("Sent update-prev RPC to next node.")

        try:
            rpc = json.dumps({
                "method": "new-msg",
                "author": "CLUSTER",
                "channel": "system",
                "user": node.username,
                "content": f"{node.username} has joined..."
            })
            send_rpc(node.socket_next, rpc)
            LOG.info(f"Sent {node.username} join message")
        except Exception as e:
            LOG.error(f"Failed to send join message: {e}")

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
            "author": node.username,
            "channel": node.channel_curr,
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
        parse_rpc(receive_rpc(node.socket_prev_s), node, node.socket_prev_s)
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