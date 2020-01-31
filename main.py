#!/usr/bin/env python

# Copyright (c) <2020>, <Zhuravlev Petr a.k.a. hutado>
# All rights reserved.

"""
System monitor
"""

import curses
import locale
import threading
import time
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


def timer(te):
    while True:
        te.set()
        time.sleep(1)


def system_info(win, params):
    """
    Window with CPU info
    """

    _main_height, _main_width = win.getmaxyx()

    _title = " CPU Info "

    system_window = curses.newwin(int(_main_height/2), _main_width-2, 2, 1)
    system_window.border(0)

    _height, _width = system_window.getmaxyx()

    _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

    system_window.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])

    #cpu_list = psutil.cpu_times_percent(percpu=True)
    cpu_count = len(params.get('PerCPU'))
    start_x = 1
    start_y = 1

    for i, item in enumerate(params.get('PerCPU')):
        if start_y > cpu_count/2:
            start_x = int(_width/2)
            start_y = 1
        cpu_usage = item[0] or 1
        cpu_str = str(i+1).ljust(3) + '['.ljust(round(((int(_width/2)-13)/100*cpu_usage)), '|').ljust(int(_width/2)-13)\
            + ']' + str(item[0]).rjust(5) + '%'
        system_window.addstr(start_y+1, start_x, cpu_str, colors['White'])
        start_y += 1

    cpu_1 = 'CPU Usage:'.ljust(11)
    cpu_2 = '{}%'.format(params.get('CPUUsage')).rjust(8)
    system_window.addstr(start_y+2, 1, cpu_1, colors['Cyan'])
    system_window.addstr(start_y+2, len(cpu_1), cpu_2, colors['White'])

    tmem_1 = 'Total Mem:'.ljust(11)
    tmem_2 = '{}GB'.format(params.get('TotalMem')).rjust(8)
    system_window.addstr(start_y+3, 1, tmem_1, colors['Cyan'])
    system_window.addstr(start_y+3, len(tmem_1), tmem_2, colors['White'])

    umem_1 = 'Used Mem:'.ljust(11)
    umem_2 = '{}%'.format(params.get('UsedMem')).rjust(8)
    system_window.addstr(start_y+4, 1, umem_1, colors['Cyan'])
    system_window.addstr(start_y+4, len(umem_1), umem_2, colors['White'])

    swp_1 = 'Used Swp:'.ljust(11)
    swp_2 = '{}%'.format(params.get('UsedSwp')).rjust(8)
    system_window.addstr(start_y+5, 1, swp_1, colors['Cyan'])
    system_window.addstr(start_y+5, len(swp_1), swp_2, colors['White'])

    system_window.refresh()


def get_params():
    """
    Returning System Info
    """

    return {
        'PerCPU': psutil.cpu_times_percent(percpu=True),
        'CPUUsage': psutil.cpu_times_percent()[0],
        'TotalMem': round(psutil.virtual_memory().total/1024/1024/1024, 2),
        'UsedMem': psutil.virtual_memory().percent + 10,
        'UsedSwp': psutil.swap_memory().percent
    }



def main():
    """
    Main function
    """

    locale.setlocale(locale.LC_ALL, '')

    #Initialize consts
    _key = 'x'
    _title = " System Monitor "
    _footer = "Press Q to exit"
    params = {}

    try:
        global colors

        win = initwindow()
        colors = init_color()
        win.timeout(1000)

        te = threading.Event()
        cpu = threading.Thread(target=timer, args=(te,))
        cpu.setDaemon(True)
        cpu.start()

        while _key != ord('q'):
            # Calculate coordinates
            _height, _width = win.getmaxyx()
            _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)

            win.erase()
            win.border(0)
            win.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])
            win.addstr(_height-1, _width-len(_footer)-1, _footer[:_width-1], colors['Black'])

            win.refresh()

            if te.is_set():
                te.clear()
                params = get_params()

            system_info(win, params)

            _key = win.getch()

    finally:
        clearwindow(win)


if __name__ == '__main__':
    main()
