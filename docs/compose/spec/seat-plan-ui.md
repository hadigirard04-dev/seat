---
feature: seat-plan-ui
status: in-progress
updated: 2026-09-29
branch: feat/seat-plan-ui
commits: 
---

# 规划上屏

## Report

## [S1] Problem

规划写在 `PLAN.md` / 教练 state 里（目标、MVP、三天计划），但开工屏只显示 STATUS 的「今天先做」和完成清单。用户看不到规划，所以觉得「规划有什么用」。需要在开工屏直接展示该项目的规划，并与「今天先做」对照。

## [S2] Design

### 数据：扫描 PLAN.md

`scripts/scan_workspace.py` 在已有字段外增加：

```ts
plan: {
  goal: string            // ## 目标 下第一段
  mvpCore: string[]       // ## MVP → - 核心： 子项或同一行
  mvpOut: string[]        // ## MVP → - 不做： 子项
  days: { label: string; text: string }[]  // ## 3-Day Plan 的 Day n
  firstTask: string       // ## First Task
} | null
```

解析约定：
- 标题按 `## 目标` / `## MVP` / `## 3-Day Plan` / `## First Task`（允许中英文括号后缀）
- MVP：`- 核心：` / `- 不做：` 右侧内容，或其下 `- ` 子列表
- Day：`- Day 1：xxx` 形式；保序
- 找不到 PLAN.md 或段落空 → `plan: null`
- 同 STATUS 一样优先项目根（含 worktree 回退）下的 `PLAN.md`

### 界面：03 规划

布局顺序保持：`00 项目` → `01 当前项目` → `02 今天先做` → **`03 规划`** → 完成清单/交给 AI → 时间线/Git。

`03 规划` 全宽 band（与 01 同结构三列：编号标签 | 正文）：

- **目标** — 一句话/一段（`plan.goal`）
- **MVP** — 两列或两块：`要做的` / `不做的`（`mvpCore` / `mvpOut`）
- **安排** — 三行 Day 1/2/3（`days`）
- **第一件事** — 可选，有则显示

空态（`plan == null`）：  
`还没有规划 — 在项目里建 PLAN.md（目标 / MVP / 三天），这里就会显示`

### 与「今天先做」关系

- 不把 Day 项做成可勾选（勾选仍只在完成清单）
- 03 为只读展示；改规划仍编辑 `PLAN.md`
- 切换项目时 03 与 01/02 一起刷新

### 视觉

- 沿用 V1 Ink band + 小节标题（serif）+ muted 说明
- 不新增依赖、不改 CLI 契约（CLI 可不展示 plan）

### 测试

- `test_scan_workspace.py`：解析 PLAN 样例、无 PLAN 时 plan 为 null
- `check_demo.py`：03 规划存在；有 plan 时显示目标；空态文案在无 plan 项目上出现（或注入样例）

## [S3] Out of Scope

- 在界面上编辑规划
- 从教练 state 回填 PLAN
- 甘特图/进度可视化
- 把 Day 自动变成任务系统

## Tasks

- [ ] T1: scan 解析 PLAN.md — acceptance: 有 PLAN 的项目 `plan.goal/mvp/days` 正确；无 PLAN 为 null (covers: S2)
- [ ] T2: 03 规划 UI — acceptance: 展示目标、MVP 要做/不做、Day 列表；切换项目随之变化 (covers: S2)
- [ ] T3: 空态 — acceptance: 无 plan 时显示口语空态，不报错 (covers: S2)
- [ ] T4: 测试 — acceptance: unit + check_demo 覆盖上列并通过 (covers: S2; depends: T1, T2, T3)

