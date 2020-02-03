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


def timer(event):
    """
    Timer for thread
    """

    while True:
        event.set()
        time.sleep(1)


def system_info(win, params):
    """
    Window with CPU info
    """

    _height, _width = win.getmaxyx()

    cpu_count = len(params.get('PerCPU'))
    start_x = 1
    start_y = 1

    # Printing info about CPU usage
    for i, item in enumerate(params.get('PerCPU')):
        if start_y > cpu_count/2:
            start_x = int(_width/2)
            start_y = 1
        cpu_usage = item[0] or 1
        part1 = str(i+1).ljust(3)
        part2 = '['.ljust(round(((int(_width/2)-13)/100*cpu_usage)), '|').ljust(int(_width/2)-13) + ']'
        part3 = str(item[0]).rjust(5) + '%'
        win.addstr(start_y+1, start_x+1, part1, colors['Cyan'])
        if item[0] < float(30):
            win.addstr(start_y+1, start_x+1+len(part1), part2, colors['White'])
            win.addstr(start_y+1, start_x+1+len(part1+part2), part3, colors['Green'])
        elif item[0] > float(70):
            win.addstr(start_y+1, start_x+1+len(part1), part2, colors['Red'])
            win.addstr(start_y+1, start_x+1+len(part1+part2), part3, colors['Red'])
        else:
            win.addstr(start_y+1, start_x+1+len(part1), part2, colors['White'])
            win.addstr(start_y+1, start_x+1+len(part1+part2), part3, colors['Yellow'])
        start_y += 1

    strings = ['CPU Usage', 'Used Mem', 'Used Swp']
    for i, item in enumerate(strings):
        part1 = (item + ':').ljust(12)
        part2 = '{}%'.format(params.get(item)).rjust(7)
        win.addstr(start_y+i+2, 2, part1, colors['Cyan'])
        if params.get(item) < float(30):
            win.addstr(start_y+i+2, len(part1), part2, colors['Green'])
        elif params.get(item) > float(70):
            win.addstr(start_y+i+2, len(part1), part2, colors['Red'])
        else:
            win.addstr(start_y+i+2, len(part1), part2, colors['Yellow'])

    part1 = 'Uptime: '
    part2 = params.get('Uptime')
    win.addstr(start_y+2, start_x+1, part1, colors['Cyan'])
    win.addstr(start_y+2, start_x+1+len(part1), part2[:int(_width/2)-len(part1)-2], colors['White'])

    part1 = 'Free Space: '
    part2 = str(round(params.get('FreeSpace'), 2)) + 'Gb'
    win.addstr(start_y+3, start_x+1, part1, colors['Cyan'])
    win.addstr(start_y+3, start_x+1+len(part1), part2[:int(_width/2)-len(part1)-2], colors['White'])

    win.refresh()


def get_uptime():
    """
    Getting uptime
    """

    with open('/proc/uptime', 'r') as file:
        up = float(file.readline().split()[0])

    parts = []

    days, up = int(up // 86400), up % 86400
    if days:
        parts.append('%d day%s ' % (days, 's' if days != 1 else ''))

    hours, up = int(up // 3600), up % 3600
    if hours < 10:
        parts.append('{}:'.format('0' + str(hours)))
    else:
        parts.append('{}:'.format(hours))

    minutes, up = int(up // 60), up % 60
    if minutes < 10:
        parts.append('{}:'.format('0' + str(minutes)))
    else:
        parts.append('{}:'.format(minutes))

    if up < 10:
        parts.append('{}'.format('0' + str(int(up))))
    else:
        parts.append('{}'.format(int(up)))

    return ''.join(parts)


def get_params():
    """
    Returning System Info
    """

    return {
        'PerCPU': psutil.cpu_times_percent(percpu=True),
        'CPU Usage': psutil.cpu_times_percent()[0],
        'Used Mem': psutil.virtual_memory().percent + 10,
        'Used Swp': psutil.swap_memory().percent,
        'Uptime': get_uptime(),
        'FreeSpace': psutil.disk_usage('/')[2]/1000/1000/1000
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
        win.timeout(1000)
        colors = init_color()

        # Creating thread with timer
        event = threading.Event()
        cpu = threading.Thread(target=timer, args=(event,))
        cpu.setDaemon(True)
        cpu.start()

        # Main cycle
        while _key not in [ord('q'), ord('Q')]:
            win.erase()
            win.border(0)
            # Calculate coordinates for title and footer
            _height, _width = win.getmaxyx()
            _start_x_title = int((_width // 2) - (len(_title) // 2) - len(_title) % 2)
            win.addstr(0, _start_x_title, _title[:_width-1], colors['Black'])
            win.addstr(_height-1, _width-len(_footer)-1, _footer[:_width-1], colors['Black'])
            win.refresh()

            # Check event for getting params
            if event.is_set():
                event.clear()
                params = get_params()

            system_info(win, params)

            _key = win.getch()
    finally:
        clearwindow(win)


if __name__ == '__main__':
    main()
