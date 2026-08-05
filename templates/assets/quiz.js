/* quiz.js — reusable quiz widget for a lesson. Self-contained, works on file://.
 * Markup contract and behaviour: skills/teach/references/COMPONENTS.md § Quiz.
 * teach-template-version: 24
 */
(function () {
  'use strict';

  const SEAL_KEY = 'teach:unsealed:' + location.pathname;
  const UNDO_MS = 3000;

  // Every string the widget writes into a page, with its English default — the
  // one place any of them live. Override with the matching attribute on .quiz
  // for one quiz, or on <html> for the whole lesson: closest() takes the nearer
  // one, so an existing per-quiz override still wins. A non-English course sets
  // what it needs once beside lang and never forks the widget.
  // Tabled in COMPONENTS.md § Quiz.
  const DEFAULTS = {
    'data-label': 'Cold open',
    'data-undo-label': 'Undo',
    'data-copied-label': 'Copied',
    'data-copy-failed-label': 'Copy failed. Result selected; copy it manually.',
    'data-copied-status': 'Result copied. Paste it into your next message to your teacher.',
    'data-unsealed-label': 'Lesson unsealed.',
    'data-progress-label': '{n} of {total} answered',
    'data-scored-label': 'Scored. Schedule updated.',
    'data-reconnect-label': 'Session restarted — reload this lesson to reconnect',
    'data-score-failed-label':
      'Scoring failed ({status}). Result saved locally — retry when the server is back.',
    'data-network-failed-label':
      'Network error. Result saved locally — retry when the server is back.',
    'data-retry-label': 'Retry',
    'data-confidence-legend': 'How sure are you, 1 to 5?',
    'data-confidence-label': 'How sure?',
    'data-confidence-option-label': '{n} out of 5',
  };

  // {name} slots fill from vals. A translated string carries its own slot
  // positions — word order moves between languages, so the widget never
  // concatenates fragments around a number.
  const t = (from, attr, vals) => {
    const src = from.closest('[' + attr + ']');
    const s = (src && src.getAttribute(attr)) || DEFAULTS[attr];
    return vals ? s.replace(/\{(\w+)\}/g, (_, k) => vals[k]) : s;
  };

  const alreadyUnsealed = () => {
    try {
      return localStorage.getItem(SEAL_KEY) === '1';
    } catch {
      return false;
    }
  };

  const rememberUnsealed = () => {
    try {
      localStorage.setItem(SEAL_KEY, '1');
    } catch {}
  };

  function unseal(targetId, announce) {
    const sealed = document.getElementById(targetId);
    if (!sealed) return;
    sealed.classList.remove('sealed');
    sealed.removeAttribute('inert');
    const note = document.querySelector('.seal-note');
    if (!note) return;
    if (announce) {
      note.textContent = t(note, 'data-unsealed-label');
      note.classList.add('is-unsealed');
    } else note.remove();
  }

  const PENDING_KEY = 'teach:pending:' + location.pathname;

  // drop prior JS-created status/schedule/reconnect/error blocks so a retry
  // (or a 401→2xx transition after manual reload) never stacks duplicates.
  const clearDynamic = (root) =>
    root
      .querySelectorAll('.quiz-status, .quiz-schedule, .quiz-reconnect, .quiz-error')
      .forEach((el) => el.remove());

  const persistLine = (line) => {
    try {
      localStorage.setItem(PENDING_KEY, line);
    } catch {}
  };
  const clearPending = () => {
    try {
      localStorage.removeItem(PENDING_KEY);
    } catch {}
  };

  const el = (tag, cls, text, role) => {
    const node = document.createElement(tag);
    node.className = cls;
    if (role) node.setAttribute('role', role);
    if (text != null) node.textContent = text;
    return node;
  };

  // The copy-button paste flow, for both routes that need it: file://, where
  // there is no server to POST to, and a 401 after the serve token went stale.
  // Everything it touches rides on ctx.
  const wireCopyFallback = (ctx) => {
    if (!ctx.copyBtn) return;
    ctx.copyBtn.hidden = false;
    ctx.copyBtn.addEventListener('click', () => {
      if (ctx.copyStatus) ctx.copyStatus.textContent = '';
      ctx.copyText(
        ctx.line,
        ctx.copyBtn,
        t(ctx.root, 'data-copied-label'),
        () => {
          if (ctx.copyStatus) ctx.copyStatus.textContent = t(ctx.root, 'data-copied-status');
        },
        () => {
          ctx.selectResult();
          if (ctx.copyStatus) ctx.copyStatus.textContent = t(ctx.root, 'data-copy-failed-label');
        },
      );
    });
  };

  // REQ-007: 2xx unseals + shows schedule; 401 keeps sealed, reveals paste
  // fallback + reload hint; other non-2xx (and network failure) stay sealed,
  // persist the line to localStorage, and offer a retry that re-runs the POST.
  function handleScoreResponse(resp, ctx) {
    clearDynamic(ctx.root);
    if (resp && resp.ok) {
      ctx.unseal(ctx.releases, true);
      ctx.rememberUnsealed();
      clearPending();
      if (ctx.copyBtn) ctx.copyBtn.hidden = true;
      ctx.root.appendChild(el('p', 'quiz-status', t(ctx.root, 'data-scored-label'), 'status'));
      return resp.json().then((data) => {
        if (!data || !Array.isArray(data.schedule)) return;
        const block = el('div', 'quiz-schedule');
        data.schedule.forEach((r) => {
          block.appendChild(
            el(
              'p',
              null,
              r.id + ' interval=' + r.interval + ' next=' + r.next + ' lapses=' + r.lapses,
            ),
          );
        });
        ctx.root.appendChild(block);
      });
    }
    if (resp && resp.status === 401) {
      ctx.root.appendChild(
        el('p', 'quiz-reconnect', t(ctx.root, 'data-reconnect-label'), 'status'),
      );
      wireCopyFallback(ctx);
      return;
    }
    persistLine(ctx.line);
    const msg = resp
      ? t(ctx.root, 'data-score-failed-label', { status: resp.status })
      : t(ctx.root, 'data-network-failed-label');
    const wrap = el('div', 'quiz-error', null, 'alert');
    wrap.appendChild(el('p', null, msg));
    const retry = document.createElement('button');
    retry.type = 'button';
    retry.className = 'quiz-retry';
    retry.textContent = t(ctx.root, 'data-retry-label');
    retry.addEventListener('click', () => ctx.postScore());
    wrap.appendChild(retry);
    ctx.root.appendChild(wrap);
  }

  function copyText(text, btn, copiedLabel, onSuccess, onFailure) {
    const done = () => {
      if (!btn) return;
      const original = btn.textContent;
      btn.textContent = copiedLabel;
      onSuccess?.();
      setTimeout(() => {
        btn.textContent = original;
      }, 1200);
    };
    const fallback = () => {
      let copied = false;
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        copied = document.execCommand('copy');
      } catch {}
      document.body.removeChild(ta);
      if (copied) done();
      else onFailure?.();
    };
    try {
      if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
        return;
      }
    } catch {}
    fallback();
  }

  function initQuiz(root) {
    const items = Array.from(root.querySelectorAll('.quiz-item'));
    if (!items.length) return;
    const outcomes = Array(items.length).fill(null);
    const resultEl = root.querySelector('.quiz-result');
    const copyBtn = root.querySelector('.quiz-copy');
    const copyStatus = root.querySelector('.quiz-copy-status');
    const releases = root.getAttribute('data-releases');
    const confOn = root.getAttribute('data-confidence');
    const confVals = Array(items.length).fill(null);
    const undoLabel = t(root, 'data-undo-label');
    let progressEl = null;
    const replay = !!releases && alreadyUnsealed();
    if (replay) unseal(releases);

    if (items.length > 1) {
      progressEl = document.createElement('p');
      progressEl.className = 'quiz-progress';
      root.insertBefore(progressEl, items[0]);
    }

    const updateProgress = () => {
      if (!progressEl) return;
      const answered = outcomes.filter((o) => o !== null).length;
      progressEl.textContent = t(root, 'data-progress-label', {
        n: answered,
        total: items.length,
      });
    };

    const selectResult = () => {
      if (!resultEl) return;
      const selection = window.getSelection();
      if (!selection) return;
      const range = document.createRange();
      range.selectNodeContents(resultEl);
      selection.removeAllRanges();
      selection.addRange(range);
    };

    updateProgress();

    items.forEach((item, i) => {
      const correct = Number(item.getAttribute('data-correct'));
      const buttons = Array.from(item.querySelectorAll('.quiz-btn'));
      const fb = item.querySelector('.quiz-fb');
      let fbText = '';
      if (fb) {
        fbText = fb.textContent;
        fb.textContent = '';
        fb.hidden = false;
      }
      let timer = null;
      let countdownTimer = null;
      let chosen = -1;
      let conf = null;

      // Optional 1-5 confidence rating, captured BEFORE the answer reveal. A
      // scheduling signal only (hypercorrection-aware re-teach), never a
      // comprehension booster. Opt-in per quiz via data-confidence; absent, this
      // block does not run and the result line is unchanged.
      if (confOn) {
        const confWrap = document.createElement('div');
        confWrap.className = 'quiz-conf';
        confWrap.setAttribute('role', 'group');
        confWrap.setAttribute('aria-label', t(root, 'data-confidence-legend'));
        const confLabel = document.createElement('span');
        confLabel.className = 'quiz-conf-label';
        confLabel.textContent = t(root, 'data-confidence-label');
        confWrap.appendChild(confLabel);
        for (let c = 1; c <= 5; c++) {
          const cb = document.createElement('button');
          cb.type = 'button';
          cb.className = 'quiz-conf-btn';
          cb.textContent = String(c);
          cb.setAttribute('aria-pressed', 'false');
          cb.setAttribute('aria-label', t(root, 'data-confidence-option-label', { n: c }));
          cb.addEventListener('click', () => {
            if (item.hasAttribute('data-answered') || timer !== null) return;
            conf = c;
            confWrap.querySelectorAll('.quiz-conf-btn').forEach((b) => {
              b.removeAttribute('data-on');
              b.setAttribute('aria-pressed', 'false');
            });
            cb.setAttribute('data-on', '');
            cb.setAttribute('aria-pressed', 'true');
          });
          confWrap.appendChild(cb);
        }
        const q = item.querySelector('.quiz-q');
        item.insertBefore(confWrap, q ? q.nextSibling : null);
      }

      const undo = document.createElement('button');
      undo.type = 'button';
      undo.className = 'quiz-undo';
      undo.textContent = undoLabel;
      undo.hidden = true;
      item.appendChild(undo);

      const setDisabled = (on) => {
        buttons.forEach((b) => {
          if (on) b.setAttribute('aria-disabled', 'true');
          else b.removeAttribute('aria-disabled');
        });
      };

      const clearCountdown = () => {
        if (countdownTimer !== null) clearInterval(countdownTimer);
        countdownTimer = null;
        undo.textContent = undoLabel;
      };

      const updateCountdown = (commitAt) => {
        const seconds = Math.max(0, Math.ceil((commitAt - Date.now()) / 1000));
        undo.textContent = `${undoLabel} (${seconds})`;
      };

      const lock = () => {
        timer = null;
        clearCountdown();
        item.removeAttribute('data-pending');
        item.setAttribute('data-answered', '');
        const focusWasOnUndo = document.activeElement === undo;
        undo.hidden = true;
        const right = chosen === correct;
        buttons[chosen].setAttribute('data-state', right ? 'right' : 'wrong');
        if (!right && buttons[correct]) buttons[correct].setAttribute('data-state', 'right');
        setDisabled(true);
        if (fb) fb.textContent = fbText;
        if (focusWasOnUndo) buttons[chosen].focus();

        navigator.vibrate?.(right ? 50 : [50, 100, 50]);

        confVals[i] = conf;
        outcomes[i] = right ? 'right' : 'wrong';
        updateProgress();
        if (outcomes.every((o) => o !== null)) finish();
      };

      undo.addEventListener('click', () => {
        if (timer === null) return;
        clearTimeout(timer);
        timer = null;
        clearCountdown();
        item.removeAttribute('data-pending');
        buttons.forEach((b) => b.removeAttribute('data-state'));
        setDisabled(false);
        undo.hidden = true;
        const back = buttons[chosen] || buttons[0];
        chosen = -1;
        if (back) back.focus();
      });

      buttons.forEach((btn, b) => {
        btn.addEventListener('click', () => {
          if (item.hasAttribute('data-answered') || timer !== null) return;
          chosen = b;
          item.setAttribute('data-pending', '');
          btn.setAttribute('data-state', 'chosen');
          setDisabled(true);
          undo.hidden = false;
          const commitAt = Date.now() + UNDO_MS;
          updateCountdown(commitAt);
          countdownTimer = setInterval(() => updateCountdown(commitAt), 1000);
          timer = setTimeout(lock, UNDO_MS);
        });
      });
    });

    function finish() {
      const label = t(root, 'data-label');
      const lesson = root.getAttribute('data-lesson');
      const head = lesson ? `${label} ${lesson}` : label;
      const line =
        head +
        ': ' +
        outcomes
          .map((o, i) => `${i + 1} ${o}${confVals[i] != null ? '/' + confVals[i] : ''}`)
          .join(', ');
      if (resultEl) resultEl.textContent = line;
      const ctx = {
        root,
        releases,
        replay,
        line,
        resultEl,
        copyBtn,
        copyStatus,
        copyText,
        selectResult,
        unseal,
        rememberUnsealed,
      };
      const serveMode = !!(window.__TEACH_SERVE && window.__TEACH_TOKEN);
      if (serveMode) {
        const payload = JSON.stringify({
          lesson: root.getAttribute('data-lesson'),
          line: line,
          token: window.__TEACH_TOKEN,
        });
        const postScore = () =>
          fetch('/score', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: payload,
          })
            .then(function (resp) {
              return handleScoreResponse(resp, ctx);
            })
            .catch(function () {
              handleScoreResponse(null, ctx);
            });
        ctx.postScore = postScore;
        postScore();
        return;
      }
      if (releases && !replay) wireCopyFallback(ctx);
      if (releases) {
        unseal(releases, true);
        rememberUnsealed();
      }
    }
  }

  const init = () => {
    document.querySelectorAll('.quiz').forEach((q) => initQuiz(q));
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
