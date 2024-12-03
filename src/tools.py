import logging
import argparse

DEBUG = False

parser = argparse.ArgumentParser(prog='p2p chat')
parser.add_argument('--headless', type=bool, default=False, required=False)
parser.add_argument('--join', type=str, default=0, required=False)
parser.add_argument('--spam', type=bool, default=False, required=False)
parser.add_argument('--username', type=str, default=0, required=False)
ARGS = parser.parse_args()

if not ARGS.username:
    NAME = input("Enter username: ")
else:
    NAME = ARGS.username

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s',
                    filename=f"{NAME}-errors.log",
                    encoding="utf-8",
                    filemode="a")

LOG = logging.getLogger()