#!/usr/bin/env python3
import json

def read_chats_local_file(being, end):
     pass
      
def write_chat_local_file(msg :list[str], filename="chats.log"):

    line = json.dumps(msg)

    with open(filename, 'a') as f:
         f.write(line)

def log_transaction():
     pass

if __name__ == '__main__':
    pass