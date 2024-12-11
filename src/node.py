#!/usr/bin/env python3

import json
import socket
from tools import LOG, ARGS
from networking import send_rpc, receive_rpc, parse_rpc
from files import write_chat_local_file
import select
import time


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

        # Debug values, not used for operation
        self.prev_user = ""
        self.next_user = ""

        # Channel values
        self.channel_curr = "general"
        self.subscribed_channels = set(["general", "system"])
        self.seen_set = set()

        # Failure handeling
        self.node_directory = []

        # Testing values
        self.test_set = dict()
        self.dups = 0
        self.lost = 0
        self.test_order = []
        self.throughput_active = False
        self.throughput_count = 0
        self.throughput_start = 0


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


def send_chat(node: Chatnode, chat_msg: str):
    """
    Sends a chat message to the next node in the ring.
    """
    try:
        rpc = json.dumps({
            "method": "new-msg",
            "timestamp": time.time(),
            "user": node.username,
            "author": node.username,
            "channel": node.channel_curr,
            "content": chat_msg
        })
        send_rpc(node, node.socket_next, rpc)
        write_chat_local_file(node, rpc)
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


def catalog_register(node):
    try:
        info = dict()
        info["type"] = "distsys-project"
        info["owner"] = "jdolak"
        info["port"] = node.socket_prev_s_port
        if ARGS.advertise != True:
            info["project"] = ARGS.advertise
        else:
            info["project"] = f"p2p-chat"

        info["user"] = node.username

        addr, port = ARGS.nameserver.split(':')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = bytes(json.dumps(info),'utf-8')

        while True:
            sock.sendto(data, (addr, int(port)))
            LOG.info(f"Sent catalog register : {info} to {addr, port}")
            time.sleep(60)
    except Exception as e:
        LOG.error(f"Failed to send catalog register : {e}")

if __name__ == '__main__':
    pass