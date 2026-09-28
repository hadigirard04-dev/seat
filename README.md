# seat

开工屏：打开就知道「接着做什么」。

面向多 Agent、多 GitHub 小项目切换的开发者：一页看清当前项目、下一步、DoD 进度，一键复制续做 / 验收 / 复盘 / 交接指令；配套 CLI 可读写真实 `STATUS.md` 与 `docs/log.md`。

## 功能

- **开工屏 UI**（V1 Ink）：当前项目、阶段、下一步、风险、DoD 清单
- **多项目切换**：扫描 `projects/*/STATUS.md` 后可切换
- **时间线**：读取 `docs/log.md`
- **Git 集成**：显示分支与近期提交
- **DoD 本地持久化**：勾选写入 `localStorage`（按项目隔离）
- **Agent 指令坞**：继续做 / 验收 / 复盘 / 交接，一键复制
- **写回**：追加 log、导出 `writeback.json`、复制 apply 命令
- **CLI**：`status` / `next` / `list` / `show` / `prompt` / `scan` / 写回

## 快速开始

### 打开页面

1. 双击 `index.html`
2. 或本地起服：`python -m http.server 5173` → `http://127.0.0.1:5173`
3. 在线：GitHub Pages（见仓库 About）

无需构建、无前端依赖。

### 刷新真实状态

```bash
python scripts/scan_workspace.py
# 或
python cli.py scan
```

### CLI

```bash
python cli.py              # 当前项目 + 下一步 + DoD
python cli.py next         # 只打印下一步
python cli.py list         # 全部项目
python cli.py show seat    # 某个项目详情
python cli.py prompt continue|verify|retro|handoff
python cli.py scan         # 重新扫描 STATUS/PLAN
python cli.py which        # 路径
```

Windows：`seat.cmd list`（等价 `python cli.py list`）。

### 写回

```bash
python cli.py next "新的下一步"     # 写 STATUS 下一步
python cli.py log "今天做完了 X"    # 追加 docs/log.md
python cli.py check "T4"            # 勾选 DoD
python cli.py check "T4" --off      # 取消勾选
python cli.py apply                 # 应用 data/writeback.json
```

网页「写回」区可复制命令或导出 `writeback.json`。CLI 除 `scan`/`apply`/写回命令外只读。

## 安装

- 依赖：Python 3.10+（标准库即可）
- 可选：Playwright + Edge（仅 UI 冒烟 `scripts/check_demo.py`）
- Windows 可用 `seat.cmd`

```bash
cd projects/seat
python cli.py which
python cli.py scan
```

## 测试

```bash
python -m unittest discover -s scripts -p "test_*.py" -v
# UI 冒烟（可选，需本机 Edge + Playwright）
python scripts/check_demo.py
```

CI 见 `.github/workflows/ci.yml`（跑单元测试）。

## 范围说明

正式版包含：UI、真实 STATUS/PLAN 扫描、CLI、写回、多项目切换、时间线、Git 集成、localStorage 持久化、测试与 CI、GitHub Pages。

仍不包含：账号体系、云同步、后端服务（保持本地优先）。

## License

MIT
