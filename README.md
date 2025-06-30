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

You can also create a `config.json` file in the same directory (an example is
included) to map specific applications to monitors. The JSON should map process
names to monitor indices, for example:

```json
{
  "vlc.exe": 0,
  "chrome.exe": 1
}
```

If a fullscreen window belongs to a listed process, it will be moved to the
specified monitor.

```bash
python fullscreen_monitor.py 0  # move to the first monitor
```

Use `Ctrl+C` to stop the script.
The tool now scans all visible top-level windows every half second so even
fullscreen windows created in the background (such as the Photos slideshow)
are detected. If a fullscreen window is already on the target monitor when it
is first detected, the script assumes it came from the primary monitor so it
will be moved back there when exiting fullscreen. The script also remembers
each window's original size and position so once fullscreen ends, the window is
restored exactly where it started instead of remaining maximized on the other
monitor. After moving, windows are maximized again to ensure slideshows fully
cover the monitor even when they were created on a different screen. Windows
are not moved back immediately after relocating; a short delay prevents
fullscreen apps from bouncing between monitors while they adjust.
Internally it lists monitors using `win32api.EnumDisplayMonitors(None, None)`.
If you see an error mentioning too many arguments for `EnumDisplayMonitors`, make
sure you are running the latest version of these scripts. The monitor loop also
handles closed windows gracefully so the tool keeps working after a slideshow
window exits fullscreen.

### GUI version

If you prefer a small graphical interface, run `fullscreen_monitor_gui.py`. It
lets you choose the target monitor from a dropdown. After you click Start the
tool periodically checks the active window and moves it if needed. The layout
uses a simple grid with a status indicator so it looks cleaner.

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
程式會每隔半秒掃描所有可見的頂層視窗，
即使像「相片」應用程式的全螢幕投影片這類在背景新開的視窗也能被偵測。
程式在背景使用 `win32api.EnumDisplayMonitors(None, None)` 列出所有螢幕，
若遇到 `EnumDisplayMonitors()` 參數過多的錯誤，請確認已更新到最新版程式。
新增的錯誤處理可以在全螢幕投影片結束後繼續正常監控，不會因為視窗關閉而停止。
若偵測到全螢幕視窗一開始就位於目標螢幕，程式會假設它原本在主要螢幕，
因此在退出全螢幕時會自動移回主要螢幕。程式也會記錄視窗進入全螢幕前的尺寸和位置，
當離開全螢幕後即可恢復原來的狀態，避免停留在另一個螢幕的全螢幕大小。
移動後會再次將視窗最大化，以確保投影片能完全填滿指定的螢幕。
移動後程式會稍候再判斷是否要移回原螢幕，
避免部分應用程式在切換全螢幕時出現來回跳動的情形。

若需要針對特定程式指定顯示器，可在同一目錄建立 `config.json`
檔案（範例檔已附在倉庫中），內容為程式名稱對應到螢幕索引的對照，例如：

```json
{
  "vlc.exe": 0,
  "chrome.exe": 1
}
```

當有設定時，進入全螢幕的視窗若屬於上述程式，就會被移到指定的螢幕。

### 圖形介面版使用方式

若想要簡單的圖形介面，可執行 `fullscreen_monitor_gui.py`。程式會列出所有螢幕
並提供下拉選單供選擇目標螢幕。按下 Start 後，程式會定期檢查作用中視窗
是否全螢幕並視需要移動位置。界面採用網格排版並顯示目前狀態，外觀更加簡潔。

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
