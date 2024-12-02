#!/usr/bin/env python3

import json

from tools import DEBUG, LOG
from files import log_transaction
from socket import socket


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
                raise RuntimeError("Socket connection broken")
            totalsent += sent
    except socket.timeout:
        LOG.error("RPC send timed out.")
    except Exception as e:
        LOG.error(f"Error sending RPC: {e}")
    finally:
        c_socket.settimeout(None)


def parse_rpc(msg:bytes, node, sock:socket):

    msg_arr = node.messages

    if not msg:
        return 0

    data = msg.decode('utf-8')
    data = json.loads(data)

    try:
        log_transaction(data, msg_arr)
    except Exception as e:
        LOG.error(f"logging error:\n{e}")

    response = perform_tx(data, msg_arr)

    #send_rpc(sock, json.dumps(response))
    
    return 0

def perform_tx(data, node):

    msg_arr = node.messages

    try:
        match data["method"]:
            case "new-msg":
                result =  msg_arr.append((data["user"], data["content"]))
    except Exception as e:
        LOG.error(f"Something went wrong:\n{e}")
        response = data
        response["result"] = "Error"
    else:
        response = data
        response["result"] = result

    return response


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
	

if __name__ == '__main__':
    pass
