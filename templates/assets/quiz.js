/* quiz.js — reusable quiz widget for a lesson. Self-contained, works on file://.
 * Markup contract and behaviour: skills/teach/references/DESIGN.md § Components.
 * teach-template-version: 12
 */
(function () {
  'use strict';

  var SEAL_KEY = 'teach:unsealed:' + location.pathname;
  var UNDO_MS = 3000;

  function alreadyUnsealed() {
    try {
      return localStorage.getItem(SEAL_KEY) === '1';
    } catch (e) {
      return false;
    }
  }

  function rememberUnsealed() {
    try {
      localStorage.setItem(SEAL_KEY, '1');
    } catch (e) {}
  }

  function unseal(targetId, announce) {
    var sealed = document.getElementById(targetId);
    if (!sealed) return;
    sealed.classList.remove('sealed');
    sealed.removeAttribute('inert');
    var note = document.querySelector('.seal-note');
    if (!note) return;
    if (announce) {
      note.textContent = note.getAttribute('data-unsealed-label') || 'Lesson unsealed.';
      note.classList.add('is-unsealed');
    } else note.remove();
  }

  function copyText(text, btn, copiedLabel, onSuccess, onFailure) {
    var done = function () {
      if (!btn) return;
      var original = btn.textContent;
      btn.textContent = copiedLabel;
      if (onSuccess) onSuccess();
      setTimeout(function () {
        btn.textContent = original;
      }, 1200);
    };
    var fallback = function () {
      var copied = false;
      var ta = document.createElement('textarea');
      ta.value = text;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        copied = document.execCommand('copy');
      } catch (e) {}
      document.body.removeChild(ta);
      if (copied) done();
      else if (onFailure) onFailure();
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
        return;
      }
    } catch (e) {}
    fallback();
  }

  function initQuiz(root) {
    var items = Array.prototype.slice.call(root.querySelectorAll('.quiz-item'));
    if (!items.length) return;
    var outcomes = new Array(items.length).fill(null);
    var resultEl = root.querySelector('.quiz-result');
    var copyBtn = root.querySelector('.quiz-copy');
    var copyStatus = root.querySelector('.quiz-copy-status');
    var releases = root.getAttribute('data-releases');
    var undoLabel = root.getAttribute('data-undo-label') || 'Undo';
    var copiedLabel = root.getAttribute('data-copied-label') || 'Copied';
    var copyFailedLabel =
      root.getAttribute('data-copy-failed-label') ||
      'Copy failed. Result selected; copy it manually.';
    var copiedStatus =
      root.getAttribute('data-copied-status') ||
      'Result copied. Paste it into your next message to your teacher.';
    var progressEl = null;
    var replay = !!releases && alreadyUnsealed();
    if (replay) unseal(releases);

    if (items.length > 1) {
      progressEl = document.createElement('p');
      progressEl.className = 'quiz-progress';
      root.insertBefore(progressEl, items[0]);
    }

    function updateProgress() {
      if (!progressEl) return;
      var answered = outcomes.filter(function (outcome) {
        return outcome !== null;
      }).length;
      progressEl.textContent = answered + ' of ' + items.length + ' answered';
    }

    function selectResult() {
      if (!resultEl) return;
      var selection = window.getSelection();
      if (!selection) return;
      var range = document.createRange();
      range.selectNodeContents(resultEl);
      selection.removeAllRanges();
      selection.addRange(range);
    }

    updateProgress();

    items.forEach(function (item, i) {
      var correct = parseInt(item.getAttribute('data-correct'), 10);
      var buttons = Array.prototype.slice.call(item.querySelectorAll('.quiz-btn'));
      var fb = item.querySelector('.quiz-fb');
      var fbText = '';
      if (fb) {
        fbText = fb.textContent;
        fb.textContent = '';
        fb.hidden = false;
      }
      var timer = null;
      var countdownTimer = null;
      var chosen = -1;

      var undo = document.createElement('button');
      undo.type = 'button';
      undo.className = 'quiz-undo';
      undo.textContent = undoLabel;
      undo.hidden = true;
      item.appendChild(undo);

      function setDisabled(on) {
        buttons.forEach(function (b) {
          if (on) b.setAttribute('aria-disabled', 'true');
          else b.removeAttribute('aria-disabled');
        });
      }

      function clearCountdown() {
        if (countdownTimer !== null) clearInterval(countdownTimer);
        countdownTimer = null;
        undo.textContent = undoLabel;
      }

      function updateCountdown(commitAt) {
        var seconds = Math.max(0, Math.ceil((commitAt - Date.now()) / 1000));
        undo.textContent = undoLabel + ' (' + seconds + ')';
      }

      function lock() {
        timer = null;
        clearCountdown();
        item.removeAttribute('data-pending');
        item.setAttribute('data-answered', '');
        var focusWasOnUndo = document.activeElement === undo;
        undo.hidden = true;
        var right = chosen === correct;
        buttons[chosen].setAttribute('data-state', right ? 'right' : 'wrong');
        if (!right && buttons[correct]) buttons[correct].setAttribute('data-state', 'right');
        setDisabled(true);
        if (fb) fb.textContent = fbText;
        if (focusWasOnUndo) buttons[chosen].focus();
        outcomes[i] = right ? 'right' : 'wrong';
        updateProgress();
        if (
          outcomes.every(function (o) {
            return o !== null;
          })
        )
          finish();
      }

      undo.addEventListener('click', function () {
        if (timer === null) return;
        clearTimeout(timer);
        timer = null;
        clearCountdown();
        item.removeAttribute('data-pending');
        buttons.forEach(function (b) {
          b.removeAttribute('data-state');
        });
        setDisabled(false);
        undo.hidden = true;
        var back = buttons[chosen] || buttons[0];
        chosen = -1;
        if (back) back.focus();
      });

      buttons.forEach(function (btn, b) {
        btn.addEventListener('click', function () {
          if (item.hasAttribute('data-answered') || timer !== null) return;
          chosen = b;
          item.setAttribute('data-pending', '');
          btn.setAttribute('data-state', 'chosen');
          setDisabled(true);
          undo.hidden = false;
          var commitAt = Date.now() + UNDO_MS;
          updateCountdown(commitAt);
          countdownTimer = setInterval(function () {
            updateCountdown(commitAt);
          }, 1000);
          timer = setTimeout(lock, UNDO_MS);
        });
      });
    });

    function finish() {
      var label = root.getAttribute('data-label') || 'Cold open';
      var lesson = root.getAttribute('data-lesson');
      var line =
        (lesson ? label + ' ' + lesson : label) +
        ': ' +
        outcomes
          .map(function (o, i) {
            return i + 1 + ' ' + o;
          })
          .join(', ');
      if (resultEl) resultEl.textContent = line;
      if (copyBtn && releases && !replay) {
        copyBtn.hidden = false;
        copyBtn.addEventListener('click', function () {
          if (copyStatus) copyStatus.textContent = '';
          copyText(
            line,
            copyBtn,
            copiedLabel,
            function () {
              if (copyStatus) copyStatus.textContent = copiedStatus;
            },
            function () {
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

  function init() {
    var quizzes = document.querySelectorAll('.quiz');
    for (var i = 0; i < quizzes.length; i++) initQuiz(quizzes[i]);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
