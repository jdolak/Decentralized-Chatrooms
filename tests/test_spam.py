#!/usr/bin/env python3

import subprocess
import sys

def main():
    
    if len(sys.argv) != 3:
        print("Wrong number of arguments")
        return
      
    SPAM = 0.005 

    host = sys.argv[2]
    print(f"host : {host}")
    print(f"n : {sys.argv[1]}")
    

    command = f'for i in {{1..{sys.argv[1]}}}; do bash -c "python3 ./src/main.py --headless=True --username=test-spam-$i --join={host} --spam={SPAM}" & done; wait'
    print(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)


if __name__ == '__main__':
    main()