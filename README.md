# Fullscreen Monitor Control Tool

This repository contains two sample Python scripts that move fullscreen windows
to a chosen monitor on Windows. They rely on the `pywin32` package.

## Requirements

* Python 3
* [pywin32](https://pypi.org/project/pywin32/) (Windows only)

Install the dependency with:

```bash
pip install pywin32
```
If you run the script and see `ModuleNotFoundError: No module named 'win32api'`,
make sure `pywin32` is installed for the interpreter you are using.

## Usage

Run `fullscreen_monitor.py` from a command prompt. By default it moves the
foreground window to the second monitor (index `1`) whenever that window goes
fullscreen. When the window leaves fullscreen it is moved back to its original
monitor. You can pass a different monitor index on the command line.

```bash
python fullscreen_monitor.py 0  # move fullscreen windows to monitor 0
```

Press `Ctrl+C` to stop the script.

### GUI version

`fullscreen_monitor_gui.py` provides a simple Tkinter interface to choose the
target monitor and start or stop monitoring. It performs the same foreground
window check every half second.

```bash
python fullscreen_monitor_gui.py
```

### Creating an executable

If you want to run the tool without Python installed, package it with
[PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile fullscreen_monitor.py
```

The resulting `fullscreen_monitor.exe` will be available in the `dist` folder.

## 中文說明

此專案提供兩個 Python 範例，示範如何在 Windows 上將全螢幕視窗移動到指定
螢幕。程式需要安裝 `pywin32` 套件。

### 需求套件

- Python 3
- [pywin32](https://pypi.org/project/pywin32/)（僅支援 Windows）

安裝方式：

```bash
pip install pywin32
```
若執行程式時出現 `ModuleNotFoundError: No module named 'win32api'`，
請確認使用的 Python 環境已安裝 `pywin32`。

### 指令列版使用方式

在命令提示字元中執行 `fullscreen_monitor.py`。預設會將進入全螢幕的
作用中視窗移到第二個螢幕（索引值 `1`），離開全螢幕後會移回原本的螢幕。
也可以在啟動時傳入其他索引值指定目標螢幕：

```bash
python fullscreen_monitor.py 0  # 移到第一個螢幕
```

按下 `Ctrl+C` 可停止執行。

### 圖形介面版使用方式

若想要簡單的圖形介面，可執行 `fullscreen_monitor_gui.py`。程式會列出所有
螢幕並提供下拉選單供選擇目標螢幕。按下 Start 後，程式會定期檢查作用中
視窗是否全螢幕並視需要移動位置。

```bash
python fullscreen_monitor_gui.py
```

### 建立可執行檔

若希望在沒有 Python 環境的電腦上直接執行，可使用
[PyInstaller](https://pyinstaller.org/) 打包成單一執行檔：

```bash
pip install pyinstaller
pyinstaller --onefile fullscreen_monitor.py
```

打包完成的 `fullscreen_monitor.exe` 會出現在 `dist` 目錄下。
