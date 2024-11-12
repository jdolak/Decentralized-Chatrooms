#!/usr/bin/env python3

import json
import socket

from networking import send_rpc, receive_rpc, parse_rpc

class Chatnode:
    def __init__(self, username) -> None:

        self.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_prev = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket_prev.bind(('',0))
        self.socket_prev_port = self.socket_prev.getsockname()[1]

        self.username = username
        self.messages = []


def join_node(node:Chatnode, input):
    return 0

def send_chat(node:Chatnode, chat_msg:str):

    rpc = f'{{"action" : "new-msg", "user" : {node.username}, "content" : {chat_msg}}}'
    send_rpc(node.socket_next, rpc)

def get_new_messages(node:Chatnode):
    try:
        parse_rpc(receive_rpc(node.socket_prev), node, node.socket_prev)
    except:
        pass

	

if __name__ == '__main__':
    pass