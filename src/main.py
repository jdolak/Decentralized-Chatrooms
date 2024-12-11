#!/usr/bin/env python3

from node import Chatnode, catalog_register
from ui import print_messages, headless
from tools import NAME, ARGS
from bench_latency import test_latency
from files import read_chats_local_file

import threading


chatnode = Chatnode(NAME)

def main():
    try:
        threading.Thread(target=chatnode.start_listening, daemon=True).start()
        chatnode.messages = read_chats_local_file(chatnode)
        chatnode.messages.append(("SYSTEM", "system", f"you are listening on {chatnode.addr}"))

        if ARGS.advertise:
            threading.Thread(target=catalog_register, args=(chatnode,), daemon=True).start()

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