# -*- coding: utf-8 -*-
"""Basic Tkinter GUI to select a target monitor for fullscreen windows.

This version polls the foreground window every half second and moves it to the
selected monitor when it enters fullscreen. When the window exits fullscreen it
returns to its original monitor. The script requires pywin32 and only works on
Windows.
"""

import threading
import time
import tkinter as tk
from tkinter import ttk

try:
    import win32api
    import win32con
    import win32gui
except ImportError as exc:
    raise SystemExit(
        "This script requires the 'pywin32' package. "
        "Install it with 'pip install pywin32' on Windows."
    ) from exc


def list_monitors():
    monitors = []
    for hmon, _hdc, _rect in win32api.EnumDisplayMonitors(None, None):
        info = win32api.GetMonitorInfo(hmon)
        monitors.append((hmon, info))
    return monitors


class FullscreenMonitorApp:
    def __init__(self, root):
        self.root = root
        self.monitors = list_monitors()
        self.target = tk.IntVar(value=1 if len(self.monitors) > 1 else 0)
        self.original = {}
        self.running = False
        self.thread = None
        self.build_ui()

    def monitor_index(self, hwnd):
        hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        for i, (h, _info) in enumerate(self.monitors):
            if h == hmon:
                return i
        return -1

    def is_fullscreen(self, hwnd):
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

    def move_to_monitor(self, hwnd, index):
        if index < 0 or index >= len(self.monitors):
            return
        hmon, info = self.monitors[index]
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

    def monitor_loop(self):
        while self.running:
            try:
                hwnd = win32gui.GetForegroundWindow()
                if hwnd:
                    if self.is_fullscreen(hwnd):
                        if hwnd not in self.original:
                            self.original[hwnd] = self.monitor_index(hwnd)
                            if self.original[hwnd] != self.target.get():
                                self.move_to_monitor(hwnd, self.target.get())
                    else:
                        if hwnd in self.original:
                            idx = self.original.pop(hwnd)
                            if idx >= 0:
                                self.move_to_monitor(hwnd, idx)
            except win32gui.error:
                pass
            time.sleep(0.5)

    def start(self):
        if self.running:
            return
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status.config(text="Monitoring...")
        self.thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status.config(text="Stopped")

    def on_close(self):
        self.stop()
        self.root.destroy()

    def build_ui(self):
        self.root.title("Fullscreen Monitor Control")
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Target Monitor:").grid(row=0, column=0, sticky="e")
        options = [f"{i}" for i in range(len(self.monitors))]
        self.combo = ttk.Combobox(frm, values=options, textvariable=self.target, width=5, state="readonly")
        self.combo.grid(row=0, column=1, sticky="w", padx=5)

        self.start_btn = ttk.Button(frm, text="Start", command=self.start)
        self.start_btn.grid(row=1, column=0, pady=10, sticky="e")
        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=1, column=1, pady=10, sticky="w")

        self.status = ttk.Label(frm, text="Stopped")
        self.status.grid(row=2, column=0, columnspan=2)


def main():
    root = tk.Tk()
    app = FullscreenMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
