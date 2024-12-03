#!/usr/bin/env python3

import json

from tools import DEBUG, LOG
from files import log_transaction
import socket

class socketTimout(Exception):
    pass


def send_rpc(c_socket, msg):
    """
    Sends an RPC message through the given socket.
    """
    msg_len = len(msg)
    totalsent = 0
    msg = bytes(f'{msg_len:09d}' + msg, 'utf-8')
    c_socket.settimeout(5)  # Timeout after 5 seconds

    if DEBUG:
        LOG.info(f"{c_socket.fileno()} : {msg}")

    try:
        while totalsent < msg_len:
            sent = c_socket.send(msg[totalsent:])
            if sent == 0:
                LOG.error("Socket connection broken")
                raise RuntimeError("Socket connection broken")
            totalsent += sent
    except socketTimout:
        LOG.error("RPC send timed out.")
    except Exception as e:
        LOG.error(f"Error sending RPC: {e}")
    finally:
        c_socket.settimeout(None)


def parse_rpc(msg:bytes, node, sock:socket.socket):

    if not msg:
        return 0

    data = msg.decode('utf-8')
    data = json.loads(data)

    try:
        #log_transaction(data, msg_arr)
        pass
    except Exception as e:
        LOG.error(f"logging error:\n{e}")

    response = perform_tx(data, node, msg)

    if response:
        send_rpc(sock, json.dumps(response))
    
    return 0

def perform_tx(data, node, msg:bytes):

    try:
        if data["method"] == "new-msg":
            LOG.info(f"Recieved new-msg : {data}")
            if data["user"] != node.username:
                node.messages.append((data["user"], data["content"]))
            pass_along(data, node, msg)

        elif data["method"] == "update-prev":
            LOG.info(f"Recieved update-prev rpc : {data}")
            update_prev(data, node)

        elif data["method"] == "update-next":
            LOG.info(f"Recieved update-next rpc : {data}")
            update_next(data, node)

        elif data["method"] == "new-prev":
            LOG.info(f"Recieved new-prev rpc : {data}")
            new_prev(data, node)

        else:
            LOG.warning(f"Recieved unknown rpc : {data}")


    except Exception as e:
        LOG.error(f"Something went wrong:\n{e}")
        response = data
        response["result"] = "Error"

    return 0


def receive_rpc(c_socket)->bytes:

    msg = c_socket.recv(9)
    
    if not len(msg):
        return 0

    try:
        msg_size = int(msg.decode())
    except Exception as e:
        LOG.error(f"Bad read : {e}")
        return 0

    chunks = []
    bytes_recd = 0

    while bytes_recd < msg_size:
        chunk = c_socket.recv(min(msg_size - bytes_recd, 2048))
        if chunk == b'':
            LOG.error("socket connection broken")
        chunks.append(chunk)
        bytes_recd = bytes_recd + len(chunk)
    return b''.join(chunks)

def pass_along(data, node, msg:bytes):
    
    if data["method"] == "new-msg" and data["user"] != node.username:
        msg = msg.decode('utf-8')
        send_rpc(node.socket_next, msg)

	
def update_prev(data, node):
    host = data["host"]
    port = data["listing_port"]

    if node.no_neighbor:
        try:
            node.socket_next.connect((host,int(port)))
            node.no_neighbor = False
            node.next_user = data["user"]
            LOG.info(f"added {(host,int(port))} as next node")
        except Exception as e:
            LOG.error(f"Failed to set {(host,int(port))} as next node : {e}")

    else:
        try:
            LOG.info(f"Attempting to send update-next message")
            rpc = json.dumps({
                "method": "update-next",
                "user": data["user"],
                "host": host,
                "port": port
            })
            send_rpc(node.socket_prev_c, rpc)
            LOG.info(f"sent : {rpc}")
        except:
            LOG.error(f"Failed to set previous node : {e}")
    node.socket_prev_c = node.socket_curr_c
    node.prev_user = data["user"]

def update_next(data, node):
    try:
        node.socket_next.close()
        node.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:
        LOG.error(f"Error closing and creating new socket : {e}")
    
    try:
        node.socket_next.connect((data["host"], int(data["port"])))
        rpc = json.dumps({
                "method": "new-prev",
                "user" : node.username
            })
        send_rpc(node.socket_next, rpc)

        node.next_user = data["user"]
        LOG.info(f"Next node now set to {node.next_user}")
    except Exception as e:
        LOG.error(f"Error sending new-prev : {e}")

def new_prev(data, node):
    node.socket_prev_c = node.socket_curr_c
    node.prev_user = data["user"]
    LOG.info(f"Previous node now set to {node.prev_user}")
 
    

if __name__ == '__main__':
    pass
