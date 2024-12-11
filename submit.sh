#!/bin/bash

tar -xzf ./src.tar
python3 ./src/main.py --headless=True --username=test-join-$HOSTNAME --join=student10.cse.nd.edu:33823"