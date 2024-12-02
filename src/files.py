#!/usr/bin/env python3

import json
import os
from tools import LOG

def read_chats_local_file(start: int, end: int, filename="chats.log") -> list:
    """
    Read a range of chat messages from the local file.
    Args:
        start (int): The starting index of messages to read.
        end (int): The ending index of messages to read.
        filename (str): The file where chats are stored.
    Returns:
        list: A list of chat messages in the specified range.
    """
    if not os.path.exists(filename):
        LOG.warning(f"File {filename} does not exist.")
        return []

    messages = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                messages.append(json.loads(line))
        return messages[start:end]
    except Exception as e:
        LOG.error(f"Error reading file {filename}: {e}")
        return []

def write_chat_local_file(msg: dict, filename="chats.log"):
    """
    Append a single chat message to the local file.
    Args:
        msg (dict): The message to append.
        filename (str): The file where chats are stored.
    """
    try:
        with open(filename, 'a') as f:
            f.write(json.dumps(msg) + '\n')
            LOG.info(f"Message written to file: {msg}")
    except Exception as e:
        LOG.error(f"Error writing to file {filename}: {e}")

def log_transaction(data: dict, msg_arr: list):
    """
    Log a transaction (e.g., a new message) locally and update the in-memory message array.
    Args:
        data (dict): The transaction data to log.
        msg_arr (list): The in-memory message array to update.
    """
    try:
        write_chat_local_file(data)
        msg_arr.append((data["user"], data["content"]))
        LOG.info(f"Transaction logged and in-memory array updated: {data}")
    except Exception as e:
        LOG.error(f"Error logging transaction: {e}")

if __name__ == '__main__':
    # Example usage
    example_message = {"user": "Alice", "content": "Hello, world!"}
    write_chat_local_file(example_message)
    messages = read_chats_local_file(0, 10)
    print(messages)
