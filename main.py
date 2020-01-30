#!/usr/bin/env python

# Copyright (c) <2020>, <Zhuravlev Petr a.k.a. hutado>
# All rights reserved.

"""
System monitor
"""

import curses
import locale
import threading
import psutil



def init_color():
    """
    Initialize color pair (font/background)
    """

    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_YELLOW, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)
    curses.init_pair(7, curses.COLOR_BLUE, -1)
    curses.init_pair(8, curses.COLOR_WHITE, -1)

    color_map = {
        "Cyan": curses.color_pair(1),
        "Red": curses.color_pair(2),
        "Black": curses.color_pair(3),
        "Green": curses.color_pair(4),
        "Yellow": curses.color_pair(5),
        "Magenta": curses.color_pair(6),
        "Blue": curses.color_pair(7),
        "White": curses.color_pair(8)
    }

    return color_map


def initwindow():
    """
    Initialize curses window
    """

    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
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


def cpu_info():

    _main_height, _main_width = win.getmaxyx()

    _title = " CPU Info "

    cpu_window = curses.newwin(int(_main_height/2), _main_width-2, 2, 1)
    cpu_window.border(0)

    _height, _width = cpu_window.getmaxyx()

    _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

    cpu_window.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])

    cpu_info = psutil.cpu_times_percent(percpu=True)
    cpu_count = len(cpu_info)
    start_x = 1
    start_y = 1

    for i, item in enumerate(cpu_info):
        if start_y > cpu_count/2:
            start_x = int(_width/2)
            start_y = 1
        cpu_usage = item[0] or 1
        cpu_str = str(i+1).ljust(3) + '['.ljust(round(((int(_width/2)-13)/100*cpu_usage)), '|').ljust(int(_width/2)-13)\
            + ']' + str(item[0]).rjust(5) + '%'
        cpu_window.addstr(start_y+1, start_x, cpu_str, colors['White'])
        start_y += 1

    cpu_window.refresh()


def print_cpu_info():
    """
    Printing CPU info
    """

    _title = " CPU Info "

    cpu_window = curses.newwin(12, 20, 2, 1)
    cpu_window.border(0)

    _height, _width = cpu_window.getmaxyx()
    _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

    cpu_window.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])

    col = 0

    for i, item in enumerate(psutil.cpu_times_percent(percpu=True)):
        cpu_str = 'ЦП №{} - '.format(i+1)
        cpu_window.addstr(i+1, 1, cpu_str, colors['Magenta'])
        cpu_window.addstr(i+1, len(cpu_str)+1, '{}%'.format(str(item[0])), colors['Cyan'])
        col = i + 2

    cpu = psutil.cpu_percent()

    if cpu > float(60):
        cpu_window.addstr(col+1, 1, 'CPU Usage: {}%'.format(cpu), colors['Red'])
    elif cpu < float(30):
        cpu_window.addstr(col+1, 1, 'CPU Usage: {}%'.format(cpu), colors['Green'])
    else:
        cpu_window.addstr(col+1, 1, 'CPU Usage: {}%'.format(cpu), colors['Yellow'])

    cpu_window.refresh()


def print_mem_info():
    """
    Printing Memory info
    """

    _title = " Memory Info "

    mem_window = curses.newwin(12, 20, 2, 22)
    mem_window.border(0)

    _height, _width = mem_window.getmaxyx()
    _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

    mem_window.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])

    col = 0

    mem_window.addstr(col+1, 1, 'Total: {}GB'.format(round(psutil.virtual_memory().total/1024/1024/1024, 2)), colors['Cyan'])
    mem_window.addstr(col+2, 1, 'Used: {}GB'.format(round(psutil.virtual_memory().used/1024/1024/1024,2)), colors['Cyan'])
    mem_window.addstr(col+3, 1, 'Available: {}GB'.format(round(psutil.virtual_memory().available/1024/1024/1024, 2)), colors['Cyan'])
    mem_window.addstr(col+4, 1, 'Used: {}%'.format(psutil.virtual_memory().percent), colors['Cyan'])

    mem_window.refresh()


def main():
    """
    Main function
    """

    locale.setlocale(locale.LC_ALL, '')

    #Initialize consts
    _key = 'x'
    _title = " System Monitor "
    _footer = "Press Q to exit"

    try:
        global win
        global colors

        win = initwindow()
        colors = init_color()

        win.timeout(1000)

        while _key != ord('q'):
            # Calculate coordinates
            _height, _width = win.getmaxyx()
            _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

            win.erase()
            win.border(0)
            win.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])
            win.addstr(_height-1, _width-len(_footer)-1, _footer[:_width-1], colors['Black'])

            win.refresh()

            cpu_info()
            #print_mem_info()

            _key = win.getch()

    finally:
        clearwindow(win)


if __name__ == '__main__':
    main()
