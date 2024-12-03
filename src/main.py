#!/usr/bin/env python3

from node import Chatnode
from ui import print_messages
from tools import NAME
import threading

chatnode = Chatnode(NAME)

def main():
    try:
        listener_thread = threading.Thread(target=chatnode.start_listening, daemon=True)
        listener_thread.start()
        chatnode.messages = [("Jachob", "hello there"), ("Jachob", "test1"), ("Jachob", "test2")]
        chatnode.messages.append(("SYSTEM", f"you are listening on {chatnode.addr}"))
        print_messages(chatnode)
    except KeyboardInterrupt:
        exit(0)
	

if __name__ == '__main__':
    main()