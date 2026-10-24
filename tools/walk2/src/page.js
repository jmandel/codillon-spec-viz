(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const FILE = location.protocol === 'file:';
  const BASE = FILE ? 'https://joshuamandel.com/codillon-spec-viz/editor/v2/' : '../editor/v2/';

  // ---------------- table of contents: highlight the section in view ----------------
  (() => {
    const links = $$('nav.toc a'), secs = links.map(a => $(a.getAttribute('href')));
    const on = () => {
      let k = 0; secs.forEach((s, i) => { if (s && s.getBoundingClientRect().top < 120) k = i; });
      links.forEach((a, i) => a.classList.toggle('on', i === k));
    };
    addEventListener('scroll', on, { passive: true }); on();
  })();

  // ---------------- live editor embeds ----------------
  // The editor (embed=1) posts {type:'codillon-height'} with its full content height, which is ~45 px per line.
  // A listing is far taller than a screen, so each frame is sized to min(content, cap) and scrolls inside;
  // when the page and the editor share an origin, the frame is scrolled to the line (or panel) the text discusses.
  const FRAMES = [];
  const cap = () => Math.max(420, Math.min(860, Math.round(innerHeight * 0.82)));
  addEventListener('message', e => {
    const m = e.data; if (!m || m.type !== 'codillon-height') return;
    const fr = FRAMES.find(x => x.f.contentWindow === e.source); if (!fr) return;
    fr.reported = Math.ceil(m.height); size(fr);
  });
  function size(fr) {
    const h = Math.max(240, Math.min(cap(), fr.reported || cap()));
    if (Math.abs(fr.f.clientHeight - h) > 2) fr.f.style.height = h + 'px';
  }
  addEventListener('resize', () => FRAMES.forEach(size));
  // scroll the frame to its target once the editor has laid the program out
  function aim(fr) {
    const want = fr.target, token = ++fr.token;
    if (!want || FILE) return;
    let tries = 0;
    const go = () => {
      if (token !== fr.token) return;
      try {
        const w = fr.f.contentWindow, d = fr.f.contentDocument;
        if (!d || !w) throw 0;
        let el = null;
        if (want.sel) el = d.querySelector(want.sel);
        else if (want.line != null) { const ls = d.querySelectorAll('.textentry > .line'); if (ls.length > want.line) el = ls[want.line]; }
        if (el && d.querySelectorAll('.textentry > .line').length > 3) {
          if (want.soft && fr.settle === 0 && w.scrollY > 0) return;   // the editor already scrolled to what changed
          const y = el.getBoundingClientRect().top + w.scrollY - (want.sel ? 8 : 110);
          w.scrollTo(0, Math.max(0, y));
          if (++fr.settle < 3) setTimeout(go, 700);   // the editor may re-layout once after its first run
          return;
        }
      } catch (err) { if (tries > 3) return; }
      if (++tries < 40) setTimeout(go, 250);
    };
    fr.settle = 0; setTimeout(go, 400);
  }
  function liveEmbed(el, id) {
    el.classList.add('live');
    el.innerHTML = `<div class="livehead"><span class="livetag">LIVE · the real editor</span> <span class="livecap"></span><a class="openlink" target="_blank" rel="noopener">open in editor ↗</a><span class="phonehint">On a narrow screen the editor shrinks the whole listing to fit. Pinch to zoom, or open it in the editor to read it at full size.</span></div><iframe loading="lazy" title="Refined Codillon editor (${id})" style="height:${cap()}px"></iframe>`;
    const fr = { el, f: $('iframe', el), a: $('a.openlink', el), cp: $('.livecap', el), token: 0, loads: 0, reported: 0, target: null, frag: null };
    fr.f.addEventListener('load', () => { fr.ready = true; aim(fr); });
    FRAMES.push(fr);
    fr.set = (st) => {
      fr.frag = st.frag; fr.target = st.sel ? { sel: st.sel } : (st.line != null ? { line: st.line, soft: !!st.soft } : null);
      if (FILE) {
        fr.f.style.display = 'none';
        if (!$('.livefile', el)) el.insertAdjacentHTML('beforeend', '<div class="livefile">This page was opened from a file, so the live editor is not embedded. Use “open in editor ↗” for the deployed editor in this state, or serve the repository over HTTP.</div>');
      } else {
        // a session replays only on load (the editor ignores a session hashchange), so a new turn reloads the frame
        const src = BASE + (st.reload ? '?r=' + (++fr.loads) : '') + '#' + st.frag + '&embed=1';
        const had = fr.f.getAttribute('src');
        if (had !== src) { if (st.reload) fr.ready = false; fr.f.setAttribute('src', src); if (had && !st.reload) aim(fr); }   // fragment-only change: the editor reacts to hashchange
      }
      fr.a.href = BASE + '#' + st.frag; fr.cp.innerHTML = st.cap || '';
    };
    return fr;
  }

  // ---------------- the states each embed can show ----------------
  const S = window.STATES;
  const EMB = {};
  $$('.emb').forEach(el => { EMB[el.dataset.id] = liveEmbed(el, el.dataset.id); });
  for (const id of Object.keys(EMB)) {
    const list = S[id]; if (!list) continue;
    const seg = $(`.seg[data-for="${id}"]`), note = $(`#${id}-note`);
    const pick = k => {
      const st = list[k]; EMB[id].set(st);
      if (seg) $$('button', seg).forEach((b, i) => b.classList.toggle('on', i === k));
      if (note) note.innerHTML = st.note || '';
    };
    if (seg) list.forEach((st, k) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = st.label; b.onclick = () => pick(k); seg.appendChild(b); });
    pick(0);
  }

  // ---------------- the vericoding session stepper ----------------
  (() => {
    const fr = EMB.e6; if (!fr) return;
    const SS = window.SESSIONS, names = Object.keys(SS);
    let cur = 'isqrt', turn = 1;
    const seg = $('#sess-seg'), turns = $('#turns'), note = $('#tnote'), kv = $('#tkv'), next = $('#tnext');
    names.forEach(n => { const b = document.createElement('button'); b.type = 'button'; b.textContent = n; b.onclick = () => { cur = n; show(1); }; seg.appendChild(b); });
    const label = { accepted: ['acc', 'accepted'], rejected: ['rej', 'rejected (crossed the boundary)'], 'not-accepted': ['na', 'not accepted yet'] };
    function show(t, keepFrame) {
      const s = SS[cur]; turn = Math.max(1, Math.min(s.turns.length, t));
      $$('button', seg).forEach(b => b.classList.toggle('on', b.textContent === cur));
      turns.innerHTML = '';
      s.turns.forEach((tt, i) => {
        const b = document.createElement('button'); b.type = 'button'; b.textContent = i + 1;
        b.className = (i + 1 === turn ? 'on ' : '') + (tt.expect === 'rejected' ? 'rej' : tt.expect === 'accepted' ? 'acc' : '');
        b.title = label[tt.expect][1]; b.onclick = () => show(i + 1); turns.appendChild(b);
      });
      next.disabled = turn >= s.turns.length;
      const tt = s.turns[turn - 1];
      note.innerHTML = `<span class="who">turn ${turn}/${s.turns.length} · scripted LLM:</span>${esc(tt.note)}`;
      kv.innerHTML = `<b>recorded outcome:</b> <span class="${label[tt.expect][0]}">${label[tt.expect][1]}</span><span id="kvlive"></span>`;
      if (keepFrame) { fr.a.href = BASE + `#session=${cur}&turn=${turn}`; return watch(); }
      fr.set({ frag: `session=${cur}&turn=${turn}`, line: tt.line, soft: true, reload: true, cap: `<b>${esc(s.title)}</b> · turn ${turn} of ${s.turns.length}. The frame opens at the first line this turn edited; the editor’s session panel (with ▶ next turn) is below the code.` });
      watch();
    }
    next.onclick = () => show(turn + 1);
    // mirror the kernel's own verdict from the editor's session panel (same origin only)
    let wt = null;
    function watch() {
      clearInterval(wt); let n = 0;
      wt = setInterval(() => {
        if (++n > 40) clearInterval(wt);
        try {
          const d = fr.f.contentDocument, v = d && d.querySelector('.vc-verdict'), tn = d && d.querySelector('.vc-row .vc-dim');
          if (!v || !fr.ready) return;
          const m = tn && /turn (\d+)\//.exec(tn.textContent);
          if (m && +m[1] !== turn) { if (+m[1] >= 1) show(+m[1], true); return; }   // the reader stepped inside the editor
          const bad = v.classList.contains('vc-bad');
          $('#kvlive').innerHTML = ` · <b>kernel, live:</b> <span class="${bad ? 'rej' : /^accepted/.test(v.textContent) ? 'acc' : 'na'}">${esc(v.textContent)}</span>`;
        } catch (err) { clearInterval(wt); }
      }, 500);
    }
    const esc = s => String(s).replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));
    show(1);
  })();
})();
