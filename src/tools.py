import logging
import argparse

DEBUG = False

#LOGS_DIR = "./logs/"
LOGS_DIR = "./"

parser = argparse.ArgumentParser(prog='p2p chat')
parser.add_argument('--headless', type=bool, default=False, required=False)
parser.add_argument('--join', type=str, default=0, required=False)
parser.add_argument('--spam', type=float, default=0, required=False)
parser.add_argument('--username', type=str, default=0, required=False)
parser.add_argument('-a','--advertise', nargs="?", const=True, default=0, required=False)
parser.add_argument('-ns','--nameserver', type=str, default="catalog.cse.nd.edu:9097", required=False)
ARGS = parser.parse_args()

if not ARGS.username:
    NAME = input("Enter username: ")
else:
    NAME = ARGS.username

logging.basicConfig(level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s',
                    filename=f"{LOGS_DIR}{NAME}-errors.log",
                    encoding="utf-8",
                    filemode="a")

LOG = logging.getLogger()

LOG_FILE = f"{LOGS_DIR}{NAME}-chats.log"
CKPT_FILE = f"{LOGS_DIR}{NAME}-chats.ckpt"