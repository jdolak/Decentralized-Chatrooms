#!/usr/bin/env python3

from node import Chatnode, catalog_register
from ui import print_messages, headless
from tools import NAME, ARGS, LOG
from bench_latency import test_latency
from files import read_chats_local_file

import threading
import time


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
                if chatnode.throughput_active >= 2:
                    time.sleep(5)
                    LOG.critical(f"# average latency {chatnode.username}:  {sum(chatnode.test_set.values()) / len(chatnode.test_set.keys())}")
                    LOG.critical(f"# dupicates {chatnode.username}: {chatnode.dups}")
                    break
            while(True):
                pass


    except KeyboardInterrupt:
        exit(0)
	

if __name__ == '__main__':
    main()