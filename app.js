/* seat — loads real workspace via data/workspace.js when present. */
(function () {
  const sampleProject = {
    id: 'sample',
    name: 'seat',
    goal: '打开电脑后的第一屏：当前项目、下一步、DoD、一键复制 Agent 指令。',
    stage: '进行中',
    stageLabel: '进行中',
    updatedLabel: '示例',
    nextAction: '运行 python scripts/scan_workspace.py 生成真实状态',
    risk: '当前为示例数据，尚未载入 data/workspace.js。',
    dod: [
      { id: 't1', label: '扫描 projects/*/STATUS.md', done: false },
      { id: 't2', label: '页面显示真实下一步', done: false },
      { id: 't3', label: '复制续做指令含真实 nextAction', done: false },
    ],
  }

  const prompts = [
    {
      id: 'continue',
      label: '继续做',
      hint: '只做下一步，不扩范围',
      template: function (p) {
        return '继续做项目「' + p.name + '」。只做这一件：' + p.nextAction + '。做完更新 STATUS 与 docs/log，不要扩散范围，不要做未授权的 push。'
      },
    },
    {
      id: 'verify',
      label: '验收',
      hint: '按 DoD 逐项要证据',
      template: function (p) {
        return '请对「' + p.name + '」按 PLAN/DoD 逐项验收。每项给出可观察证据；缺证据标 failed，不要报喜。当前下一步是：' + p.nextAction + '。'
      },
    },
    {
      id: 'retro',
      label: '复盘',
      hint: '写 log 与可复用经验',
      template: function (p) {
        return '对「' + p.name + '」做简短复盘：完成项、卡点、可复用经验写入 docs/log.md 与 lessons（如有）。不要虚构未做的事。'
      },
    },
    {
      id: 'handoff',
      label: '交接',
      hint: '给下一个会话的上下文',
      template: function (p) {
        return '交接「' + p.name + '」：目标是 ' + (p.goal || '') + ' 阶段=' + (p.stageLabel || p.stage || '') + '，下一步=' + p.nextAction + '。DoD 未完成项请列出。忽略无关工作区历史。'
      },
    },
  ]

  let projects = []
  let active = sampleProject
  let dodState = []

  function $(id) {
    return document.getElementById(id)
  }

  function storageKey(id) {
    return 'seat.dod.' + id
  }

  function loadDodOverrides(projectId) {
    try {
      const raw = window.localStorage.getItem(storageKey(projectId))
      if (!raw) return {}
      const obj = JSON.parse(raw)
      return obj && typeof obj === 'object' ? obj : {}
    } catch (e) {
      return {}
    }
  }

  function saveDodOverrides(projectId, state) {
    try {
      const map = {}
      state.forEach(function (d) {
        map[d.id] = !!d.done
      })
      window.localStorage.setItem(storageKey(projectId), JSON.stringify(map))
    } catch (e) {
      /* private mode / quota — ignore */
    }
  }

  function clearDodOverrides(projectId) {
    try {
      window.localStorage.removeItem(storageKey(projectId))
    } catch (e) {
      /* ignore */
    }
  }

  function copyFallback(text) {
    try {
      const ta = document.createElement('textarea')
      ta.value = text
      ta.setAttribute('readonly', '')
      ta.style.position = 'fixed'
      ta.style.left = '-9999px'
      document.body.appendChild(ta)
      ta.select()
      const ok = document.execCommand('copy')
      ta.remove()
      return ok
    } catch (e) {
      return false
    }
  }

  async function copyText(text, button) {
    const original = button.dataset.originalLabel || button.textContent
    button.dataset.originalLabel = original
    if (button.dataset.restoreTimer) window.clearTimeout(Number(button.dataset.restoreTimer))
    let ok = false
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text)
        ok = true
      } else {
        ok = copyFallback(text)
      }
    } catch (e) {
      ok = copyFallback(text)
    }
    button.classList.toggle('is-ok', ok)
    button.classList.toggle('is-fail', !ok)
    button.textContent = ok ? '已复制' : '复制失败'
    const delay = ok ? 1200 : 2000
    const timer = window.setTimeout(function () {
      button.classList.remove('is-ok', 'is-fail')
      button.textContent = button.dataset.originalLabel || original
      delete button.dataset.restoreTimer
    }, delay)
    button.dataset.restoreTimer = String(timer)
    return ok
  }

  function project() {
    return active
  }

  function renderDod() {
    const listEl = $('slot-dod')
    const countEl = $('slot-count')
    const fillEl = $('slot-fill')
    listEl.innerHTML = ''
    if (!dodState.length) {
      listEl.innerHTML =
        '<li class="dod-item"><div class="dod-empty">该项目暂无 DoD 勾选项（STATUS / PLAN / spec 里没有 [ ] 条目）</div></li>'
    } else {
      dodState.forEach(function (item, index) {
        const li = document.createElement('li')
        li.className = 'dod-item' + (item.done ? ' is-done' : '')
        li.innerHTML =
          '<label><input type="checkbox" data-id="' +
          item.id +
          '"' +
          (item.done ? ' checked' : '') +
          ' /><span class="dod-index">' +
          String(index + 1).padStart(2, '0') +
          '</span><span class="dod-label">' +
          item.label +
          '</span></label>'
        listEl.appendChild(li)
      })
    }
    updateProgress()
  }

  function updateProgress() {
    const total = dodState.length
    const done = dodState.filter(function (d) {
      return d.done
    }).length
    const countEl = $('slot-count')
    const fillEl = $('slot-fill')
    if (countEl) countEl.textContent = done + ' / ' + total
    if (fillEl) fillEl.style.width = (total === 0 ? 0 : Math.round((done / total) * 100)) + '%'
  }

  function renderDate() {
    const el = $('slot-date')
    if (!el) return
    const d = new Date()
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const week = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
    el.textContent = y + '.' + m + '.' + day + ' · 周' + week
  }

  function setActive(p) {
    if (!p) {
      renderEmpty()
      return
    }
    active = p
    const overrides = loadDodOverrides(p.id || p.name || 'sample')
    dodState = (p.dod || []).map(function (d) {
      const hasOverride = Object.prototype.hasOwnProperty.call(overrides, d.id)
      return {
        id: d.id,
        label: d.label,
        done: hasOverride ? !!overrides[d.id] : !!d.done,
      }
    })
    const name = $('slot-name')
    const goal = $('slot-goal')
    const stage = $('slot-stage')
    const updated = $('slot-updated')
    const next = $('slot-next')
    const risk = $('slot-risk')
    if (name) name.textContent = p.name || '—'
    if (goal) goal.textContent = p.goal || '（无目标描述）'
    if (stage) stage.textContent = p.stage || p.stageLabel || '—'
    if (updated) updated.textContent = p.updatedLabel || '—'
    if (next) {
      const hasNext = !!(p.nextAction && p.nextAction.trim())
      next.textContent = hasNext ? p.nextAction : '还没写「下一步」— 用 python cli.py next "…" 补一条'
      next.classList.toggle('is-empty', !hasNext)
    }
    if (risk) {
      if (p.risk) {
        risk.hidden = false
        risk.textContent = p.risk
      } else {
        risk.hidden = true
        risk.textContent = ''
      }
    }
    renderDod()
    renderProjectSwitcher()
    renderTimeline(p)
    renderGit(p)
  }

  function renderTimeline(p) {
    const el = $('slot-timeline')
    if (!el) return
    const items = (p && p.timeline) || []
    el.innerHTML = ''
    if (!items.length) {
      el.innerHTML = '<li class="tl-empty">暂无时间线（docs/log.md 为空或未扫描）</li>'
      return
    }
    items.forEach(function (item) {
      const li = document.createElement('li')
      li.className = 'tl-item'
      li.innerHTML =
        '<span class="tl-date">' +
        (item.date || '') +
        '</span><span class="tl-text">' +
        (item.text || '') +
        '</span>'
      el.appendChild(li)
    })
  }

  function renderGit(p) {
    const el = $('slot-git')
    if (!el) return
    const g = (p && p.git) || {}
    el.innerHTML = ''
    if (!g.available) {
      el.innerHTML = '<p class="git-empty">该项目未检测到 git 仓库</p>'
      return
    }
    const head = document.createElement('p')
    head.className = 'git-branch'
    head.textContent = '分支 ' + (g.branch || '—')
    el.appendChild(head)
    const list = document.createElement('ul')
    list.className = 'git-log'
    ;(g.commits || []).forEach(function (c) {
      const li = document.createElement('li')
      li.innerHTML =
        '<span class="git-sha">' +
        (c.sha || '') +
        '</span><span class="git-subject">' +
        (c.subject || '') +
        '</span><span class="git-date">' +
        (c.date || '') +
        '</span>'
      list.appendChild(li)
    })
    el.appendChild(list)
  }

  function renderEmpty() {
    const name = $('slot-name')
    const goal = $('slot-goal')
    const next = $('slot-next')
    if (name) name.textContent = '没有可显示的项目'
    if (goal) {
      goal.textContent = '在实验室根目录执行 python cli.py scan，或确认 projects/ 下存在 STATUS.md。'
    }
    if (next) {
      next.textContent = '扫描后，这里只显示一条「下一步」'
      next.classList.add('is-empty')
    }
    dodState = []
    renderDod()
    renderTimeline(null)
    renderGit(null)
  }

  function renderProjectSwitcher() {
    const el = $('slot-projects')
    const picker = $('slot-project-picker')
    if (!el) return
    if (!projects.length) {
      if (picker) picker.hidden = true
      return
    }
    if (picker) picker.hidden = false
    el.innerHTML = ''
    projects.forEach(function (p) {
      const b = document.createElement('button')
      b.type = 'button'
      b.className = 'proj-chip' + (p.id === active.id ? ' is-active' : '')
      b.setAttribute('aria-pressed', p.id === active.id ? 'true' : 'false')
      b.textContent = p.name
      b.addEventListener('click', function () {
        setActive(p)
      })
      el.appendChild(b)
    })
  }

  function renderPrompts() {
    const grid = $('slot-prompts')
    grid.innerHTML = ''
    prompts.forEach(function (p) {
      const btn = document.createElement('button')
      btn.type = 'button'
      btn.className = 'prompt-btn'
      btn.setAttribute('data-copy', p.id)
      btn.innerHTML = '<strong>' + p.label + '</strong><span>' + p.hint + '</span>'
      grid.appendChild(btn)
    })
  }

  function bindWriteback() {
    const logBtn = $('slot-wb-log-btn')
    const exportBtn = $('slot-wb-export')
    const copyBtn = $('slot-wb-copy')
    const input = $('slot-wb-log')
    const msg = $('slot-wb-msg')

    function say(text) {
      if (!msg) return
      msg.hidden = false
      msg.textContent = text
    }

    function payload() {
      return {
        next: active.nextAction || '',
        stage: active.stage || '',
        log: (input && input.value.trim()) || '',
        checks: dodState.map(function (d) {
          return { label: d.label, done: d.done }
        }),
        project: active.name,
        generatedAt: new Date().toISOString(),
      }
    }

    if (logBtn) {
      logBtn.addEventListener('click', function () {
        const text = (input && input.value.trim()) || ''
        if (!text) {
          say('先填一句 log 内容')
          return
        }
        const cmd = 'python cli.py log ' + JSON.stringify(text)
        copyText(cmd, logBtn)
        say('已复制 log 命令，粘贴到终端执行写回')
        if (input) input.value = ''
      })
    }

    if (exportBtn) {
      exportBtn.addEventListener('click', function () {
        const blob = new Blob([JSON.stringify(payload(), null, 2)], { type: 'application/json' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'writeback.json'
        a.click()
        URL.revokeObjectURL(url)
        say('已下载 writeback.json — 放到 data/ 后执行 python cli.py apply')
      })
    }

    if (copyBtn) {
      copyBtn.addEventListener('click', function () {
        const checks = dodState
          .filter(function (d) {
            return d.done
          })
          .map(function (d) {
            return 'python cli.py check ' + JSON.stringify(d.label)
          })
        const lines = []
        if (active.nextAction) {
          lines.push('python cli.py next ' + JSON.stringify(active.nextAction))
        }
        lines.push.apply(lines, checks)
        const cmd = lines.join(' && ') || 'python cli.py apply'
        copyText(cmd, copyBtn)
        say('已复制写回命令序列')
      })
    }
  }

  function bindEvents() {
    $('slot-dod').addEventListener('change', function (e) {
      const t = e.target
      if (!t || t.tagName !== 'INPUT') return
      const item = dodState.find(function (d) {
        return d.id === t.dataset.id
      })
      if (!item) return
      item.done = t.checked
      const li = t.closest('li')
      if (li) li.classList.toggle('is-done', item.done)
      updateProgress()
      saveDodOverrides(active.id || active.name || 'sample', dodState)
    })

    $('slot-prompts').addEventListener('click', function (e) {
      const btn = e.target && e.target.closest ? e.target.closest('[data-copy]') : null
      if (!btn) return
      const id = btn.getAttribute('data-copy')
      const p = prompts.find(function (x) {
        return x.id === id
      })
      if (p) copyText(p.template(project()), btn)
    })

    const main = $('slot-copy-continue')
    if (main) {
      main.addEventListener('click', function () {
        const p = prompts.find(function (x) {
          return x.id === 'continue'
        })
        copyText(p.template(project()), main)
      })
    }
  }

  function boot() {
    renderDate()
    renderPrompts()
    bindEvents()
    bindWriteback()
    const data = window.SEAT_DATA
    if (data && data.projects && data.projects.length) {
      projects = data.projects
      const primary =
        projects.find(function (p) {
          return p.id === data.primaryId
        }) || projects[0]
      const banner = $('slot-source')
      if (banner) {
        banner.hidden = false
        banner.classList.remove('is-sample')
        const rootLabel = (data.root || 'workspace').split(/[\\/]/).filter(Boolean).slice(-2).join('/')
        banner.textContent =
          '真实状态 · ' + rootLabel + ' · 生成于 ' + (data.generatedAt || '') +
          ' · 刷新：python cli.py scan'
      }
      setActive(primary)
    } else {
      projects = [sampleProject]
      const banner = $('slot-source')
      if (banner) {
        banner.hidden = false
        banner.classList.add('is-sample')
        banner.textContent = '示例数据 · 运行 python scripts/scan_workspace.py 后刷新'
      }
      setActive(sampleProject)
    }
  }

  window.SEAT = { boot: boot, init: boot }
})()
