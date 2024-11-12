#!/usr/bin/env python3

import json

from networking import send_rpc

class Chatnode:
    def __init__(self, username) -> None:

        self.socket_next = 0
        self.socket_prev = 0

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