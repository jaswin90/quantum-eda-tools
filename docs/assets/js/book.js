// Page script for "From Laboratory to Foundry".
// Kept deliberately small. It provides what the library at jaswin90.github.io/library/ expects
// from a book: a dark-mode toggle stored under the site-wide key "site-theme", a window.Book
// object for the library shim, and a "book:ready" event. The review has no quizzes, so it keeps
// no reading progress and shows no sign-in button.
(function () {
  'use strict';
  var KEY = 'site-theme';
  function safeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function setTheme(t) {
    if (t) document.documentElement.setAttribute('data-theme', t);
    else document.documentElement.removeAttribute('data-theme');
    safeSet(KEY, t || '');
  }
  function currentTheme() {
    var t = document.documentElement.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // The library shim replaces renderAuth; with no #auth-slot on the page it renders nothing.
  window.Book = { renderAuth: function () {} };

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('theme-btn');
    if (btn) btn.addEventListener('click', function () { setTheme(currentTheme() === 'dark' ? 'light' : 'dark'); });
    document.dispatchEvent(new CustomEvent('book:ready'));
  });
})();
