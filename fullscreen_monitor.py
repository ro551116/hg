# -*- coding: utf-8 -*-
"""Simple tool to move fullscreen windows to a chosen monitor.

This script polls the active window every half second. If that window is in
fullscreen mode, it will be moved to the specified monitor. When the window
leaves fullscreen, it is moved back to its original monitor.

Usage:
    python fullscreen_monitor.py [target_monitor_index]

The default target monitor index is 1 (the second monitor). The script requires
pywin32 and only works on Windows.
"""

import sys
import time

try:
    import win32api
    import win32con
    import win32gui
except ImportError as exc:
    raise SystemExit(
        "This script requires the 'pywin32' package. "
        "Install it with 'pip install pywin32' on Windows."
    ) from exc

TARGET_MONITOR = 1
if len(sys.argv) > 1:
    try:
        TARGET_MONITOR = int(sys.argv[1])
    except ValueError:
        pass

# List monitor handles and their info once at startup
MONITORS = []
for hmon, _hdc, _rect in win32api.EnumDisplayMonitors(None, None):
    info = win32api.GetMonitorInfo(hmon)
    MONITORS.append((hmon, info))

# Track each moved window's original monitor
ORIGINAL_MONITOR = {}


def monitor_index_from_hwnd(hwnd):
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    for i, (h, _info) in enumerate(MONITORS):
        if h == hmon:
            return i
    return -1


def is_fullscreen(hwnd):
    """Return True if the window covers its entire monitor."""
    try:
        if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            return False
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(hmon)
        m_left, m_top, m_right, m_bottom = info["Monitor"]
        return left == m_left and top == m_top and right == m_right and bottom == m_bottom
    except win32gui.error:
        return False


def move_to_monitor(hwnd, index):
    if index < 0 or index >= len(MONITORS):
        return
    hmon, info = MONITORS[index]
    m_left, m_top, m_right, m_bottom = info["Monitor"]
    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,
        m_left,
        m_top,
        m_right - m_left,
        m_bottom - m_top,
        win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED,
    )
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
    except win32gui.error:
        pass


while True:
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            if is_fullscreen(hwnd):
                if hwnd not in ORIGINAL_MONITOR:
                    ORIGINAL_MONITOR[hwnd] = monitor_index_from_hwnd(hwnd)
                    if ORIGINAL_MONITOR[hwnd] != TARGET_MONITOR:
                        move_to_monitor(hwnd, TARGET_MONITOR)
            else:
                if hwnd in ORIGINAL_MONITOR:
                    idx = ORIGINAL_MONITOR.pop(hwnd)
                    if idx >= 0:
                        move_to_monitor(hwnd, idx)
    except win32gui.error:
        pass
    time.sleep(0.5)
