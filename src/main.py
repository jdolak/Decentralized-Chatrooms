#!/usr/bin/env python3

from node import Chatnode, catalog_register
from ui import print_messages, headless, send_chat
from tools import NAME, ARGS, LOG
import threading
import time

chatnode = Chatnode(NAME)

def main():
    try:
        listener_thread = threading.Thread(target=chatnode.start_listening, daemon=True)
        listener_thread.start()
        chatnode.messages = [("SYSTEM", "system", f"you are listening on {chatnode.addr}")]

        if ARGS.advertise:
            catalog_thread = threading.Thread(target=catalog_register, args=(chatnode,), daemon=True).start()


        if not ARGS.headless:
            print_messages(chatnode)
        else:
            threading.Thread(target=headless, args=(chatnode, ARGS), daemon=True).start()

            start = 0
            last_len = 0
            #time.sleep(5)
            while(True):
                if not ARGS.spam:
                    length = len(set(map(lambda x:x[0], chatnode.node_directory)))
                    if not start and length > 1:
                        start = time.time()
                    elif start and last_len < length:  
                        print(length, time.time() - start )
                        last_len = length
                else:
                    try:
                        send_chat(chatnode, f"{chatnode.username}-latency:{start}:{time.time()}")
                    except:
                        pass
                    start = start + 1
                    time.sleep(ARGS.spam)

                    if start >= 250:
                        break

            LOG.debug(f"average latency {chatnode.username}:  {sum(chatnode.test_set.values()) / len(chatnode.test_set.keys())}")
            LOG.debug(f"dupicates {chatnode.username}: {chatnode.dups}")

            while(True):
                pass


    except KeyboardInterrupt:
        exit(0)
	

if __name__ == '__main__':
    main()