---
feature: seat-plain-ux
status: in-progress
updated: 2026-09-29
branch: feat/seat-plain-ux
commits: 
---

# seat 人话化与好上手

## Report

## [S1] Problem

用户打开开工屏后看不懂在做什么、怎么用。界面充斥内部术语（Definition of Done、Agent 指令坞、写回），没有「今天先做什么」的焦点，项目列表看不出谁在推进/谁被搁置，也没有首次使用说明。多项目切换刚做完，但心智负担仍在。

目标：坐下 10 秒能明白——选哪个项目、今天只做哪一件事、复制哪段话给 AI。

## [S2] Design

### 文案人话化（全站术语替换）

| 现文案 | 新文案 |
|---|---|
| Definition of Done | 完成清单 |
| Agent 指令坞 | 交给 AI |
| 写回 | 保存进度 |
| 复制续做指令 → | 复制「接着做」指令 |
| 先选项目，下面显示它的进度 | 选一个项目，下面就是它的进度 |
| 点击复制 | 点一下复制 |
| 追加 log | 记一笔 |
| 导出 writeback.json | 导出进度文件 |
| 复制 apply 命令 | 复制保存命令 |
| 完成清单空态、下一步空态 | 保持口语，去掉「DoD / STATUS」等词 |

页脚：`SEAT · 开工屏 · 数据来自各项目 STATUS · 勾选保存在本机`  
指令坞按钮说明改写为：接着做 / 验收 / 复盘 / 交班（保持四类，标签人话）。

### 今日焦点（顶部「今天先做」）

在「02 下一步」之上或融合为更醒目的主行动区：

- 标签：`今天先做`（替代/并列「下一步」）
- 仅一条动作，字更大；无下一步时显示：`还没写下一步 — 在项目 STATUS 里补一条`
- 风险提示仍可选，弱化显示
- 主按钮：`复制「接着做」指令`

`02` 编号可保留为「02 今天先做」，避免用户已熟悉的编号体系大变。

### 项目状态标签（选择栏）

`00 项目` 每个 chip 或 chip 下方小标显示就绪度：

| 规则 | 标签 |
|---|---|
| `updatedLabel`/timeline 最近 1 天内 | 今天 |
| 最近 3 天内 | 本周 |
| 超过 3 天 | 放一放 |
| `stage`/STATUS 含完成/交付/Pages 等已收尾语义 | 已收尾 |
| `stage`/STATUS 含卡点/blocked | 被卡住 |

数据不足时显示 `—`。标签只影响展示，不写文件。

### 首开三步引导

当 `localStorage` 无 `seat.onboarded` 时，在 `00 项目` 下方显示可关闭的引导条：

1. **选项目** — 点上面的名字切换  
2. **看今天先做** — 只做这一件  
3. **复制给 AI** — 点黑色按钮，粘到 MiMo / Claude  

按钮「知道了」→ 写入 `localStorage.seat.onboarded = '1'`，本机不再显示。  
`?onboard=1` 查询参数可强制再次显示（便于验收/演示）。

### 布局约束

- 不改动：V1 Ink 视觉语言、双栏结构、时间线/Git/写回功能、扫描与 CLI
- 项目选择栏保持在开工屏标题下、当前项目上
- 390px 无横向溢出
- 不引入构建步骤与新依赖

### 测试边界

- 扩展 `scripts/check_demo.py`：术语不存在断言、今日焦点存在、onboard 显示/关闭、状态 chip 渲染
- `scripts/test_*.py` 仍须通过（不改扫描契约则零改动）

## [S3] Out of Scope

- 多根目录扫描、会话闭环、git log 自动写回
- 隐藏「保存进度」区（只改文案）
- 账号/云同步/后端
- 重新设计视觉风格（改版布局/换皮）
- CLI 命令改名

## Tasks

- [ ] T1: 全站术语人话替换 — acceptance: 页面与按钮不再出现 Definition of Done / Agent 指令坞 / 写回 / writeback 等词；引导与页脚为中文口语 (covers: S2)
- [ ] T2: 今天先做焦点区 — acceptance: 主行动区标题为「今天先做」，空态口语提示，主按钮复制续做指令 (covers: S2)
- [ ] T3: 项目状态标签 — acceptance: 多项目时 chip 带今天/本周/放一放/已收尾/被卡住/— 之一，规则与 S2 表一致 (covers: S2)
- [ ] T4: 首开三步引导 — acceptance: 无 onboarded 时显示引导；点「知道了」刷新后不再显示；`?onboard=1` 可再现 (covers: S2)
- [ ] T5: 验收脚本 — acceptance: `check_demo.py` 新增上述断言并 ALL_PASS；`test_*.py` 通过 (covers: S2; depends: T1, T2, T3, T4)

