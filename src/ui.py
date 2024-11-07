#!/usr/bin/env python3

import curses
import threading
import time
from functools import partial

def _print_messages(stdscr : curses.window, messages):

    h, w = stdscr.getmaxyx()
    win = curses.newwin(h-2, w, 0, 0)
    curses.curs_set(False)
    threading.Thread(target=get_more_msgs, args=(stdscr, win, messages), daemon=True).start()
    
    simulation_user(messages)


    while True:
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

        #stdscr.addstr(h - 2, 1, f'Message: ')
        win.refresh()
        time.sleep(0.25)


def print_messages(messages):
    curses.wrapper(partial(_print_messages,messages=messages))


def simulation_user(messages):
    threading.Thread(target=_simulation_user, args=(messages,), daemon=True).start()
    
def _simulation_user(messages):
    while True:
        messages.append(("user1", "chat?"))
        time.sleep(2)


def get_more_msgs(stdscr : curses.window, win: curses.window, messages):
    stdscr.keypad(True)
    while True:
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(h - 2, 1, f'Message: ') 
        messages.append(("Jachob", stdscr.getstr().decode()))
        stdscr.refresh()
        win.refresh()

def test():
    messages = [("Jachob", "hello there"), ("Jachob", "test1"), ("Jachob", "test2")]
    print_messages(messages)

if __name__ == '__main__':
    test()