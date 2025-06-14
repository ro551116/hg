# -*- coding: utf-8 -*-
"""
Example tool to monitor windows entering fullscreen and move them to a
specific monitor. This script requires pywin32 and only works on Windows.

Usage:
    python fullscreen_monitor.py [target_monitor_index]

By default, the script moves fullscreen windows to monitor index 1 (the second
monitor). Monitor indices follow the order returned by EnumDisplayMonitors.
"""

import sys
import time
import win32api
import win32con
import win32gui

# Map of window handle to its original monitor index when moved
ORIGINAL_MONITORS = {}

TARGET_MONITOR = 1

if len(sys.argv) > 1:
    try:
        TARGET_MONITOR = int(sys.argv[1])
    except ValueError:
        pass


def list_monitors():
    """Return a list of (hMonitor, info) for all monitors."""
    mons = []
    def callback(hMon, hdc, lprc, lparam):
        info = win32api.GetMonitorInfo(hMon)
        mons.append((hMon, info))
        return True
    win32api.EnumDisplayMonitors(None, None, callback, None)
    return mons


MONITORS = list_monitors()


def monitor_index_from_hwnd(hwnd):
    """Return the index of the monitor a window is on."""
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    for i, (h, _info) in enumerate(MONITORS):
        if h == hmon:
            return i
    return -1


def is_fullscreen(hwnd):
    """Check if a window covers its monitor's work area."""
    if not win32gui.IsWindowVisible(hwnd):
        return False
    if win32gui.IsIconic(hwnd):
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    info = win32api.GetMonitorInfo(hmon)
    m_left, m_top, m_right, m_bottom = info['Monitor']
    return (left <= m_left and top <= m_top and right >= m_right and bottom >= m_bottom)

def move_to_monitor(hwnd, index):
    """Move the given window to the specified monitor index."""
    if index >= len(MONITORS):
        return
    hMonitor, info = MONITORS[index]
    m_left, m_top, m_right, m_bottom = info['Monitor']
    width = m_right - m_left
    height = m_bottom - m_top
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,
        m_left,
        m_top,
        width,
        height,
        win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED,
    )


def handle_window(hwnd):
    if is_fullscreen(hwnd):
        if hwnd not in ORIGINAL_MONITORS:
            ORIGINAL_MONITORS[hwnd] = monitor_index_from_hwnd(hwnd)
        if monitor_index_from_hwnd(hwnd) != TARGET_MONITOR:
            move_to_monitor(hwnd, TARGET_MONITOR)
    else:
        if hwnd in ORIGINAL_MONITORS:
            orig_idx = ORIGINAL_MONITORS.pop(hwnd)
            if orig_idx >= 0:
                move_to_monitor(hwnd, orig_idx)


def win_event_proc(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
    if event in (win32con.EVENT_SYSTEM_FOREGROUND, win32con.EVENT_OBJECT_LOCATIONCHANGE):
        handle_window(hwnd)


if __name__ == "__main__":
    hooks = [
        win32gui.SetWinEventHook(
            win32con.EVENT_SYSTEM_FOREGROUND,
            win32con.EVENT_SYSTEM_FOREGROUND,
            0,
            win_event_proc,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT,
        ),
        win32gui.SetWinEventHook(
            win32con.EVENT_OBJECT_LOCATIONCHANGE,
            win32con.EVENT_OBJECT_LOCATIONCHANGE,
            0,
            win_event_proc,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT,
        ),
    ]

    try:
        while True:
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        for h in hooks:
            win32gui.UnhookWinEvent(h)
