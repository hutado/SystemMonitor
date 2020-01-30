#!/usr/bin/env python

"""
System monitor
"""

import os
import curses
import psutil


def init_color():
    """
    Initialize color pair (font/background)
    """

    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)


def initwindow():
    """
    Initialize curses window
    """

    stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(1)

    return stdscr


def clearwindow(stdscr):
    """
    Clearing window after exit
    """

    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()


def print_cpu_info(win):
    """
    Printing CPU info
    """

    col = 0

    for i, item in enumerate(psutil.cpu_times_percent(percpu=True)):
        win.addstr(i+1, 1, 'ЦП №{} - {}%'.format(i+1, str(item[0])), curses.color_pair(1))
        col = i + 2

    cpu = psutil.cpu_percent()

    if cpu > float(60):
        win.addstr(col, 1, 'CPU Usage: {}%'.format(cpu), curses.color_pair(2))
    elif cpu < float(30):
        win.addstr(col, 1, 'CPU Usage: {}%'.format(cpu), curses.color_pair(4))
    else:
        win.addstr(col, 1, 'CPU Usage: {}%'.format(cpu), curses.color_pair(5))

    win.refresh()


def main():
    """
    Main function
    """

    key = 'x'
    title = " System Monitor "
    footer = "Press Q to exit"

    try:
        win = initwindow()
        init_color()
        win.timeout(1000)
        while key != ord('q'):
            _height, _width = win.getmaxyx()
            win.erase()
            win.border(0)
            win.addstr(0, 1, title[:_width-1], curses.color_pair(3))
            win.addstr(_height-1, _width-len(footer)-1, footer[:_width-1], curses.color_pair(3))
            print_cpu_info(win)
            key = win.getch()
    finally:
        clearwindow(win)


if __name__ == '__main__':
    main()
