# seat

开工屏 Demo：打开就知道「接着做什么」。

## 这是什么

单页可交互原型（示例数据，不读写真实项目文件）：

- 当前项目与阶段
- **下一步**（只强调一条动作）
- DoD 清单勾选与进度
- Agent 指令一键复制（继续做 / 验收 / 复盘 / 交接）

## 打开 Demo

任选其一：

1. 双击 `index.html`（或浏览器打开本地文件）
2. 静态起服：在本目录运行 `python -m http.server 5173`，访问 `http://127.0.0.1:5173`

无需安装依赖、无需构建。

刷新真实状态：

```bash
python scripts/scan_workspace.py
# 或
python cli.py scan
```

## CLI（P2）

```bash
python cli.py              # 当前项目 + 下一步 + DoD
python cli.py next         # 只打印下一步
python cli.py list         # 全部项目
python cli.py show seat    # 某个项目详情
python cli.py prompt continue|verify|retro|handoff
python cli.py scan         # 重新扫描 STATUS/PLAN
python cli.py which        # 路径
```

Windows 也可用：`seat.cmd list`（等价 `python cli.py list`）。

CLI **只读**（除 `scan` 写 `data/`）；不写回 STATUS。

## 操作

| 操作 | 结果 |
|---|---|
| 勾选 DoD | 进度与计数立即变化 |
| 「复制续做指令」 | 剪贴板得到针对「下一步」的续做 prompt |
| 指令坞按钮 | 复制验收 / 复盘 / 交接等固定指令 |

## 范围说明

Demo **不**包含：CLI、真实 `STATUS.md` 写回、多项目切换、持久化。  
正式版范围见 `docs/compose/spec/seat-demo.md`。

## License

MIT
