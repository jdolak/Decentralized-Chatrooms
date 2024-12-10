#!/usr/bin/env python3

from node import Chatnode, catalog_register
from ui import print_messages, headless
from tools import NAME, ARGS
from benchmarking import test_latency

import threading


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

            test_latency(chatnode)

            while(True):
                pass

    except KeyboardInterrupt:
        exit(0)
	

if __name__ == '__main__':
    main()