/* quiz.js — reusable quiz widget for a lesson. Self-contained, works on file://.
 * Markup contract and behaviour: skills/teach/references/COMPONENTS.md § Quiz.
 * teach-template-version: 18
 */
(function () {
  'use strict';

  const SEAL_KEY = 'teach:unsealed:' + location.pathname;
  const UNDO_MS = 3000;

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
      note.textContent = note.getAttribute('data-unsealed-label') || 'Lesson unsealed.';
      note.classList.add('is-unsealed');
    } else note.remove();
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
    const undoLabel = root.getAttribute('data-undo-label') || 'Undo';
    const copiedLabel = root.getAttribute('data-copied-label') || 'Copied';
    const copyFailedLabel =
      root.getAttribute('data-copy-failed-label') ||
      'Copy failed. Result selected; copy it manually.';
    const copiedStatus =
      root.getAttribute('data-copied-status') ||
      'Result copied. Paste it into your next message to your teacher.';
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
      progressEl.textContent = `${answered} of ${items.length} answered`;
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
        confWrap.setAttribute('aria-label', 'How sure are you, 1 to 5?');
        const confLabel = document.createElement('span');
        confLabel.className = 'quiz-conf-label';
        confLabel.textContent = 'How sure?';
        confWrap.appendChild(confLabel);
        for (let c = 1; c <= 5; c++) {
          const cb = document.createElement('button');
          cb.type = 'button';
          cb.className = 'quiz-conf-btn';
          cb.textContent = String(c);
          cb.setAttribute('aria-pressed', 'false');
          cb.setAttribute('aria-label', c + ' out of 5');
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
      const label = root.getAttribute('data-label') || 'Cold open';
      const lesson = root.getAttribute('data-lesson');
      const head = lesson ? `${label} ${lesson}` : label;
      const line =
        head +
        ': ' +
        outcomes
          .map((o, i) => `${i + 1} ${o}${confVals[i] != null ? '/' + confVals[i] : ''}`)
          .join(', ');
      if (resultEl) resultEl.textContent = line;
      if (copyBtn && releases && !replay) {
        copyBtn.hidden = false;
        copyBtn.addEventListener('click', () => {
          if (copyStatus) copyStatus.textContent = '';
          copyText(
            line,
            copyBtn,
            copiedLabel,
            () => {
              if (copyStatus) copyStatus.textContent = copiedStatus;
            },
            () => {
              selectResult();
              if (copyStatus) copyStatus.textContent = copyFailedLabel;
            },
          );
        });
      }
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
