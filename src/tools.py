import logging

DEBUG = False

logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(funcName)s() - %(message)s',
                    filename="errors.log",
                    encoding="utf-8",
                    filemode="a")

LOG = logging.getLogger()
