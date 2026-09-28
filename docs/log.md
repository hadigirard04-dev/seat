# docs/log

## 2026-09-28

- 完成可交互核心屏 Demo：DoD 勾选（计数 + 进度条即时更新）与 4 个 Agent 指令复制按钮联调。
- 复制链路：`clipboard.writeText`（安全上下文）→ 失败走 `textarea`/`execCommand` 兜底；成功提示 1.2s，失败提示 2s；连点清理上一次 restore timer。
- 验证：`scripts/check_demo.py`（Playwright + Edge）ALL_PASS。
- 未扩散：未做 CLI、未读写真实项目 STATUS、未 push。
