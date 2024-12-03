#!/usr/bin/env python3

import curses
import threading
import time

from node import join_node, send_chat, Chatnode, get_new_messages
from functools import partial
from tools import LOG

def _print_messages(stdscr: curses.window, node: Chatnode):
    """
    Main curses loop for displaying messages and handling user input.
    Args:
        stdscr (curses.window): The curses standard screen window.
        node (Chatnode): The current chat node.
    """
    messages = node.messages

    h, w = stdscr.getmaxyx()
    win = curses.newwin(h - 2, w, 0, 0)

    threading.Thread(target=take_user_input, args=(stdscr, win, node), daemon=True).start()
    #simulation_user(messages)

    while True:
        get_new_messages(node)

        win.clear()
        win.border()
        curses.echo()



        start = 0
        if len(messages) >= h - 4:
            start = len(messages) - h + 4

        for n, i in enumerate(range(start, len(messages))):
            out = f'[{messages[i][1]}] {messages[i][0]} : {messages[i][2]}'
            win.addstr(n + 1, 1, out)
        curses.curs_set(False)
        win.refresh()
        curses.curs_set(True)
        time.sleep(0.25)

def print_messages(node: Chatnode):
    """
    Initialize the curses wrapper to display messages.
    Args:
        node (Chatnode): The current chat node.
    """
    curses.wrapper(partial(_print_messages, node=node))

def simulation_user(messages):
    """
    Starts a background thread simulating another user sending messages.
    Args:
        messages (list): List of messages.
    """
    threading.Thread(target=_simulation_user, args=(messages,), daemon=True).start()

def _simulation_user(messages):
    """
    Simulates another user sending messages periodically.
    Args:
        messages (list): List of messages.
    """
    while True:
        messages.append(("Lang", "general", "chat?"))
        time.sleep(2)

def take_user_input(stdscr: curses.window, win: curses.window, node: Chatnode):
    """
    Handles user input for sending messages or commands.
    Args:
        stdscr (curses.window): The curses standard screen window.
        win (curses.window): The curses message window.
        node (Chatnode): The current chat node.
    """
    messages = node.messages
    stdscr.keypad(True)
    while True:
        curses.curs_set(True)
        h, w = stdscr.getmaxyx()
        stdscr.clear()
        stdscr.addstr(h - 2, 1, f'[{node.channel_curr}] Message: ')

        msg = stdscr.getstr().decode()
        if msg.startswith('/'):
            messages.append(("COMMAND", "system", msg))
            win.refresh()
            response = parse_command(node, msg)
            messages.append(("SYSTEM", "system", response))

        else:
            try:
                send_chat(node, msg)
                messages.append((node.username, node.channel_curr, msg))
            except Exception as e:
                messages.append((node.username, node.channel_curr, msg))
                messages.append(("ERROR", "system", str(e)))
                LOG.warning(e)

        stdscr.refresh()
        win.refresh()

def parse_command(node: Chatnode, msg: str) -> bool:
    """
    Parses and executes a user command.
    Args:
        node (Chatnode): The current chat node.
        msg (str): The command message.
    Returns:
        bool: True if the command was successfully executed, False otherwise.
    """
    msg = msg.strip('/')
    args = msg.split()

    if args[0] == "cluster" and args[1] == "join":
        if join_node(node, args[2]):
            return "ERROR : Failed to join"
        else:
            return f"SUCCESS : joined {args[2]}"

    
    elif args[0] == "sub":
        node.subscribed_channels.add(args[1])
        return f"SUCCESS : subscribed to channel {args[1]}"

    elif args[0] == "unsub":
        if args[1] != "general":
            if args[1] in node.subscribed_channels:
                node.subscribed_channels.remove(args[1])
                node.channel_curr = "general"
                return f"SUCCESS : unsubscribed from channel {args[1]}"
            else: 
                return f"INVALID : was not subscribed to {args[1]}"
        else:
            return "INVALID : cannot unsub to gereral"

    elif args[0] == "switch":
        if args[1] in node.subscribed_channels:
            node.channel_curr = args[1]
            return f"Now on channel {args[1]}"
    return False

if __name__ == '__main__':
    pass