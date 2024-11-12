#!/usr/bin/env python3

from node import Chatnode
from ui import print_messages

chatnode = Chatnode("Jachob")


def main():
    
    chatnode.messages = [("Jachob", "hello there"), ("Jachob", "test1"), ("Jachob", "test2")]
    print_messages(chatnode)
	

if __name__ == '__main__':
    main()