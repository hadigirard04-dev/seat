# STATUS · seat

- 阶段：正式版已部署 GitHub Pages，公开访问已验收；本地 UI 提交已推送
- 仓库：https://github.com/hadigirard04-dev/seat （PUBLIC）
- Pages：https://hadigirard04-dev.github.io/seat/
- 已推送提交：`1080df0..9b78be5`（plain-ux / plan-ui）
- 入口：`index.html` · `cli.py` · `scan`/`writeback`
- 验证：`scripts/test_*.py` 9 passed；`check_demo.py` ALL_PASS（含 T5 localStorage）
- Pages 验收（2026-09-29）：无登录访问均 HTTP 200；页面含 slot-timeline、slot-git
- 下一步：推送 `.github/workflows/ci.yml` 并确认 Actions；发布 Release
- 明确未做：账号 / 云同步 / 后端（本地优先）
