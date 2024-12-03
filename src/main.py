#!/usr/bin/env python3

from node import Chatnode
from ui import print_messages, headless
from tools import NAME, ARGS
import threading
import time

chatnode = Chatnode(NAME)

def main():
    try:
        listener_thread = threading.Thread(target=chatnode.start_listening, daemon=True)
        listener_thread.start()
        chatnode.messages = [("SYSTEM", "system", f"you are listening on {chatnode.addr}")]

        if not ARGS.headless:
            print_messages(chatnode)
        else:
            threading.Thread(target=headless, args=(chatnode, ARGS), daemon=True).start()

            start = 0
            last_len = 0

            while(True):
                length = len(set(map(lambda x:x[0], chatnode.node_directory)))
                if not start and length > 1:
                    start = time.time()
                elif start and last_len < length:  
                    print(length, time.time() - start )
                    last_len = length

    except KeyboardInterrupt:
        exit(0)
	

if __name__ == '__main__':
    main()