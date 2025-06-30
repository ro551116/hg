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
import os
import json
try:
    import win32api
    import win32con
    import win32gui
    import win32process
except ImportError as exc:
    raise SystemExit(
        "This script requires the 'pywin32' package. "
        "Install it with 'pip install pywin32' on Windows."
    ) from exc

# Map of window handle to its original monitor index when moved
ORIGINAL_MONITORS = {}

TARGET_MONITOR = 1
APP_MONITORS = {}

if len(sys.argv) > 1:
    try:
        TARGET_MONITOR = int(sys.argv[1])
    except ValueError:
        pass

# Load optional config mapping process names to monitor indices
if os.path.exists("config.json"):
    try:
        with open("config.json", "r", encoding="utf-8") as fh:
            APP_MONITORS = {
                k.lower(): int(v) for k, v in json.load(fh).items()
            }
    except Exception:
        APP_MONITORS = {}


def list_monitors():
    """Return a list of (hMonitor, info) for all monitors."""
    mons = []
    # call EnumDisplayMonitors with two parameters (HDC and clip rect)
    # to avoid the legacy callback style that requires four arguments
    for hMon, _hdc, _rect in win32api.EnumDisplayMonitors(None, None):
        info = win32api.GetMonitorInfo(hMon)
        mons.append((hMon, info))
    return mons


MONITORS = list_monitors()


def get_primary_monitor_index():
    """Return the index of the primary monitor."""
    for i, (_h, info) in enumerate(MONITORS):
        if info.get("Flags", 0) & win32con.MONITORINFOF_PRIMARY:
            return i
    return 0


PRIMARY_MONITOR = get_primary_monitor_index()


def monitor_index_from_hwnd(hwnd):
    """Return the index of the monitor a window is on."""
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    for i, (h, _info) in enumerate(MONITORS):
        if h == hmon:
            return i
    return -1


def is_fullscreen(hwnd):
    """Return True if the window appears to occupy its entire monitor."""
    try:
        if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            return False

        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(hmon)
        m_left, m_top, m_right, m_bottom = info["Monitor"]
        margin = 2  # tolerate small offsets used by some apps like Photos
        return (
            left <= m_left + margin
            and top <= m_top + margin
            and right >= m_right - margin
            and bottom >= m_bottom - margin
        )
    except win32gui.error:
        return False


def get_process_name(hwnd):
    """Return the lowercase process name for the given window."""
    try:
        _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        hproc = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
            False,
            pid,
        )
        try:
            exe = win32process.GetModuleFileNameEx(hproc, 0)
        finally:
            win32api.CloseHandle(hproc)
        return os.path.basename(exe).lower()
    except Exception:
        return ""

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
    target = TARGET_MONITOR
    name = get_process_name(hwnd)
    if name in APP_MONITORS:
        target = APP_MONITORS[name]

    if is_fullscreen(hwnd):
        if hwnd not in ORIGINAL_MONITORS:
            orig = monitor_index_from_hwnd(hwnd)
            if orig == target:
                orig = PRIMARY_MONITOR
            ORIGINAL_MONITORS[hwnd] = orig
        if monitor_index_from_hwnd(hwnd) != target:
            move_to_monitor(hwnd, target)
    else:
        if hwnd in ORIGINAL_MONITORS:
            orig_idx = ORIGINAL_MONITORS.pop(hwnd)
            if orig_idx >= 0:
                move_to_monitor(hwnd, orig_idx)


def restore_windows():
    """Return windows that were moved back to their original monitor."""
    for hwnd in list(ORIGINAL_MONITORS.keys()):
        try:
            if not win32gui.IsWindow(hwnd):
                ORIGINAL_MONITORS.pop(hwnd, None)
                continue
            if not is_fullscreen(hwnd):
                idx = ORIGINAL_MONITORS.pop(hwnd)
                if idx >= 0:
                    move_to_monitor(hwnd, idx)
        except win32gui.error:
            ORIGINAL_MONITORS.pop(hwnd, None)


def check_all_windows():
    """Enumerate top-level windows and handle those that are fullscreen."""
    def callback(hwnd, _extra):
        try:
            if win32gui.IsWindowVisible(hwnd):
                handle_window(hwnd)
        except win32gui.error:
            pass
    win32gui.EnumWindows(callback, None)


if __name__ == "__main__":
    try:
        while True:
            check_all_windows()
            restore_windows()
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
