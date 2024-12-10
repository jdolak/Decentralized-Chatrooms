#!/usr/bin/env python3

import json

from tools import DEBUG, LOG
from files import log_transaction
import socket
import time

class socketTimout(Exception):
    pass


def send_rpc(node, c_socket, msg):
    """
    Sends an RPC message through the given socket.
    """
    msg_len = len(msg)
    totalsent = 0
    payload = bytes(f'{msg_len:09d}' + msg, 'utf-8')
    #c_socket.settimeout(5)  # Timeout after 5 seconds

    LOG.debug(f"{c_socket.fileno()} : {payload}")

    try:
        while totalsent < msg_len:
            sent = c_socket.send(payload[totalsent:])
            if sent == 0:
                LOG.error("Socket connection broken")
                raise RuntimeError("Socket connection broken")
            totalsent += sent
    except socketTimout:
        LOG.error("RPC send timed out.")
        raise RuntimeError("Send failed")
    except BrokenPipeError:
        if not find_node(node):
            resend_after_fail(node, msg)
        else:
            raise RuntimeError("Send failed")
    except Exception as e:
        LOG.error(f"Error sending RPC: {e}")
        raise RuntimeError("Send failed")
    #finally:
    #    if type(c_socket) != int:
    #        c_socket.settimeout(None)
    return 0

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
        send_rpc(node, sock, json.dumps(response))
    return 0


def perform_tx(data, node, msg:bytes):

    try:
        if data["method"] == "new-msg":
            LOG.info(f"Recieved new-msg : {data}")
            new_msg(data, node, msg)

        elif data["method"] == "update-prev":
            LOG.info(f"Recieved update-prev rpc : {data}")
            update_prev(data, node)

        elif data["method"] == "update-next":
            LOG.info(f"Recieved update-next rpc : {data}")
            update_next(data, node)

        elif data["method"] == "new-prev":
            LOG.info(f"Recieved new-prev rpc : {data}")
            new_prev(data, node)

        elif data["method"] == "rollcall-checkin":
            LOG.info(f"Recieved rollcall-checkin rpc : {data}")
            rollcall_checkin(data, node)

        elif data["method"] == "rollcall-results":
            LOG.info(f"Recieved rollcall-results rpc : {data}")
            rollcall_results(data, node, msg)

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
    try:
        id = (data["user"], data["timestamp"])

        if id in node.seen_set:
            return
        node.seen_set.add(id)
    
        if data["user"] != node.username:
            msg = msg.decode('utf-8')
            send_rpc(node, node.socket_next, msg)
    except Exception as e:
        LOG.error(f"Error passing along : {e} : {msg} : {data}")

	
def update_prev(data, node):

    host = data["host"]
    port = data["listing_port"]

    if node.no_neighbor:
        try:
            node.socket_next.connect((host,int(port)))
            node.no_neighbor = False
            node.next_user = data["user"]
            node.socket_prev_incoming.insert(0, node.socket_next)

            rpc = json.dumps({
                "method": "new-prev",
                "user" : node.username
            })
            send_rpc(node, node.socket_next, rpc)

            LOG.info(f"added {(host,int(port))} as next node")
        except Exception as e:
            LOG.error(f"Failed to set {(host,int(port))} as next node : {e}")

    else:
        try:
            LOG.info(f"Attempting to send update-next message to {node.socket_prev_c}")
            rpc = json.dumps({
                "method": "update-next",
                "user": data["user"],
                "host": host,
                "port": port
            })
            send_rpc(node, node.socket_prev_c, rpc)
            LOG.info(f"sent update-next: {rpc}")
        except Exception as e:
            LOG.error(f"Failed to set previous node : {e}")
    LOG.debug(f"socket prev client set to : {node.socket_curr_c} from {node.socket_prev_c}")
    node.socket_prev_c = node.socket_curr_c
    node.prev_user = data["user"]


def update_next(data, node):

    try:
        node.socket_next.close()
        node.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except Exception as e:
        LOG.error(f"Error closing and creating new socket : {e}")
    
    try:
        LOG.debug(f"Attempting to send new-prev to {data["host"]}:{data["port"]}")
        node.socket_next.connect((data["host"], int(data["port"])))
        node.socket_prev_incoming.insert(0, node.socket_next)
        rpc = json.dumps({
                "method": "new-prev",
                "user" : node.username
            })
        send_rpc(node, node.socket_next, rpc)

        node.next_user = data["user"]
        LOG.info(f"Next node now set to {node.next_user}")
    except Exception as e:
        LOG.error(f"Error sending new-prev : {e}")


