from tools import LOG, ARGS
from ui import send_chat

import time

def test_latency(chatnode):  
        try:
            start = 0
            last_len = 0
            time.sleep(100)
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

                    if start >= 20:
                        break

            chatnode.throughput_active = 2
            
        except Exception as e:
            LOG.error(f"error during latency testing : {e}")
