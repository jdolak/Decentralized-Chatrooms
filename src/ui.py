#!/usr/bin/env python3

import curses
import threading
import time

from node import join_node, send_chat, Chatnode, get_new_messages
from functools import partial

def _print_messages(stdscr : curses.window, node:Chatnode):

    messages = node.messages

    h, w = stdscr.getmaxyx()
    win = curses.newwin(h-2, w, 0, 0)
    curses.curs_set(False)
    threading.Thread(target=take_user_input, args=(stdscr, win, node), daemon=True).start()
    
    simulation_user(messages)

    while True:

        get_new_messages(node)

        win.clear()
        win.border()
        curses.echo()

        start = 0
        if len(messages) >= h - 4:
            start = len(messages) - h + 4
            print(start)

        for n, i in enumerate(range(start, len(messages))):
            out = f'{messages[i][0]} : {messages[i][1]}'
            win.addstr(n+1, 1, out)

        win.refresh()
        time.sleep(0.25)


def print_messages(node:Chatnode):
    curses.wrapper(partial(_print_messages,node=node))


def simulation_user(messages):
    threading.Thread(target=_simulation_user, args=(messages,), daemon=True).start()
    
def _simulation_user(messages):
    while True:
        messages.append(("user1", "chat?"))
        time.sleep(2)


def take_user_input(stdscr : curses.window, win: curses.window, node:Chatnode):
    messages = node.messages
    stdscr.keypad(True)
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(h - 2, 1, f'Message: ') 

        msg = stdscr.getstr().decode()
        if msg.startswith('/'):
            messages.append(("COMMAND", msg))
            win.refresh()
            if not parse_command(node, msg):
               messages.append(("SYSTEM", "SUCCESS")) 
        else:
            try:
                send_chat(node, msg)
                messages.append((node.username, msg))
            except Exception as e:
                messages.append((node.username, msg))
                messages.append(("ERROR", e))

        stdscr.refresh()
        win.refresh()


def parse_command(node:Chatnode, msg:str):

    msg = msg.strip('/')
    args = msg.split()

    if args[0] == "cluster" and args[1] == "join":
        return join_node(node, args[2])


if __name__ == '__main__':
    messages = [("Jachob", "hello there"), ("Jachob", "test1"), ("Jachob", "test2")]
    print_messages(messages)