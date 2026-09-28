---
feature: seat-demo
status: designed
updated: 2026-09-28
branch: feat/seat-demo
commits: 
---

# seat 可交互核心屏 Demo

## Report

## [S1] Problem

用户在多 Agent、多 GitHub 小项目之间切换时，状态分散（CURRENT.md / PLAN / STATUS / 会话），坐下开工时不知道「接着干什么」，每次都要向 Agent 重新交代续做/验收约束。需要一页能立刻看懂、能演示给他人看的「开工屏」原型，用来看清产品价值，而不是先做完整工具。

## [S2] Design

### 形态

- 单页静态 Web Demo，纯前端，无构建步骤亦可打开（`index.html` + 同目录 CSS/JS），零外部依赖。
- 数据为**内置示例工作区**（虚构但逼真的 `sampleWorkspace`），不读取真实磁盘、不写回文件。
- 交付目录：`projects/seat`（worktree 分支 `feat/seat-demo`）。

### 屏幕结构（单屏，桌面优先，窄屏可读）

自上而下：

1. **顶栏**：产品名 `seat`、副标题「开工屏」、示例工作区路径徽章。
2. **主卡片 · 当前项目**
   - 项目名、一句话目标
   - 阶段徽章（如 `in-progress`）
   - 「最后更新」相对时间（如 `今天` / `3 天前`）
3. **主卡片 · 下一步**（视觉焦点）
   - 仅一条动作文案
   - 风险提示（可选，示例中有 1 条）
   - 按钮「复制续做指令」
4. **DoD 清单**
   - 复选框列表（约 6–8 项），含已勾/未勾混排
   - 顶部进度：`已勾 x / 全部 y` + 细进度条
   - 勾选**即时反馈**（进度条与计数变化）；不持久化，刷新恢复示例状态
5. **Agent 指令坞**
   - 4 个复制按钮：继续做 / 验收 / 复盘 / 交接
   - 每项有标签 + 一行说明
   - 点击后按钮短暂变为「已复制」
6. **页脚**：「Demo · 数据为示例 · 不写回真实 STATUS」

### 交互契约

| 操作 | 行为 |
|---|---|
| 勾选/取消 DoD | 更新计数与进度条宽度 |
| 点复制按钮 | 使用 `navigator.clipboard.writeText`；失败则用隐藏 `textarea` + `execCommand('copy')` 兜底；按钮文案 1.2s 后恢复 |
| 点「复制续做指令」 | 复制内容 = 针对「下一步」拼出的续做 prompt |
| 键盘 | 不强制；Tab 可聚焦按钮与复选框 |

### 示例数据契约

```ts
type DemoProject = {
  name: string            // 例如 "seat"
  goal: string            // 一句话
  stage: 'in-progress' | 'ready-for-review' | 'blocked' | 'done'
  updatedLabel: string    // "今天"
  nextAction: string      // 单条下一步
  risk?: string           // 可选
  dod: { id: string; label: string; done: boolean }[]
}

type AgentPrompt = {
  id: 'continue' | 'verify' | 'retro' | 'handoff'
  label: string
  hint: string
  template: (p: DemoProject) => string
}
```

示例项目名称可用虚构的 `seat` 自身或 `demo-project`；文案用中文，语气与实验室 AGENTS 一致（只做下一步、写 STATUS、不扩权）。

### 视觉

- 深色工作台风格：背景近黑 `#0f1419`，卡片 `#171d25`，描边 `#2a3542`
- 强调色青蓝 `#5b9fd4`，完成绿 `#3dba7a`
- 字体系统栈 + PingFang SC / Microsoft YaHei
- 无渐变滥用、无外部字体/图标 CDN；可用内联 SVG 小图标
- 焦点态可见（键盘）

### 错误行为

- Clipboard 不可用：显示「已复制」前先尝试兜底；仍失败则按钮变为「复制失败，请手动选中」2s
- 无其他运行时错误路径（无网络、无文件 IO）

### 测试边界

- Demo 阶段不要求自动化测试框架
- 人工验收：浏览器打开 `index.html`，完成下方 Tasks 中的可观察行为

## [S3] Out of Scope

- CLI（`seat` 命令）
- 读取真实 `projects/*`、`CURRENT.md`、`PLAN.md`、`STATUS.md`
- 勾选写回文件 / localStorage 持久化
- 多项目切换、时间线、Git 集成、部署 Pages
- 账号、云同步、后端
- 单元测试 / CI（demo 不引入）

## Tasks

- [ ] T1: 页面骨架与示例数据 — acceptance: 打开 `index.html` 可见顶栏、当前项目、下一步、DoD、指令坞、页脚，文案为中文示例 (covers: S2)
- [ ] T2: DoD 勾选与进度 — acceptance: 勾选任意一项后计数与进度条立即变化，取消勾选还原 (covers: S2)
- [ ] T3: 一键复制 Agent 指令 — acceptance: 点 4 个按钮之一，剪贴板得到对应中文指令，按钮显示「已复制」后恢复；含续做按钮文案含「下一步」内容 (covers: S2)
- [ ] T4: 视觉与窄屏 — acceptance: 1280px 与 390px 宽度下无横向滚动、主卡片可读，深色样式完整 (covers: S2)
