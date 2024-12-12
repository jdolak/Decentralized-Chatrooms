#!/usr/bin/env python3

import subprocess
import sys
import time

def main():
    
    if len(sys.argv) != 3:
        print("Wrong number of arguments")
        return
      
    SPAM = 1

    host = sys.argv[2]
    print(f"host : {host}")
    print(f"n : {sys.argv[1]}")
    
    for i in range(int(sys.argv[1])-2):
        command = f"python3 ./src/main.py --headless=True --username={i} --join={host}"
        print(command)
        subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(0.33)

    command = f'python3 ./src/main.py --headless=True --username=test-spam --join={host} --spam={SPAM}'
    subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(command)

    while True:
        pass

if __name__ == '__main__':
    main()