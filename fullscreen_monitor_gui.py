# -*- coding: utf-8 -*-
"""Simple Tkinter UI to control fullscreen window placement on Windows.

This UI allows the user to select the target monitor for fullscreen windows
and start/stop monitoring. It relies on pywin32 and only runs on Windows.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk

import win32api
import win32con
import win32gui

ORIGINAL_MONITORS = {}


def list_monitors():
    """Return list of (hMonitor, info)."""
    monitors = []

    def cb(hmon, hdc, rect, lparam):
        info = win32api.GetMonitorInfo(hmon)
        monitors.append((hmon, info))
        return True

    win32api.EnumDisplayMonitors(None, None, cb, None)
    return monitors


def monitor_index_from_hwnd(hwnd, monitors):
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    for i, (h, _info) in enumerate(monitors):
        if h == hmon:
            return i
    return -1


def is_fullscreen(hwnd):
    """Check if hwnd covers its monitor's bounds."""
    if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
        return False

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    info = win32api.GetMonitorInfo(hmon)
    m_left, m_top, m_right, m_bottom = info["Monitor"]
    return (
        left <= m_left
        and top <= m_top
        and right >= m_right
        and bottom >= m_bottom
    )


def move_to_monitor(hwnd, index, monitors):
    if index >= len(monitors):
        return
    hmon, info = monitors[index]
    m_left, m_top, m_right, m_bottom = info["Monitor"]
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


class FullscreenMonitorApp:
    def __init__(self, root):
        self.root = root
        self.monitors = list_monitors()
        self.target = tk.IntVar(value=1 if len(self.monitors) > 1 else 0)
        self.hooks = []
        self.running = False
        self.thread = None
        self.build_ui()

    def handle_window(self, hwnd):
        if is_fullscreen(hwnd):
            if hwnd not in ORIGINAL_MONITORS:
                ORIGINAL_MONITORS[hwnd] = monitor_index_from_hwnd(hwnd, self.monitors)
            if monitor_index_from_hwnd(hwnd, self.monitors) != self.target.get():
                move_to_monitor(hwnd, self.target.get(), self.monitors)
        else:
            if hwnd in ORIGINAL_MONITORS:
                idx = ORIGINAL_MONITORS.pop(hwnd)
                if idx >= 0:
                    move_to_monitor(hwnd, idx, self.monitors)

    def build_ui(self):
        self.root.title("Fullscreen Monitor Control")
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Target Monitor:").pack(side=tk.LEFT)
        monitor_options = [f"{i}" for i in range(len(self.monitors))]
        self.combo = ttk.Combobox(frm, values=monitor_options, textvariable=self.target, width=5)
        self.combo.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(frm, text="Start", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

    def win_event_proc(self, hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
        if event in (win32con.EVENT_SYSTEM_FOREGROUND, win32con.EVENT_OBJECT_LOCATIONCHANGE):
            self.handle_window(hwnd)

    def message_loop(self):
        while self.running:
            win32gui.PumpWaitingMessages()
            time.sleep(0.1)

    def start(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.hooks = [
            win32gui.SetWinEventHook(
                win32con.EVENT_SYSTEM_FOREGROUND,
                win32con.EVENT_SYSTEM_FOREGROUND,
                0,
                self.win_event_proc,
                0,
                0,
                win32con.WINEVENT_OUTOFCONTEXT,
            ),
            win32gui.SetWinEventHook(
                win32con.EVENT_OBJECT_LOCATIONCHANGE,
                win32con.EVENT_OBJECT_LOCATIONCHANGE,
                0,
                self.win_event_proc,
                0,
                0,
                win32con.WINEVENT_OUTOFCONTEXT,
            ),
        ]
        self.thread = threading.Thread(target=self.message_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        for h in self.hooks:
            win32gui.UnhookWinEvent(h)
        self.hooks = []
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def on_close(self):
        self.stop()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = FullscreenMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
