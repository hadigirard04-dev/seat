/* shared demo behavior for seat design variants */
(function () {
  const sampleProject = {
    name: 'seat',
    goal: '打开电脑后的第一屏：当前项目、下一步、DoD、一键复制 Agent 指令。',
    stageLabel: '进行中',
    updatedLabel: '今天',
    nextAction: '选定 UI 方向并替换主 Demo 皮肤',
    risk: '三版并存仅供对比；最终只保留一版进 main。',
    dod: [
      { id: 't1', label: '三版信息架构一致，可互换对比', done: true },
      { id: 't2', label: 'V1 Ink 视觉完成并可交互', done: true },
      { id: 't3', label: 'V2 Console 视觉完成并可交互', done: true },
      { id: 't4', label: 'V3 Bloom 视觉完成并可交互', done: false },
      { id: 't5', label: '截图并排可放进作品集', done: false },
      { id: 't6', label: '选定最终皮肤写入 STATUS', done: false },
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
        `交接「${p.name}」：目标是 ${p.goal} 阶段=${p.stageLabel}，下一步=${p.nextAction}。DoD 未完成项请列出。忽略无关工作区历史。`,
    },
  ]

  const state = {
    dod: sampleProject.dod.map((d) => Object.assign({}, d)),
  }

  function $(id) {
    return document.getElementById(id)
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
    if (button.dataset.restoreTimer) {
      window.clearTimeout(Number(button.dataset.restoreTimer))
    }
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
    return {
      name: sampleProject.name,
      goal: sampleProject.goal,
      stageLabel: sampleProject.stageLabel,
      nextAction: sampleProject.nextAction,
    }
  }

  function renderDod(listEl, countEl, fillEl) {
    listEl.innerHTML = ''
    state.dod.forEach(function (item, index) {
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
    updateProgress(countEl, fillEl, listEl)
  }

  function updateProgress(countEl, fillEl, listEl) {
    const total = state.dod.length
    const done = state.dod.filter(function (d) {
      return d.done
    }).length
    if (countEl) countEl.textContent = done + ' / ' + total
    if (fillEl) fillEl.style.width = (total === 0 ? 0 : Math.round((done / total) * 100)) + '%'
    if (listEl) {
      listEl.querySelectorAll('li').forEach(function (li, i) {
        li.classList.toggle('is-done', state.dod[i] && state.dod[i].done)
      })
    }
  }

  function bindDod(listEl, countEl, fillEl) {
    listEl.addEventListener('change', function (e) {
      const t = e.target
      if (!t || t.tagName !== 'INPUT') return
      const item = state.dod.find(function (d) {
        return d.id === t.dataset.id
      })
      if (!item) return
      item.done = t.checked
      updateProgress(countEl, fillEl, listEl)
    })
  }

  function bindPrompts(gridEl) {
    gridEl.addEventListener('click', function (e) {
      const btn = e.target && e.target.closest ? e.target.closest('[data-copy]') : null
      if (!btn) return
      const kind = btn.getAttribute('data-copy')
      if (kind === 'continue-main') {
        const p = prompts.find(function (x) {
          return x.id === 'continue'
        })
        copyText(p.template(project()), btn)
        return
      }
      const p = prompts.find(function (x) {
        return x.id === kind
      })
      if (p) copyText(p.template(project()), btn)
    })
  }

  function fillStatic() {
    ;['name', 'goal', 'stage', 'updated', 'next', 'risk'].forEach(function (key) {
      const el = $('slot-' + key)
      if (!el) return
      if (key === 'name') el.textContent = sampleProject.name
      if (key === 'goal') el.textContent = sampleProject.goal
      if (key === 'stage') el.textContent = sampleProject.stageLabel
      if (key === 'updated') el.textContent = sampleProject.updatedLabel
      if (key === 'next') el.textContent = sampleProject.nextAction
      if (key === 'risk' && sampleProject.risk) {
        el.hidden = false
        el.textContent = sampleProject.risk
      }
    })
    const grid = $('slot-prompts')
    if (grid) {
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
  }

  window.SEAT = {
    init: function () {
      fillStatic()
      renderDod($('slot-dod'), $('slot-count'), $('slot-fill'))
      bindDod($('slot-dod'), $('slot-count'), $('slot-fill'))
      bindPrompts($('slot-prompts'))
      const main = $('slot-copy-continue')
      if (main) {
        main.addEventListener('click', function () {
          const p = prompts.find(function (x) {
            return x.id === 'continue'
          })
          copyText(p.template(project()), main)
        })
      }
    },
  }
})()
