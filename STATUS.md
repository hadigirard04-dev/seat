# STATUS · seat

- 阶段：正式版已部署 GitHub Pages
- 仓库：https://github.com/hadigirard04-dev/seat （PUBLIC）
- Pages：https://hadigirard04-dev.github.io/seat/ （status=built）
- 交付 commit：`ed09908`
- 入口：`index.html` · `cli.py` · `scan`/`writeback`
- 验证：`scripts/test_*.py` 9 passed；`check_demo.py` ALL_PASS（含 T5 localStorage）
- 下一步：补推 `.github/workflows/ci.yml`（需 gh `workflow` scope）并跑通 CI
- 明确未做：账号 / 云同步 / 后端（本地优先）；CI 配置已写好但尚未进入远程仓库
