(function () {
  'use strict';
  function setOpen(fig, open) {
    fig.classList.toggle('open', open);
    var b = fig.querySelector('button.zoom');
    if (b) { b.setAttribute('aria-expanded', open ? 'true' : 'false'); b.textContent = open ? 'shrink' : 'enlarge'; }
  }
  document.addEventListener('click', function (ev) {
    var t = ev.target;
    if (!(t instanceof Element)) return;
    if (t.closest('a')) return;
    var btn = t.closest('button.zoom');
    var fig = btn ? btn.closest('figure') : t.closest('figure.thumb');
    if (!fig) return;
    if (!btn && fig.classList.contains('open') && fig.querySelector('.svgbox').scrollWidth > fig.querySelector('.svgbox').clientWidth + 4) return;
    var open = !fig.classList.contains('open');
    setOpen(fig, open);
    if (!open && fig.getBoundingClientRect().top < 0) fig.scrollIntoView({ block: 'start' });
  });
  // scroll spy for the sticky index
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.idx a[href^="#"]'));
  var byId = {};
  links.forEach(function (a) { byId[a.getAttribute('href').slice(1)] = a; });
  var targets = Object.keys(byId).map(function (id) { return document.getElementById(id); }).filter(Boolean);
  if (!('IntersectionObserver' in window) || !targets.length) return;
  var visible = {};
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
    var cur = null, curSec = null;
    targets.forEach(function (el) {
      if (!visible[el.id]) return;
      if (el.tagName === 'ARTICLE') { if (!cur) cur = el.id; }
      else if (!curSec) curSec = el.id;
    });
    links.forEach(function (a) { a.classList.remove('on'); });
    var pick = cur ? byId[cur] : (curSec ? byId[curSec] : null);
    if (pick) {
      pick.classList.add('on');
      var nav = pick.closest('nav');
      if (nav && nav.scrollWidth > nav.clientWidth) {
        var r = pick.getBoundingClientRect(), nr = nav.getBoundingClientRect();
        if (r.left < nr.left || r.right > nr.right) nav.scrollLeft += (r.left - nr.left) - nr.width / 3;
      }
    }
  }, { rootMargin: '-15% 0px -60% 0px' });
  targets.forEach(function (el) { io.observe(el); });
})();
