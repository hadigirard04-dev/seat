# STATUS · seat

- 阶段：P0–P2 + **P1 写回** 完成（真实状态 / CLI / V1 UI / STATUS·log 写回）
- 分支：`feat/seat-demo`
- UI：V1 Ink；DoD 可勾选；写回区可导出 `writeback.json` / 复制命令
- 扫描：`python scripts/scan_workspace.py` 或 `python cli.py scan`
- CLI 写回：`next` / `log` / `check [--off]` / `apply`
- 验证：`check_demo.py` ALL_PASS；`next`/`log`/`check` 已实测写入 STATUS、docs/log、spec
- 下一步：合并 main，或 P3 UI 微调
- 明确未做：push、Pages、合并 main