def new_prev(data, node):

    node.socket_prev_c = node.socket_curr_c
    node.prev_user = data["user"]
    LOG.info(f"Previous node now set to {node.prev_user}")

    start_rollcall(data, node)


def new_msg(data, node, msg):

    if data["user"] != node.username and data["channel"] in node.subscribed_channels:
        node.messages.append((data["author"], data["channel"], data["content"]))
    else:
        spam_test(data,node)
    pass_along(data, node, msg)


def start_rollcall(data, node):
    
    try:
        rpc = json.dumps({
            "method": "rollcall-checkin",
            "user": node.username,
            "attendance": [[node.username, node.hostname, node.socket_prev_s_port],]
        })
        send_rpc(node, node.socket_next, rpc)
        LOG.info("Sending rollcall")
    except Exception as e:
        LOG.error(f"Error starting rollcall : {e}")


def rollcall_checkin(data, node):

    if data["user"] == node.username:
        try:
            rpc = json.dumps({
                "method": "rollcall-results",
                "user": data["user"],
                "timestamp": time.time(),
                "attendance": data["attendance"]
            })
            send_rpc(node, node.socket_next, rpc)
            LOG.debug(f"sending results : {rpc}")
        except Exception as e:
            LOG.error(f"Error starting rollcall result: {e}") 
    else:
        try:
            data["attendance"].append([node.username, node.hostname, node.socket_prev_s_port]) 
            LOG.debug(f"sending checkin : {data}")
            send_rpc(node, node.socket_next, json.dumps(data))
        except Exception as e:
            LOG.error(f"error passing attendance along : {e}")


def rollcall_results(data, node, msg):

    node.node_directory = data["attendance"]
    LOG.debug(f"updated directory to : {node.node_directory}")
    pass_along(data, node, msg)


def spam_test(data, node):

    if f"{node.username}-latency" in data["content"]:
        try:
            _, num, stime = data["content"].split(':')
            if num in node.test_set:
                node.dups = node.dups + 1
            else:
                node.test_set[num] = time.time() - float(stime)
                #LOG.debug(f"timestamps={node.username}:{time.time()}:{stime}")
        except Exception as e:
            LOG.warning(f"could not parse : {data["content"]} : {e}")


def find_node(node):

    LOG.warning(f"Failed to connect to next node, starting failure handeling...")
    self_index = -1
    i = 0

    while True:
        if node.username == node.node_directory[i][0]:
            self_index = i
        elif self_index != -1:
            if node.username == node.node_directory[i][0]:
                return 1
            else:
                try:
                    address = f"{node.node_directory[i][1]}:{node.node_directory[i][2]}"
                    LOG.info(f"Trying to join node {node.node_directory[i][0]} at {address}")
                    if not join_node(node, address):
                        return 0
                except Exception as e:
                    LOG.warning(f"Failed to join node {node.node_directory[i][0]} at {address}")
                    
        i = i + 1
        i = i % len(node.node_directory)


def join_node(node, next_node_address: str) -> bool:
    """
    Connect the current node to the next node in the ring.
    """
    try:
        next_host, next_port = next_node_address.split(":")
        LOG.info((next_host, int(next_port)))

        node.socket_next.close()
        node.socket_next = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node.socket_next.connect((next_host, int(next_port)))
        node.next_user = f"{next_host}:{next_port}" 
        LOG.info(f"{node.username} connected to next node at {next_host}:{next_port}")

        node.socket_prev_incoming.insert(0, node.socket_next)

        # Notify the next node to update its predecessor
        rpc = json.dumps({
            "method": "update-prev",
            "host": node.hostname,
            "listing_port": node.socket_prev_s_port,
            "user" : node.username
        })
        send_rpc(node, node.socket_next, rpc)
        LOG.info("Sent update-prev RPC to next node.")

        try:
            rpc = json.dumps({
                "method": "new-msg",
                "timestamp": time.time(),
                "author": "CLUSTER",
                "channel": "system",
                "user": node.username,
                "content": f"{node.username} has joined..."
            })
            send_rpc(node, node.socket_next, rpc)
            LOG.info(f"Sent {node.username} join message")
        except Exception as e:
            LOG.error(f"Failed to send join message: {e}")

        node.no_neighbor = False
    except Exception as e:
        LOG.error(f"Failed to join ring {next_node_address}: {e}")
        return 1
    return 0


def resend_after_fail(node, msg):

    data = json.loads(msg)
    if data["method"] == "new-msg":
        send_rpc(node, node.socket_next, msg)


if __name__ == '__main__':
    pass
