# -*- coding: utf-8 -*-
"""Simple Tkinter UI to control fullscreen window placement on Windows.

This UI allows the user to select the target monitor for fullscreen windows
and start/stop monitoring. It relies on pywin32 and only runs on Windows.
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

# Track each moved window's original monitor index and placement so we can
# restore it once it leaves fullscreen.
ORIGINAL_WINDOWS = {}


def list_monitors():
    """Return list of (hMonitor, info)."""
    monitors = []
    # explicit arguments avoid the callback-style API that expects four params
    for hmon, _hdc, _rect in win32api.EnumDisplayMonitors(None, None):
        info = win32api.GetMonitorInfo(hmon)
        monitors.append((hmon, info))
    return monitors


def primary_monitor_index(monitors):
    for i, (_h, info) in enumerate(monitors):
        if info.get("Flags", 0) & win32con.MONITORINFOF_PRIMARY:
            return i
    return 0


def monitor_index_from_hwnd(hwnd, monitors):
    hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
    for i, (h, _info) in enumerate(monitors):
        if h == hmon:
            return i
    return -1


def is_fullscreen(hwnd):
    """Return True if the window appears to cover the whole monitor."""
    try:
        if not win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            return False

        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        hmon = win32api.MonitorFromWindow(hwnd, win32con.MONITOR_DEFAULTTONEAREST)
        info = win32api.GetMonitorInfo(hmon)
        m_left, m_top, m_right, m_bottom = info["Monitor"]
        margin = 2
        return (
            left <= m_left + margin
            and top <= m_top + margin
            and right >= m_right - margin
            and bottom >= m_bottom - margin
        )
    except win32gui.error:
        return False


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
        self.primary = primary_monitor_index(self.monitors)
        self.target = tk.IntVar(value=1 if len(self.monitors) > 1 else 0)
        self.running = False
        self.thread = None
        self.build_ui()

    def handle_window(self, hwnd):
        if is_fullscreen(hwnd):
            if hwnd not in ORIGINAL_WINDOWS:
                orig = monitor_index_from_hwnd(hwnd, self.monitors)
                if orig == self.target.get():
                    orig = self.primary
                placement = win32gui.GetWindowPlacement(hwnd)
                ORIGINAL_WINDOWS[hwnd] = (orig, placement)
            if monitor_index_from_hwnd(hwnd, self.monitors) != self.target.get():
                move_to_monitor(hwnd, self.target.get(), self.monitors)
        else:
            if hwnd in ORIGINAL_WINDOWS:
                idx, placement = ORIGINAL_WINDOWS.pop(hwnd)
                if idx >= 0:
                    move_to_monitor(hwnd, idx, self.monitors)
                try:
                    win32gui.SetWindowPlacement(hwnd, placement)
                except win32gui.error:
                    pass

    def build_ui(self):
        self.root.title("Fullscreen Monitor Control")
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Fullscreen Monitor Control", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        ttk.Label(frm, text="Target Monitor:").grid(row=1, column=0, sticky="e")
        monitor_options = [f"{i}" for i in range(len(self.monitors))]
        self.combo = ttk.Combobox(frm, values=monitor_options, textvariable=self.target, width=5, state="readonly")
        self.combo.grid(row=1, column=1, sticky="w", padx=5)

        self.start_btn = ttk.Button(frm, text="Start", command=self.start)
        self.start_btn.grid(row=2, column=0, pady=10, sticky="e")
        self.stop_btn = ttk.Button(frm, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=2, column=1, pady=10, sticky="w")

        self.status = ttk.Label(frm, text="Stopped")
        self.status.grid(row=3, column=0, columnspan=2)

    def monitor_loop(self):
        while self.running:
            def cb(hwnd, _):
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        self.handle_window(hwnd)
                except win32gui.error:
                    pass
            win32gui.EnumWindows(cb, None)
            for wh in list(ORIGINAL_WINDOWS.keys()):
                try:
                    if not win32gui.IsWindow(wh):
                        ORIGINAL_WINDOWS.pop(wh, None)
                        continue
                    if not is_fullscreen(wh):
                        idx, placement = ORIGINAL_WINDOWS.pop(wh)
                        if idx >= 0:
                            move_to_monitor(wh, idx, self.monitors)
                        try:
                            win32gui.SetWindowPlacement(wh, placement)
                        except win32gui.error:
                            pass
                except win32gui.error:
                    ORIGINAL_WINDOWS.pop(wh, None)
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


def main():
    root = tk.Tk()
    app = FullscreenMonitorApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
