# 软件工程实验四 面向对象的系统建模

使用 Python 3.10 或更新版本。在本目录运行 `python -m unittest -v` 执行测试，运行 `python state_machines.py sample.txt` 提取示例文件的字符串。

- B1 用 `Tank.sample` 注入当天分钟数、温度、水量及故障和维修事件。通过 `relay_on` 查询继电器。
- B2 用 `ControlPanel.press` 注入单个按键及单调时钟秒数，用 `tick` 单独推进计时。
- B3 默认读 UTF-8，可用 `--encoding` 指定编码。按题设扫描双引号。未闭合引号或悬空反斜杠会返回退出码 1，已经输出的完整字符串保留。
- `diagrams/` 包含 Graphviz DOT 模型和 SVG 图。用 `neato -n2 -Tsvg input.dot -o output.svg` 按固定坐标重新生成。
