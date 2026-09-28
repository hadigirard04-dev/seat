# STATUS · seat

- 阶段：P2 完成 — CLI（status/list/show/prompt/scan/which）+ P0 真实状态 + V1 UI
- 分支：`feat/seat-demo`
- UI：V1 Ink 已合入主 `index.html`
- 扫描：`python scripts/scan_workspace.py` → `data/workspace.js`（file:// 可用）
- CLI：`python cli.py` / `seat.cmd`（只读，scan 除外）
- 验证：`scripts/check_demo.py` ALL_PASS；CLI 手测 status/list/next/prompt/which 通过
- 下一步（未做）：P1 勾选写回 STATUS/docs/log；P3 微调 UI / 空状态
- 明确未做：写回、push、Pages、合并 main
