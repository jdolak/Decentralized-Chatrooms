#!/usr/bin/env python3

import json
import os
import pickle
from tools import LOG, NAME, CKPT_FILE, LOG_FILE

def read_chats_local_file(node) -> list:
    """
    Read a range of chat messages from the local file.
    Args:
        start (int): The starting index of messages to read.
        end (int): The ending index of messages to read.
        filename (str): The file where chats are stored.
    Returns:
        list: A list of chat messages in the specified range.
    """

    ckpt = CKPT_FILE
    log = LOG_FILE

    messages = read_ckpt(node, ckpt)

    if not os.path.exists(log):
        return messages

    try:
        with open(log, 'r') as f:
            for line in f:
                data = json.loads(line)
                messages.append((data["author"], data["channel"], data["content"]))
        return messages
    except Exception as e:
        LOG.error(f"Error reading file {log} and {ckpt}: {e}")
        return []
    

def read_ckpt(node, checkpoint)->list:
    try:
        if not os.path.exists(checkpoint):
            with open(checkpoint, 'wb') as f:
                pickle.dump(node.messages,f)

                f.flush()
                os.fsync(f.fileno())

        with open(checkpoint, 'rb') as f:
            messages = pickle.load(f)
            return messages
    except Exception as e:
        LOG.error(f"error reading checkpoint : {e}")
        return []


def write_chat_local_file(msg, filename=LOG_FILE):
    """
    Append a single chat message to the local file.
    Args:
        msg (dict): The message to append.
        filename (str): The file where chats are stored.
    """
    try:
        with open(filename, 'a') as f:
            f.write(msg + '\n')
            LOG.debug(f"Message written to file: {str(msg)}")
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


def create_checkpoint(node, checkpoint, log):

    with open(f"{checkpoint}.swp", 'wb') as f:
        pickle.Pickler(f).dump(node.messages)
        f.flush()
        os.fsync(f.fileno())

    os.rename(f"{checkpoint}.swp", checkpoint)

    with open(log, 'w+') as f:
        f.truncate(0)
        f.flush()
        os.fsync(f.fileno())

    return 0



if __name__ == '__main__':
    # Example usage
    example_message = {"user": "Alice", "content": "Hello, world!"}
    write_chat_local_file(example_message)
    messages = read_chats_local_file(0, 10)
    print(messages)
