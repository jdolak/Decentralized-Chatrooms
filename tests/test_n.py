#!/usr/bin/env python3

import subprocess
import sys

def main():
    
    if len(sys.argv) != 3:
        print("Wrong number of arguments")
        return
      
    

    host = sys.argv[2]
    print(f"host : {host}")
    print(f"n : {sys.argv[1]}")
    
    for i in range(int(sys.argv[1])-1):
        command = f"python3 ./src/main.py --headless=True --username={i} --join={host}"
        print(command)
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        command = f'for i in {{1..{sys.argv[1]}}}; do bash -c "python3 ./src/main.py --headless=True --username=test-spam-$i --join={host} --spam={SPAM}" & done; wait'

    while True:
        pass

if __name__ == '__main__':
    main()