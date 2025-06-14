# Text-driven Blender Generator

This repository contains Python scripts that allow you to create 3D scenes in Blender using plain text instructions, simple diagrams, or natural language with the help of a language model.

## 中文說明

本專案提供多種方式在 Blender 中產生 3D 場景：

1. **文字指令**：撰寫指令檔後以 `text_to_blender.py` 產生立方體、球體及圓柱等物件。
2. **Graphviz 圖形**：使用 `diagram_to_blender.py` 將 `.dot` 檔轉成節點與邊的 3D 模型。
3. **自然語言**：搭配 OpenAI API，`lm_to_blender.py` 可把自由文字轉成可供 `text_to_blender.py` 執行的指令。

## Usage

### Text instructions

1. Prepare a text file with one instruction per line. Supported commands:
   - `cube size=<number> location=x,y,z color=r,g,b`
   - `sphere radius=<number> location=x,y,z color=r,g,b`
   - `cylinder radius=<number> depth=<number> location=x,y,z color=r,g,b`

2. Run Blender in background mode with the script:

```
blender --background --python text_to_blender.py -- <your_instructions.txt>
```

The script will parse the instructions and create the corresponding objects with basic materials.

## Example

```
cube size=2 location=0,0,0 color=1,0,0
sphere radius=1 location=3,0,0 color=0,0,1
```

Running the above will produce a red cube at the origin and a blue sphere at (3,0,0).

### Diagram input

You can generate 3D graphs from a Graphviz `.dot` file:

```
blender --background --python diagram_to_blender.py -- <graph.dot>
```

Nodes will be visualized as spheres and edges as cylinders. If node positions
are not specified in the dot file, a spring layout will be used.

### Natural language with a language model

With an OpenAI API key configured, you can let a language model translate free
text into commands for `text_to_blender.py`:

```
blender --background --python lm_to_blender.py -- "a big red cube next to a small blue sphere"
```

The script will call the model to convert the prompt into structured commands
and then create the objects in Blender.

## Dependencies
Install the required libraries with:
```bash
pip install -r requirements.txt
```
These scripts must be run inside Blender as shown in the usage examples.

## 依賴與測試
使用 `pip install -r requirements.txt` 來安裝所需套件，然後執行：
```bash
python3 -m py_compile text_to_blender.py diagram_to_blender.py lm_to_blender.py
```
確保所有腳本都能正常載入。


