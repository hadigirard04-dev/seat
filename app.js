/**
 * seat demo — sample workspace only. No disk IO, no persistence.
 */

const sampleProject = {
  name: 'seat',
  goal: '打开电脑后的第一屏：当前项目、下一步、DoD、一键复制 Agent 指令。',
  stage: 'in-progress',
  stageLabel: '进行中',
  updatedLabel: '今天',
  nextAction: '完成可交互核心屏 Demo：DoD 勾选与 4 个复制按钮联调',
  risk: 'Demo 不读写真实 STATUS，验收只看浏览器内行为。',
  dod: [
    { id: 't1', label: '页面骨架与中文示例数据可见', done: true },
    { id: 't2', label: 'DoD 勾选后计数与进度条立即更新', done: true },
    { id: 't3', label: '四个 Agent 指令按钮可复制到剪贴板', done: false },
    { id: 't4', label: '续做指令文案包含「下一步」内容', done: false },
    { id: 't5', label: '1280px 与 390px 宽度无横向滚动', done: false },
    { id: 't6', label: 'README 写明如何打开 Demo', done: false },
    { id: 't7', label: '截图可放进作品集', done: false },
  ],
}

const prompts = [
  {
    id: 'continue',
    label: '继续做',
    hint: '只做下一步，不扩范围',
    template: (p) =>
      `继续做项目「${p.name}」。只做这一件：${p.nextAction}。做完更新 STATUS 与 docs/log，不要扩散范围，不要做未授权的 push。`,
  },
  {
    id: 'verify',
    label: '验收',
    hint: '按 DoD 逐项要证据',
    template: (p) =>
      `请对「${p.name}」按 PLAN/DoD 逐项验收。每项给出可观察证据；缺证据标 failed，不要报喜。当前下一步是：${p.nextAction}。`,
  },
  {
    id: 'retro',
    label: '复盘',
    hint: '写 log 与可复用经验',
    template: (p) =>
      `对「${p.name}」做简短复盘：完成项、卡点、可复用经验写入 docs/log.md 与 lessons（如有）。不要虚构未做的事。`,
  },
  {
    id: 'handoff',
    label: '交接',
    hint: '给下一个会话的上下文',
    template: (p) =>
      `交接「${p.name}」：目标是${p.goal} 阶段=${p.stageLabel}，下一步=${p.nextAction}。DoD 未完成项请列出。忽略无关工作区历史。`,
  },
]

const els = {
  title: document.getElementById('project-title'),
  goal: document.getElementById('project-goal'),
  stage: document.getElementById('project-stage'),
  updated: document.getElementById('project-updated'),
  next: document.getElementById('next-title'),
  risk: document.getElementById('project-risk'),
  dodList: document.getElementById('dod-list'),
  dodCount: document.getElementById('dod-count'),
  progressFill: document.getElementById('progress-fill'),
  promptGrid: document.getElementById('prompt-grid'),
  btnContinue: document.getElementById('btn-copy-continue'),
}

const state = {
  dod: sampleProject.dod.map((d) => ({ ...d })),
}

function renderProject() {
  els.title.textContent = sampleProject.name
  els.goal.textContent = sampleProject.goal
  els.stage.textContent = sampleProject.stageLabel
  els.stage.className = `stage stage-${sampleProject.stage}`
  els.updated.textContent = sampleProject.updatedLabel
  els.next.textContent = sampleProject.nextAction
  if (sampleProject.risk) {
    els.risk.hidden = false
    els.risk.textContent = `⚠ ${sampleProject.risk}`
  }
}

function renderDod() {
  els.dodList.innerHTML = ''
  for (const item of state.dod) {
    const li = document.createElement('li')
    if (item.done) li.classList.add('done')

    const label = document.createElement('label')
    const input = document.createElement('input')
    input.type = 'checkbox'
    input.checked = item.done
    input.dataset.id = item.id
    input.setAttribute('aria-label', item.label)

    const span = document.createElement('span')
    span.className = 'dod-label'
    span.textContent = item.label

    label.append(input, span)
    li.append(label)
    els.dodList.append(li)
  }
  updateProgress()
}

function updateProgress() {
  const total = state.dod.length
  const done = state.dod.filter((d) => d.done).length
  els.dodCount.textContent = `${done} / ${total}`
  els.progressFill.style.width = total === 0 ? '0%' : `${Math.round((done / total) * 100)}%`
}

function renderPrompts() {
  els.promptGrid.innerHTML = ''
  for (const p of prompts) {
    const wrap = document.createElement('div')
    wrap.className = 'prompt-item'

    const row = document.createElement('div')
    row.className = 'row'

    const left = document.createElement('div')
    const strong = document.createElement('strong')
    strong.textContent = p.label
    const hint = document.createElement('p')
    hint.textContent = p.hint
    left.append(strong, hint)

    const btn = document.createElement('button')
    btn.type = 'button'
    btn.className = 'btn'
    btn.textContent = '复制'
    btn.dataset.promptId = p.id

    row.append(left, btn)
    wrap.append(row)
    els.promptGrid.append(wrap)
  }
}

async function copyText(text, button, okLabel = '已复制') {
  const original = button.textContent
  let ok = false
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text)
      ok = true
    } else {
      ok = copyFallback(text)
    }
  } catch {
    ok = copyFallback(text)
  }

  button.classList.remove('copied', 'failed')
  button.classList.add(ok ? 'copied' : 'failed')
  button.textContent = ok ? okLabel : '复制失败，请手动选中'
  window.setTimeout(() => {
    button.classList.remove('copied', 'failed')
    button.textContent = original
  }, 1200)
  return ok
}

function copyFallback(text) {
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.setAttribute('readonly', '')
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    document.body.append(ta)
    ta.select()
    const ok = document.execCommand('copy')
    ta.remove()
    return ok
  } catch {
    return false
  }
}

function currentProject() {
  return {
    ...sampleProject,
    dod: state.dod,
    stageLabel: sampleProject.stageLabel,
    goal: sampleProject.goal,
    nextAction: sampleProject.nextAction,
  }
}

function bindEvents() {
  els.dodList.addEventListener('change', (e) => {
    const target = e.target
    if (!(target instanceof HTMLInputElement)) return
    const id = target.dataset.id
    const item = state.dod.find((d) => d.id === id)
    if (!item) return
    item.done = target.checked
    const li = target.closest('li')
    if (li) li.classList.toggle('done', item.done)
    updateProgress()
  })

  els.btnContinue.addEventListener('click', () => {
    const text = prompts.find((p) => p.id === 'continue').template(currentProject())
    void copyText(text, els.btnContinue)
  })

  els.promptGrid.addEventListener('click', (e) => {
    const target = e.target
    if (!(target instanceof HTMLElement)) return
    const btn = target.closest('button[data-prompt-id]')
    if (!(btn instanceof HTMLButtonElement)) return
    const id = btn.dataset.promptId
    const prompt = prompts.find((p) => p.id === id)
    if (!prompt) return
    void copyText(prompt.template(currentProject()), btn)
  })
}

renderProject()
renderDod()
renderPrompts()
bindEvents()
