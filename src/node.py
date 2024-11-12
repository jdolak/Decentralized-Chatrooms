#!/usr/bin/env python3

import json
import socket

from networking import send_rpc

class Chatnode:
    def __init__(self, username) -> None:

        self.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_prev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socket_prev.bind(('',0))
        self.port = self.socket_prev.getsockname()[1]

        self.username = username
        self.messages = []

def join_node(cluster):
    return 0

def send_chat(node:Chatnode, chat_msg:str):

    sock = node.socket_next
    rpc = f'{{"action" : "new-msg", "user" : {node.username}, "content" : {chat_msg}}}'
    send_rpc(sock, rpc)

	

if __name__ == '__main__':
    pass