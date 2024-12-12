#!/bin/bash

tar -xzf ./src.tar
tar -xzf ./ppy.tar

source ./ppy/bin/activate

./ppy/bin/python3.12 ./src/main.py --headless=True --username=test-join-$HOSTNAME --join=student10.cse.nd.edu:37023