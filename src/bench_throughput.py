from tools import LOG, ARGS

import time

def test_throughput(node):
    try:    
        if ARGS.spam:
            if node.throughput_active < 1:
                node.throughput_active = 1
                node.throughput_start = time.time()
            if node.throughput_active == 1:
                node.throughput_count = node.throughput_count + 1
            elif node.throughput_active == 2:
                end = time.time()
                elapsed = end - node.throughput_start

                throughput = node.throughput_count / elapsed
                latency = elapsed / node.throughput_count
                LOG.critical(f" # throughput test result : throughput {throughput} : latency {latency} : elapsed {elapsed}")
                node.throughput_active = 3
            elif node.throughput_active > 2:
                return
        else:
            return
    except Exception as e:
        LOG.error(f"error doing throughput benchmark : {e} : elapsed {elapsed} : count {node.throughput_count}")