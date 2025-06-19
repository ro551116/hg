# Fullscreen Monitor Control Tool

This repository includes sample scripts that show how to detect when a window
enters fullscreen mode on Windows and automatically move it to a desired
monitor. They rely on the `pywin32` package.

## Requirements

* Python 3
* [pywin32](https://pypi.org/project/pywin32/) (only available on Windows)

Install the dependency with:

```bash
pip install pywin32
```
若執行程式時出現 `ModuleNotFoundError: No module named 'win32api'`，
請確認目前使用的 Python 環境已安裝 `pywin32`。
If you run the script and see `ModuleNotFoundError: No module named 'win32api'`,
make sure `pywin32` is installed for the Python interpreter you are using.

## Usage

Run the script from a command prompt. By default it moves fullscreen windows to
the second monitor (index `1`). When the window leaves fullscreen it is
returned to its original monitor. You can pass a different monitor index as a
command-line argument.

```bash
python fullscreen_monitor.py 0  # move to the first monitor
```

Use `Ctrl+C` to stop the script.

### GUI version

If you prefer a small graphical interface, run `fullscreen_monitor_gui.py`. It
lets you choose the target monitor from a dropdown and start/stop monitoring.

```bash
python fullscreen_monitor_gui.py
```







### Creating an executable

If you want to run the tool without needing Python installed, you can package
it with [PyInstaller](https://pyinstaller.org/). Install PyInstaller and then
build a single-file executable like this:

```bash
pip install pyinstaller
pyinstaller --onefile fullscreen_monitor.py
```

The resulting `fullscreen_monitor.exe` will be found in the `dist` directory.

## 中文說明

此專案提供兩個範例程式，示範如何在 Windows 上偵測視窗進入全螢幕模式
並自動將其移至指定的螢幕。兩個檔案皆需要安裝 `pywin32` 套件才能運作。

### 需求套件

- Python 3
- [pywin32](https://pypi.org/project/pywin32/)（僅支援 Windows）

安裝方式如下：

```bash
pip install pywin32
```
若執行程式時出現 `ModuleNotFoundError: No module named 'win32api'`，
請確認使用的 Python 環境已安裝 `pywin32`。

### 指令列版使用方式

在命令提示字元中執行 `fullscreen_monitor.py`。預設會把全螢幕視窗移到第二個
螢幕（索引值 `1`），離開全螢幕後會自動移回原本的螢幕，也可以在啟動時傳入
其他索引值來指定目標螢幕：

```bash
python fullscreen_monitor.py 0  # 移到第一個螢幕
```

按下 `Ctrl+C` 可停止執行。

### 圖形介面版使用方式

若想要簡單的圖形介面，可執行 `fullscreen_monitor_gui.py`。程式會列出所有螢幕
並提供下拉選單供選擇目標螢幕，按下 Start 後就會開始監聽並移動視窗。

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

完成後的 `fullscreen_monitor.exe` 會出現在 `dist` 目錄下。
