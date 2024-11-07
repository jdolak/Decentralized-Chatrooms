#!/usr/bin/env python3

import curses
import logging
from functools import partial

logging.basicConfig(
     filename="log",
     encoding="utf-8",
     filemode="a",
     format="{asctime} - {levelname} - {message}",
     style="{",
     datefmt="%Y-%m-%d %H:%M",
 )

def _print_messages(stdscr : curses.window, messages):
    while True:
        stdscr.clear()
        stdscr.border()
        curses.echo()
        h, w = stdscr.getmaxyx()

        start = 0
        if len(messages) >= h - 4:
            start = len(messages) - h + 4
            print(start)

        for n, i in enumerate(range(start, len(messages))):
            out = f'{messages[i][0]} : {messages[i][1]}'
            stdscr.addstr(n+1, 1, out)

        stdscr.addstr(h - 2, 1, f'Message: ') 

        stdscr.refresh()
        msg = stdscr.getstr()

        messages.append(("Jachob", msg.decode()))

def print_messages(messages):
    curses.wrapper(partial(_print_messages,messages=messages))

if __name__ == '__main__':
    messages = [("Jachob", "hello there"), ("Jachob", "test1"), ("Jachob", "test2")]
    print_messages(messages)