import logging

DEBUG = False

NAME = input("Enter username: ")

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s',
                    filename=f"{NAME}-errors.log",
                    encoding="utf-8",
                    filemode="a")

LOG = logging.getLogger()
