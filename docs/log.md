# docs/log

## 2026-09-28

- 完成可交互核心屏 Demo：DoD 勾选（计数 + 进度条即时更新）与 4 个 Agent 指令复制按钮联调。
- 复制链路：`clipboard.writeText`（安全上下文）→ 失败走 `textarea`/`execCommand` 兜底；成功提示 1.2s，失败提示 2s；连点清理上一次 restore timer。
- 验证：`scripts/check_demo.py`（Playwright + Edge）ALL_PASS。
- 未扩散：未做 CLI、未读写真实项目 STATUS、未 push。

## 2026-09-28 · UI 三版

- 做了 V1 Ink（编辑部）/ V2 Console（Linear 风）/ V3 Bloom（柔和）三套可交互 UI，信息架构一致。
- 用户选定 **V1 Ink**，已合入根目录 `index.html` + `style.css` + `app.js`；`designs/` 保留三版对照。
- `check_demo.py` / `check_designs.py` 均 ALL_PASS。

## 2026-09-28 · P0 真实状态

- 新增 `scripts/scan_workspace.py`：扫描实验室 `projects/*/STATUS.md`、PLAN、compose spec，生成 `data/workspace.js`。
- 主页面改为载入真实项目；示例数据仅在无扫描结果时兜底。
- 已验证：`slot-next` 为 STATUS 中真实下一步；DoD 从 spec 解析 4 项；续做指令文案含真实 nextAction。
- 仍不写回文件、不做 CLI。

## 2026-09-28 · P2 CLI

- 新增 `cli.py` + `seat.cmd`：`status` / `next` / `list` / `show` / `prompt` / `scan` / `which`。
- 只读真实 STATUS；`scan` 仅刷新 `data/`。未做写回（仍属 P1）。
- 手测：summary / list / next / prompt continue&verify / which / seat.cmd list 均正常。
- 2026-09-28 · P1 写回联调测试
- 2026-09-28 · P1 check/log/next 写回复测通过

## 2026-09-28 · P1 写回

- 新增 `scripts/writeback.py` 与 CLI：`next`（改 STATUS 下一步）、`log`（追加 docs/log）、`check [--off]`（改 spec/PLAN 勾选）、`apply`（吃 `data/writeback.json`）。
- UI 增加写回区：复制 log 命令、导出 writeback.json、复制 apply/check 命令。
- 已实测写入 `STATUS.md`、`docs/log.md`、`docs/compose/spec/seat-demo.md`。勾选「已是目标状态」也会报告命中文件。

- 2026-09-28 · P1 写回通道：next/log/check/apply + UI 导出
