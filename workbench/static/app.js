/* Oracle7 Workbench - page logic. Talks only to the local server that served it (127.0.0.1). */
(function () {
  "use strict";
  const $ = id => document.getElementById(id);
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const newId = () => (crypto.getRandomValues(new Uint32Array(2)).join("") + "abcdefgh").replace(/[^0-9a-z]/g, "").slice(0, 16);
  const store = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } } };
  // the conversation id is also the core's session: reopening a conversation carries on its context
  let SID = /^[a-z0-9]{6,40}$/.test(store.get("o7wb.conv") || "") ? store.get("o7wb.conv") : newId();
  store.set("o7wb.conv", SID);
  const turns = [];
  let head = "", explorer = null, specData = null, pendingExamples = [], filmTurns = new Set(), filmSeen = new Set();

  async function api(path, body) {
    const r = await fetch(path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const j = await r.json().catch(() => ({ error: "bad reply" }));
    if (!r.ok) throw new Error(j.error || ("HTTP " + r.status));
    return j;
  }

  // ------------------------------------------------------------------ log pane
  function log(kind, text, cls) {
    const li = document.createElement("li");
    const t = new Date().toTimeString().slice(0, 8);
    li.innerHTML = `<time>${t}</time><span class="k ${cls || ""}">${esc(kind)}</span><span>${esc(text)}</span>`;
    const ol = $("log"); ol.appendChild(li);
    while (ol.children.length > 400) ol.removeChild(ol.firstChild);
    ol.scrollTop = ol.scrollHeight;
  }
  $("log-clear").onclick = () => { $("log").innerHTML = ""; };

  // ------------------------------------------------------------------ diagram
  try {
    explorer = O7Explorer($("diagram"), { mode: "improve", select: "L2",
      palette: { accent: 0x946d1e, lit: 0xc0602e, fresh: 0xc0602e, spec: 0x5c4416, hazard: 0xc49132, store: 0x2a3b52 },
      onSelect(id) { const s = O7Explorer.data.STAGES.find(x => x.id === id); if (s) log("diagram", s.name + ": " + s.blurb); } });
  } catch (e) { $("diagram").insertAdjacentHTML("beforeend", `<p class="muted" style="padding:16px">The diagram needs WebGL (${esc(e.message)}).</p>`); }
  document.querySelectorAll(".views [data-view]").forEach(b => b.onclick = () => {
    document.querySelectorAll(".views [data-view]").forEach(x => x.classList.toggle("on", x === b)); explorer && explorer.setView(b.dataset.view); });
  let allLabels = false;
  $("labels-all").onclick = () => { allLabels = !allLabels; explorer && explorer.setShowAll(allLabels); $("labels-all").classList.toggle("on", allLabels); };

  // ------------------------------------------------------------------ state
  async function refreshState() {
    const s = await api("/api/state");
    head = s.head;
    $("f-head").textContent = "core " + String(s.head).replace("oracle_release_runtime_", "");
    $("f-yours").textContent = s.yours.length + " of yours";
    $("f-journal").textContent = s.journal ? "gap journal on" : "gap journal off";
    $("f-journal").classList.toggle("on", s.journal);
    $("g-on").checked = s.journal;
    s.yours.forEach(id => explorer && explorer.addModule("S", "Yours: " + id));
    return s;
  }

  // ------------------------------------------------------------------ ask
  function renderAnswer(text) {
    const t = String(text || "");
    if (t.includes("```")) return t.split("```").map((p, i) => i % 2 ? `<pre>${esc(p.replace(/^[a-z]*\n/, ""))}</pre>` : esc(p)).join("");
    const m = t.match(/^([\s\S]*?)((?:^|\n)(?:def |import |from |class )[\s\S]*)$/);
    return m ? esc(m[1]) + `<pre>${esc(m[2].replace(/^\n/, ""))}</pre>` : esc(t);
  }
  const stepNames = tr => (tr || []).filter(x => x[1]).map(x => x[1]);
  // one turn's answer, its path and its controls: used live and when a saved conversation is reopened
  function renderTurn(box, t, live) {
    const declined = t.status !== "answered";
    box.classList.toggle("declined", declined);
    box.querySelector(".a").className = "a";
    box.querySelector(".a").innerHTML = renderAnswer(t.response || (declined ? "(declined)" : ""));
    const lit = live && explorer ? explorer.trace(t.trace, declined) : [];
    const mine = /^yours:([a-z0-9-]+)/.exec(t.path || "");
    const when = t.t ? new Date(t.t * 1000).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) + " · " : "";
    box.insertAdjacentHTML("beforeend", `${t.why ? `<div class="why">${esc(t.why)}</div>` : ""}<div class="meta"><span>${esc(when)}<b>${esc(t.status)}</b> · ${t.ms} ms</span>` +
      `<span>${esc((lit.length ? lit.map(x => x[1]) : stepNames(t.trace)).join(" → "))}</span>${mine ? `<span><b>your specialist: ${esc(mine[1])}</b></span>` : ""}` +
      `<button data-act="trace">show path</button><button data-act="film">film this</button><button data-act="raw">route</button></div>`);
    box.querySelector('[data-act="trace"]').onclick = () => explorer && explorer.trace(t.trace, declined);
    box.querySelector('[data-act="film"]').onclick = () => { filmTurns = new Set([t.n]); showTab("film"); renderFilmList(); record(); };
    box.querySelector('[data-act="raw"]').onclick = () => log("route", t.path);
    if (mine && live) {                             // marks teach your own specialists (tool specialists learn from them)
      box.querySelector(".meta").insertAdjacentHTML("beforeend", `<button data-act="right">✓ right</button><button data-act="wrong">✗ wrong</button>`);
      const mark = async right => {
        const f = await api("/api/feedback", { path: t.path, response: t.response, q: t.q, right });
        log("learn", f.learned ? `${mine[1]}: ${f.tool || "tool"} marked ${right ? "right" : "wrong"}; re-checking its lane` : f.note, f.learned ? "live" : "");
        box.querySelectorAll('[data-act="right"],[data-act="wrong"]').forEach(b => b.disabled = true);
      };
      box.querySelector('[data-act="right"]').onclick = () => mark(true);
      box.querySelector('[data-act="wrong"]').onclick = () => mark(false);
    }
    return lit;
  }
  function turnBox(q) {
    const hello = $("thread").querySelector(".hello"); if (hello) hello.hidden = true;
    const box = document.createElement("div"); box.className = "turn";
    box.innerHTML = `<div class="q">${esc(q)}</div><div class="a muted">reading…</div>`;
    $("thread").appendChild(box); return box;
  }
  async function ask(text, asQuestion) {
    text = text.trim(); if (!text) return;
    if (text.startsWith("/") && !asQuestion) { $("q").value = ""; return command(text); }
    const box = turnBox(text); $("thread").scrollTop = $("thread").scrollHeight;
    $("q").value = ""; $("ask").querySelector("button").disabled = true;
    log("ask", text, "live");
    try {
      const r = await api("/api/chat", { text, sid: SID });
      const declined = r.status !== "answered";
      const t = { q: text, ...r, t: Math.floor(Date.now() / 1000), n: turns.length + 1 }; turns.push(t);
      const lit = renderTurn(box, t, true);
      log(declined ? "declined" : "answered", `${r.ms} ms · ${lit.map(x => x[0] + ": " + x[1]).join(" → ") || r.path}`, declined ? "no" : "ok");
      if (declined && r.why_kind) log("why", r.why_kind + " - " + r.why);
      renderFilmList(); loadConvs();
    } catch (e) {
      box.querySelector(".a").textContent = "Error: " + e.message; log("error", e.message, "no");
    } finally { $("ask").querySelector("button").disabled = false; $("thread").scrollTop = $("thread").scrollHeight; }
  }
  $("ask").onsubmit = e => { e.preventDefault(); ask($("q").value); };
  $("q").addEventListener("keydown", e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); ask($("q").value); } });
  document.querySelectorAll(".tries button").forEach(b => b.onclick = () => ask(b.textContent));

  // ------------------------------------------------------------------ tabs
  function showTab(name) {
    document.querySelectorAll(".tabs button").forEach(b => b.classList.toggle("on", b.dataset.tab === name));
    document.querySelectorAll(".tab").forEach(t => t.classList.toggle("on", t.id === "t-" + name));
    if (name === "gaps") loadGaps();
    if (name === "build" || name === "share") loadYours();
    if (name === "film") renderFilmList();
    clearInterval(snTimer);
    if (name === "sensors") { loadSensors(); snTimer = setInterval(() => { if (!document.hidden) loadSensors(); }, 15000); }
  }
  document.querySelectorAll(".tabs button").forEach(b => b.onclick = () => showTab(b.dataset.tab));

  // ------------------------------------------------------------------ specialists
  const md = s => esc(s).split(/\n{2,}/).map(block => {
    if (/^#{1,3} /.test(block)) return block.replace(/^(#{1,3}) (.*)$/gm, (m, h, t) => `<h${h.length}>${t}</h${h.length}>`);
    if (/^- /m.test(block)) return "<ul>" + block.split(/\n/).filter(l => l.startsWith("- ")).map(l => `<li>${l.slice(2)}</li>`).join("") + "</ul>";
    return `<p>${block}</p>`;
  }).join("").replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/`([^`]+)`/g, "<code>$1</code>");
  let group = "All";
  function renderSpecs() {
    const f = $("s-find").value.trim().toLowerCase();
    const items = specData.items.filter(x => (group === "All" || x.group === group) &&
      (!f || (x.name + " " + x.id + " " + x.takes.join(" ")).toLowerCase().includes(f)));
    const yours = group === "All" || group === "Yours" ? specData.yours.filter(x => !f || x.id.includes(f)) : [];
    $("s-list").innerHTML = yours.map(x => `<div class="it" data-mine="${esc(x.id)}"><b>${esc(x.name)}</b><span class="state ${x.state}">${x.state}</span><small>yours · ${esc(x.note || "built in this workbench")}</small></div>`).join("") +
      items.slice(0, 400).map(x => `<div class="it" data-id="${esc(x.id)}"><b>${esc(x.name)}</b>` +
      `<span class="sc">${x.heldout ? `${x.heldout[0]}/${x.heldout[2]} <span class="muted">vs core ${x.heldout[1]}</span>` : ""}</span>` +
      `<small>${esc(x.group)} · ${esc(x.takes.join(", ") || x.id)}</small></div>`).join("") +
      (items.length ? "" : `<p class="muted">No specialist matches.</p>`);
    $("s-list").querySelectorAll("[data-id]").forEach(el => el.onclick = () => openCard(el.dataset.id));
    $("s-list").querySelectorAll("[data-mine]").forEach(el => el.onclick = () => { showTab("build"); openEditor(el.dataset.mine); });
  }
  async function openCard(id) {
    const x = specData.items.find(i => i.id === id); const c = $("s-card"); c.hidden = false;
    let body = "";
    if (x.card) { try { body = md((await api("/api/card?id=" + encodeURIComponent(x.card))).md); } catch (e) { body = ""; } }
    if (!body) body = `<h1>${esc(x.name)}</h1><p>${x.group === "Relation readers" ? "Reads one family of Wikidata relations (" + esc(x.takes.join(", ")) + ") from the relation store and answers with the record it read, both ends with ids." : "Takes: " + esc(x.takes.join(", "))}</p>`;
    c.innerHTML = body + (x.heldout ? `<p class="muted">Held-out exam, seen once: ${x.heldout[0]} of ${x.heldout[2]} right with it, ${x.heldout[1]} with the core alone. Admitted ${esc(x.admitted)}.</p>` : "");
    c.scrollIntoView({ block: "nearest" });
    log("card", x.name);
  }
  async function loadSpecs() {
    specData = await api("/api/specialists");
    const counts = {}; specData.items.forEach(x => { counts[x.group] = (counts[x.group] || 0) + 1; });
    const gs = [["All", specData.items.length]].concat(Object.entries(counts).sort((a, b) => b[1] - a[1])).concat([["Yours", specData.yours.length]]);
    $("s-groups").innerHTML = gs.map(([g, n]) => `<button data-g="${esc(g)}" class="${g === group ? "on" : ""}">${esc(g)} ${n}</button>`).join("");
    $("s-groups").querySelectorAll("button").forEach(b => b.onclick = () => { group = b.dataset.g; $("s-groups").querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b)); renderSpecs(); });
    $("f-spec").textContent = specData.items.length + " specialists";
    renderSpecs();
  }
  $("s-find").oninput = renderSpecs;

  async function loadSystems() {
    const s = await api("/api/systems");
    $("sys-about").textContent = s.about;
    $("sys-list").innerHTML = s.items.map(x => `<div class="sys"><h3>${esc(x.name)}<small>${esc(x.id)}</small></h3><p>${esc(x.does)}</p><ul>${x.measured.map(m => `<li>${esc(m)}</li>`).join("")}</ul><div class="use">runs on: ${esc(x.runs)} · for: ${esc(x.use)}</div></div>`).join("");
  }

  // ------------------------------------------------------------------ build
  let edId = null, edFile = null;
  async function loadYours() {
    specData = await api("/api/specialists");
    const rows = specData.yours.map(x => `<div class="it" data-id="${esc(x.id)}"><b>${esc(x.name)}</b><span class="state ${x.state}">${x.state}</span><small>${esc(x.id)}${x.note ? " · " + esc(x.note) : ""}</small></div>`).join("") || `<p class="muted">None yet. Start one, or add the worked example.</p>`;
    $("b-list").innerHTML = rows;
    $("b-list").querySelectorAll("[data-id]").forEach(el => el.onclick = () => openEditor(el.dataset.id));
    $("sh-list").innerHTML = specData.yours.map(x => `<div class="it"><b>${esc(x.name)}</b><span class="state ${x.state}">${x.state}</span><small>` +
      `<button class="btn" data-pack="${esc(x.id)}">Package for sharing</button> ` +
      (x.state === "admitted" ? `<button class="btn primary" data-reg="${esc(x.id)}" title="One Solana transaction: burns exactly 1 $ORACLE7 from your wallet and records this specialist's fingerprint">Register on Solana · 1 $ORACLE7</button> ` +
        `<button class="btn" data-att="${esc(x.id)}" title="Free: sign that this specialist passed its held-out exam on your machine">Attest</button> ` : "") +
      `<button class="btn" data-chk="${esc(x.id)}">Check on Solana</button></small><div class="reg-out" id="reg-${esc(x.id)}"></div></div>`).join("") || `<p class="muted">Build or import a specialist first.</p>`;
    $("sh-list").querySelectorAll("[data-pack]").forEach(b => b.onclick = () => pack(b.dataset.pack));
    $("sh-list").querySelectorAll("[data-reg]").forEach(b => b.onclick = () => solanaRecord(b.dataset.reg, "register"));
    $("sh-list").querySelectorAll("[data-att]").forEach(b => b.onclick = () => solanaRecord(b.dataset.att, "attest"));
    $("sh-list").querySelectorAll("[data-chk]").forEach(b => b.onclick = () => solanaCheck(b.dataset.chk));
  }
  async function openEditor(id, file) {
    const r = await api("/api/files?id=" + encodeURIComponent(id));
    edId = id; $("b-editor").hidden = false; $("b-title").textContent = id;
    const st = r.status; $("b-state").className = "state " + st.state; $("b-state").textContent = st.state;
    const files = r.files.filter(f => !/^(verdict_|shared_verdict_|exam_log)/.test(f));
    const organ = files.find(f => /^organ_/.test(f));
    file = file || edFile && files.includes(edFile) && edId === id ? file || edFile : organ || files[0];
    $("b-files").innerHTML = files.map(f => `<button class="${f === file ? "on" : ""}" data-f="${esc(f)}">${esc(f)}</button>`).join("");
    $("b-files").querySelectorAll("button").forEach(b => b.onclick = () => openEditor(id, b.dataset.f));
    edFile = file;
    $("b-text").value = (await api(`/api/file?id=${encodeURIComponent(id)}&name=${encodeURIComponent(file)}`)).text;
    renderVerdict(st.verdict);
  }
  async function save() {
    if (!edId) return;
    const r = await api("/api/file", { id: edId, name: edFile, text: $("b-text").value });
    $("b-state").className = "state " + r.status.state; $("b-state").textContent = r.status.state;
    log("saved", `${edId}/${edFile}${r.status.state === "changed" ? " - changed after its exam: out of your model until a new held-out set passes" : ""}`, "live");
    refreshState(); loadYours();
  }
  $("b-save").onclick = save;
  $("b-text").addEventListener("keydown", e => {
    if (e.key === "Tab") { e.preventDefault(); const t = e.target, s = t.selectionStart; t.setRangeText("    ", s, t.selectionEnd, "end"); }
    if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); save(); }
  });
  function renderVerdict(v) {
    if (!v) { $("b-verdict").innerHTML = `<p class="muted">No exam yet. The dev exam is free to repeat; the held-out exam uses its items once.</p>`; return; }
    const ok = c => c ? `<span class="pass">PASS</span>` : `<span class="fail">FAIL</span>`;
    const gain = v.with_specialist.ok - v.head.ok, wrongCap = Math.max(1, Math.floor(0.02 * v.n));
    $("b-verdict").innerHTML = `<div class="head">${esc(v.split === "heldout" ? "HELD-OUT" : "DEV")} EXAM · ${esc(v.decision)} · ${esc(v.time)}</div><table>` +
      `<tr><td>Domain</td><td>${ok(gain >= v.gain_needed)}</td><td>${v.with_specialist.ok}/${v.n} with it, ${v.head.ok}/${v.n} core alone: gain ${gain}, needs ${v.gain_needed}</td></tr>` +
      `<tr><td>No false yes</td><td>${ok(v.with_specialist.fy <= v.head.fy)}</td><td>${v.with_specialist.fy} must-decline answered (core: ${v.head.fy})</td></tr>` +
      `<tr><td>Few wrong</td><td>${ok(v.with_specialist.wrong <= wrongCap)}</td><td>${v.with_specialist.wrong} answered wrong, cap ${wrongCap}</td></tr>` +
      `<tr><td>Stays in lane</td><td>${ok(v.core.taken <= v.core.cap)}</td><td>takes ${v.core.taken} of ${v.core.n} general questions, cap ${v.core.cap}${v.core.examples.length ? ": " + esc(v.core.examples.slice(0, 3).join(" | ")) : ""}</td></tr>` +
      `<tr><td>Self</td><td>${ok(v.self_ok)}</td><td>identity questions stay the core's</td></tr>` +
      `<tr><td>Budget</td><td>${ok(v.p50_ms <= v.budget_ms)}</td><td>median ${v.p50_ms} ms, budget ${v.budget_ms} ms</td></tr></table>` +
      (v.fails.length ? `<div class="head">NOT RIGHT (${v.fails.length})</div><table>${v.fails.map(f => `<tr><td>${esc(f.q)}</td><td>expected ${esc(f.expected)}</td><td>${esc(f.by)}: ${esc(f.got || f.status)}</td></tr>`).join("")}</table>` : "");
  }
  async function exam(split) {
    if (!edId) return;
    if (split === "heldout" && !confirm("Run the held-out exam? Its items are used once: the same held-out set cannot be run again.")) return;
    await save();
    try { await api("/api/exam", { id: edId, split }); } catch (e) { log("exam", e.message, "no"); $("b-prog").textContent = e.message; return; }
    log("exam", `${edId}: ${split} exam started`, "live");
    const id = edId;
    const poll = async () => {
      const p = await api("/api/exam?id=" + encodeURIComponent(id));
      if (p.state === "running") { $("b-prog").textContent = `${p.phase || ""} ${p.done || 0}/${p.total || "?"}`; setTimeout(poll, 800); return; }
      if (p.state === "error") { $("b-prog").textContent = p.error; log("exam", id + ": " + p.error, "no"); return; }
      $("b-prog").textContent = p.result ? p.result.decision : "";
      if (p.result) { renderVerdict(p.result); log("verdict", `${id} ${p.result.split}: ${p.result.decision}${p.result.reasons.length ? " - " + p.result.reasons.join("; ") : ""}`, p.result.decision === "ADMIT" || p.result.decision === "WOULD PASS" ? "ok" : "no"); }
      if (p.result && p.result.decision === "ADMIT" && p.result.split !== "dev") { explorer && explorer.addModule("S", "Yours: " + id); explorer && explorer.trace([["S", "Yours: " + id]], false); log("grow", `${id} joined your model; the diagram has a new node`, "live"); }
      refreshState(); loadYours(); openEditor(id, edFile);
    };
    poll();
  }
  $("b-dev").onclick = () => exam("dev");
  $("b-held").onclick = () => exam("heldout");
  $("b-new").onsubmit = async e => {
    e.preventDefault();
    try {
      const r = await api("/api/new", { id: $("b-id").value.trim(), name: $("b-name").value.trim(), words: $("b-words").value, examples: pendingExamples });
      pendingExamples = []; log("new", "specialist " + r.id + " scaffolded in workbench/local/specialists/" + r.id, "live");
      $("b-new").reset(); await loadYours(); openEditor(r.id);
    } catch (err) { log("new", err.message, "no"); alert(err.message); }
  };
  $("b-example").onclick = async () => {
    try { const r = await api("/api/example", {}); log("new", "added the worked example: " + r.id, "live"); await loadYours(); openEditor(r.id); }
    catch (err) { log("example", err.message, "no"); }
  };

  // ------------------------------------------------------------------ gaps
  async function loadGaps() {
    const g = await api("/api/gaps");
    $("g-on").checked = g.on;
    if (!g.turns) { $("g-list").innerHTML = `<p class="muted">${g.on ? "The journal is on. Ask questions and the gaps appear here." : "The journal is off."}</p>`; return; }
    $("g-list").innerHTML = `<p class="muted">${g.turns} turns kept, ${g.declined} declined.</p>` + g.groups.map(gr => `<div class="gap"><b>${esc(gr.kind)} · ${gr.count}</b>` +
      (gr.themes.length ? gr.themes.map((t, i) => `<div class="theme"><span>“${esc(t.word)}” · ${t.count} questions<br><em>${esc(t.examples.join(" | "))}</em></span><button class="btn" data-k="${esc(gr.kind)}" data-i="${i}">Start a specialist</button></div>`).join("")
        : `<div class="muted">${esc(gr.examples.join(" | "))}</div>`) + `</div>`).join("");
    $("g-list").querySelectorAll("button[data-k]").forEach(b => b.onclick = () => {
      const t = g.groups.find(x => x.kind === b.dataset.k).themes[+b.dataset.i];
      pendingExamples = t.examples; showTab("build");
      $("b-id").value = t.word.replace(/[^a-z0-9-]/g, ""); $("b-name").value = t.word[0].toUpperCase() + t.word.slice(1); $("b-words").value = t.word; $("b-id").focus();
      log("gap", `starting a specialist for "${t.word}" with ${t.examples.length} of your questions as dev items`, "live");
    });
  }
  $("g-on").onchange = async () => { const r = await api("/api/journal", { on: $("g-on").checked }); log("journal", r.on ? "on: kept on this machine only" : "off", "live"); refreshState(); loadGaps(); };
  $("g-clear").onclick = async () => { if (!confirm("Delete the gap journal from this machine?")) return; await api("/api/journal/clear", {}); log("journal", "deleted", "live"); loadGaps(); };

  // ------------------------------------------------------------------ code
  $("e-style").onchange = () => { $("e-voice").hidden = $("e-style").value !== "custom"; };
  $("e-write").onclick = async () => {
    const topic = $("e-topic").value.trim();
    if (!topic) { $("e-res").textContent = "name a topic"; return; }
    const body = { topic, length: $("e-length").value, level: $("e-level").value, depth: $("e-depth").value, style: $("e-style").value,
                   voice_text: $("e-style").value === "custom" ? $("e-voice").value : "" };
    $("e-res").textContent = "composing from the record…"; $("e-out").hidden = true; log("essay", topic, "live");
    try {
      const r = await api("/api/essay", body);
      if (r.error) { $("e-res").textContent = r.error; return; }
      if (!r.sentences) { $("e-res").textContent = "no records about that topic, so no essay"; log("essay", "nothing on record: " + topic, "no"); return; }
      const band = r.level_band[1] >= 30 ? `grade ${r.level_band[0]}+` : `grades ${r.level_band[0]}-${r.level_band[1]}`;
      $("e-res").textContent = `${r.sentences} sentences from ${r.records_used} records · ${r.faithful} of ${r.sentences} checked word for word against their sources · reading grade ${r.reading_grade} (asked for ${band}${r.level_reached ? "" : "; the record could not get closer"}) · ${r.ms} ms · no language model`;
      $("e-out").innerHTML = md(r.essay_md); $("e-out").hidden = false;
      log("essay", `${topic}: ${r.sentences} sentences, grade ${r.reading_grade}, ${r.faithful}/${r.sentences} faithful`, "ok");
    } catch (e) { $("e-res").textContent = e.message; }
  };
  $("c-compose").onclick = async () => {
    const what = $("c-what").value.trim(), i = $("c-in").value.trim(), o = $("c-out").value.trim();
    const prompt = `Write a Python function${what ? " to " + what.replace(/^(to |that )/, "") : ""}${i && o ? ", so " + i + " becomes " + o : ""}`;
    $("c-res").textContent = "composing…"; log("code", prompt, "live");
    try {
      const r = await api("/api/chat", { text: prompt, sid: SID + "code", nokeep: true });
      const t = String(r.response || ""), m = t.match(/```(?:python)?\n?([\s\S]*?)```/) || t.match(/((?:^|\n)(?:def |import |from )[\s\S]*)$/);
      if (r.status !== "answered" || !m) { $("c-res").textContent = "declined: " + (r.why || t.slice(0, 160)); log("code", "declined: " + r.path, "no"); return; }
      const code = m[1].trim(); $("c-code").value = code;
      const fn = (code.match(/def\s+([A-Za-z_]\w*)\s*\(/) || [])[1];
      if (fn && i && o && !$("c-tests").value.trim()) $("c-tests").value = `assert ${fn}(${i}) == ${o}`;
      $("c-res").textContent = "composed; " + (r.response.split("\n")[0] || "").slice(0, 120); log("code", "composed " + (fn || "a function") + " via " + r.path, "ok");
    } catch (e) { $("c-res").textContent = e.message; }
  };
  $("c-run").onclick = async () => {
    $("c-res").textContent = "running…";
    const r = await api("/api/code/run", { code: $("c-code").value, tests: $("c-tests").value });
    $("c-res").textContent = r.ok ? "all tests passed" : "failed"; $("c-out-text").hidden = false; $("c-out-text").textContent = r.output;
    log("tests", r.ok ? "all tests passed" : "failed: " + r.output.trim().split("\n").slice(-1)[0], r.ok ? "ok" : "no");
  };
  [$("c-code"), $("c-tests")].forEach(t => t.addEventListener("keydown", e => { if (e.key === "Tab") { e.preventDefault(); t.setRangeText("    ", t.selectionStart, t.selectionEnd, "end"); } }));

  // ------------------------------------------------------------------ film (made in the browser; nothing uploaded)
  function renderFilmList() {
    if (!turns.length) { $("f-list").innerHTML = `<p class="muted">Ask something first; each answer can be filmed.</p>`; return; }
    turns.forEach(t => { if (!filmSeen.has(t.n)) { filmSeen.add(t.n); filmTurns.add(t.n); } });   // new answers start ticked
    $("f-list").innerHTML = turns.map(t => `<label><input type="checkbox" data-n="${t.n}" ${filmTurns.has(t.n) ? "checked" : ""}> <span>${esc(t.q)} <span class="muted">· ${esc(t.status)}</span></span></label>`).join("");
    $("f-list").querySelectorAll("input").forEach(c => c.onchange = () => { c.checked ? filmTurns.add(+c.dataset.n) : filmTurns.delete(+c.dataset.n); });
  }
  // the film shows the answer without the chat's internal markers ([ev:direct], [enwiki_...], [specialist])
  const clean = t => String(t || "").replace(/\[(?:ev|vessel):[^\]]*\]\s*/g, "").replace(/\s*\[(?:enwiki|simplewiki|dbpedia)_[0-9a-f]+\]/g, "").replace(/\s*\[[a-z0-9-]+\]\s*$/, "").trim();
  function wrap(ctx, text, x, y, w, lh, maxLines) {
    const words = String(text).split(/\s+/); let line = "", n = 0;
    for (const word of words) {
      const t = line ? line + " " + word : word;
      if (ctx.measureText(t).width > w && line) { ctx.fillText(line, x, y + n * lh); n++; line = word; if (n >= maxLines - 1) { line = line + " …"; break; } }
      else line = t;
    }
    if (line) { ctx.fillText(line, x, y + n * lh); n++; }
    return n;
  }
  async function record() {
    const sel = turns.filter(t => filmTurns.has(t.n));
    if (!sel.length || !explorer || !window.MediaRecorder) { $("f-prog").textContent = !explorer ? "the diagram is not available" : "nothing selected"; return; }
    const W = 1280, H = 720, LW = 760, cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    const ctx = cv.getContext("2d"), src = explorer.canvas, host = $("diagram");
    // optional ElevenLabs narration + sound bed, fetched before recording starts
    let ac = null, dest = null, voices = [], bed = null, pics = [];
    if (el.on && $("el-img").checked) {
      const model = $("el-img-model").value, style = $("el-img-style").value.trim() || "engraved plate illustration, warm parchment and burnt orange palette, no text";
      for (let i = 0; i < sel.length; i++) {
        $("f-prog").textContent = `illustrating ${i + 1} of ${sel.length}… (up to a minute each)`;
        try { pics[i] = { bmp: await createImageBitmap(new Blob([await elAudio("/api/el/image", { prompt: `${style}. Subject: ${sel[i].q}`, model })])), model }; log("image", `illustration ${i + 1} made (${model})`, "live"); }
        catch (e) { log("image", e.message, "no"); }
      }
    }
    if (el.on && ($("el-narrate").checked || $("el-sound").value.trim())) {
      ac = new AudioContext(); dest = ac.createMediaStreamDestination();
      try {
        if ($("el-narrate").checked) for (let i = 0; i < sel.length; i++) {
          $("f-prog").textContent = `narrating ${i + 1} of ${sel.length}…`;
          const t = sel[i], text = `${t.q} ... ${clean(t.response).replace(/\s+/g, " ").slice(0, 700)}`;
          voices.push(await ac.decodeAudioData(await elAudio("/api/el/speech", { text, voice: $("el-voice").value })));
          log("voice", `narration ${i + 1}: ${voices[i].duration.toFixed(1)} s`, "live");
        }
        if ($("el-sound").value.trim()) { $("f-prog").textContent = "making the sound…"; bed = await ac.decodeAudioData(await elAudio("/api/el/sound", { prompt: $("el-sound").value.trim(), seconds: 20 })); log("voice", `sound bed ${bed.duration.toFixed(1)} s`, "live"); }
      } catch (e) { log("voice", e.message, "no"); $("f-prog").textContent = e.message; ac.close(); ac = null; voices = []; bed = null; }
    }
    const stream = cv.captureStream(30);
    if (ac) dest.stream.getAudioTracks().forEach(tr => stream.addTrack(tr));
    if (bed) { const s = ac.createBufferSource(), g = ac.createGain(); s.buffer = bed; s.loop = true; g.gain.value = voices.length ? 0.16 : 0.5; s.connect(g).connect(dest); s.start(); }
    const type = (ac ? ["video/webm;codecs=vp9,opus", "video/webm;codecs=vp8,opus"] : []).concat(["video/webm;codecs=vp9", "video/webm;codecs=vp8", "video/webm"]).find(t => MediaRecorder.isTypeSupported(t));
    const rec = new MediaRecorder(stream, { mimeType: type, videoBitsPerSecond: 6e6 }), chunks = [];
    rec.ondataavailable = e => e.data.size && chunks.push(e.data);
    const done = new Promise(r => { rec.onstop = r; });
    rec.start(250); $("f-rec").disabled = true; log("film", `recording ${sel.length} answer(s)`, "live");
    // film time runs on drawn frames only; a hidden tab pauses the recording (and its sound) instead of losing the segment
    let last = performance.now();
    const tick = now => { const dt = Math.min(now - last, 50); last = now; return dt; };
    const onVis = () => {
      if (document.hidden) { if (rec.state === "recording") rec.pause(); if (ac) ac.suspend(); $("f-prog").textContent = "paused: the tab is hidden"; log("film", "paused while the tab is hidden", ""); }
      else { last = performance.now(); if (rec.state === "paused") rec.resume(); if (ac) ac.resume(); }
    };
    document.addEventListener("visibilitychange", onVis);
    for (let k = 0; k < sel.length; k++) {
      const t = sel[k], declined = t.status !== "answered";
      if (pics[k]) await new Promise(resolve => {      // the illustration card, labelled as a generated image
        const p = pics[k]; let ce = 0;
        const card = now => {
          ce += tick(now); const b = p.bmp, sc = Math.max(W / b.width, H / b.height), e = ce / 2800;
          ctx.drawImage(b, (W - b.width * sc * (1 + e * 0.04)) / 2, (H - b.height * sc * (1 + e * 0.04)) / 2, b.width * sc * (1 + e * 0.04), b.height * sc * (1 + e * 0.04));
          const g = ctx.createLinearGradient(0, H * 0.55, 0, H); g.addColorStop(0, "rgba(21,16,13,0)"); g.addColorStop(1, "rgba(21,16,13,.82)"); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
          ctx.fillStyle = "#fffaf0"; ctx.font = "italic 34px 'EB Garamond', Georgia, serif"; wrap(ctx, t.q, 60, H - 110, W - 120, 40, 2);
          ctx.font = "11px 'JetBrains Mono', monospace"; ctx.fillStyle = "rgba(255,250,240,.75)"; ctx.fillText("GENERATED IMAGE · ELEVENLABS · " + p.model.toUpperCase(), 60, H - 28);
          if (ce < 2800) requestAnimationFrame(card); else resolve();
        };
        requestAnimationFrame(card);
      });
      const lit = explorer.trace(t.trace, declined);
      let dur = Math.max(5, lit.length * 0.75 + 3.5) * 1000;
      if (voices[k]) { const s = ac.createBufferSource(); s.buffer = voices[k]; s.connect(dest); s.start(ac.currentTime + 0.4); dur = Math.max(dur, (voices[k].duration + 1.2) * 1000); }
      let el = 0;
      await new Promise(resolve => {
        const frame = now => {
          el += tick(now);
          ctx.fillStyle = "#f5efe1"; ctx.fillRect(0, 0, W, H);
          // diagram, contained in the left panel
          // the diagram fills the left panel: scaled up around its centre and clipped to the panel
          const sw = src.width, sh = src.height, s = Math.min(LW / sw, (H - 60) / sh) * 1.75, dw = sw * s, dh = sh * s, dx = (LW - dw) / 2, dy = (H - dh) / 2;
          ctx.save(); ctx.beginPath(); ctx.rect(0, 0, LW, H); ctx.clip();
          ctx.drawImage(src, dx, dy, dw, dh);
          const k2 = dw / host.clientWidth;
          explorer.labelsOnScreen().forEach(L => {
            if (!/lit|layer|mine/.test(L.cls)) return;
            const x = dx + L.x * k2, y = dy + L.y * k2, layer = /layer/.test(L.cls), on = /lit/.test(L.cls);
            ctx.font = layer ? "600 13px Cinzel, Georgia, serif" : "600 12px 'JetBrains Mono', monospace";
            const w = ctx.measureText(L.text).width;
            if (layer) { ctx.fillStyle = "#6a5a47"; ctx.fillText(L.text.toUpperCase(), x, y + 4); return; }
            ctx.fillStyle = on ? "#c0602e" : "rgba(250,246,236,.92)"; ctx.fillRect(x - w / 2 - 5, y - 26, w + 10, 18);
            ctx.fillStyle = on ? "#fffaf0" : "#9a4a20"; ctx.fillText(L.text, x - w / 2, y - 13);
          });
          ctx.restore();
          // right panel: question, answer, path
          ctx.fillStyle = "#efe6cf"; ctx.fillRect(LW, 0, W - LW, H); ctx.fillStyle = "rgba(21,16,13,.24)"; ctx.fillRect(LW, 0, 1, H);
          const X = LW + 36, RW = W - LW - 72;
          ctx.fillStyle = "#5c4416"; ctx.font = "700 20px Cinzel, Georgia, serif"; ctx.fillText("ORACLE", X, 58);
          ctx.fillStyle = "#c0602e"; ctx.fillText("7", X + ctx.measureText("ORACLE").width + 2, 58);
          ctx.fillStyle = "#946d1e"; ctx.font = "500 12px 'JetBrains Mono', monospace"; ctx.fillText("QUESTION", X, 104);
          ctx.fillStyle = "#342820"; ctx.font = "italic 24px 'EB Garamond', Georgia, serif"; let n = wrap(ctx, t.q, X, 136, RW, 30, 3);
          let y = 136 + n * 30 + 28;
          ctx.fillStyle = "#946d1e"; ctx.font = "500 12px 'JetBrains Mono', monospace"; ctx.fillText(declined ? "DECLINED" : "ANSWER", X, y);
          ctx.fillStyle = declined ? "#5c4416" : "#15100d"; ctx.font = "21px 'EB Garamond', Georgia, serif";
          const shown = el > 900 ? clean(t.response) : "";
          n = wrap(ctx, shown, X, y + 32, RW, 27, 7); y = y + 32 + Math.max(1, n) * 27 + 26;
          ctx.fillStyle = "#946d1e"; ctx.font = "500 12px 'JetBrains Mono', monospace"; ctx.fillText("PATH", X, y);
          const steps = Math.min(lit.length, Math.floor(el / 750) + 1);
          lit.forEach((p, i) => { ctx.fillStyle = i < steps ? "#c0602e" : "rgba(106,90,71,.45)"; ctx.font = (i < steps ? "600 " : "") + "13px 'JetBrains Mono', monospace"; if (y + 26 + i * 22 < H - 50) ctx.fillText((i + 1) + "  " + p[0] + " · " + p[1], X, y + 26 + i * 22); });
          ctx.fillStyle = "#6a5a47"; ctx.font = "11px 'JetBrains Mono', monospace";
          ctx.fillText(`${String(head).replace("oracle_release_runtime_", "core ")} · path traced live on this machine`, X, H - 30);
          $("f-prog").textContent = `answer ${k + 1} of ${sel.length}`;
          if (el < dur) requestAnimationFrame(frame); else resolve();
        };
        requestAnimationFrame(frame);
      });
    }
    document.removeEventListener("visibilitychange", onVis);
    rec.stop(); await done; $("f-rec").disabled = false; if (ac) ac.close();
    const blob = new Blob(chunks, { type: "video/webm" }), url = URL.createObjectURL(blob);
    $("f-video").src = url; $("f-video").hidden = false; $("f-dl").href = url; $("f-dl").hidden = false;
    $("f-prog").textContent = `done · ${(blob.size / 1e6).toFixed(1)} MB`; log("film", `film ready (${(blob.size / 1e6).toFixed(1)} MB)`, "ok");
  }
  $("f-rec").onclick = record;
  // ElevenLabs (optional): the key lives in this variable, or on this computer if "remember" is ticked
  const el = { on: false, key: "" };
  async function elAudio(path, body) {
    const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...body, key: el.key }) });
    if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error || "ElevenLabs request failed");
    return r.arrayBuffer();
  }
  async function elConnect(remembered) {
    $("el-connect").disabled = true;
    try {
      el.key = remembered ? "" : $("el-key").value.trim();
      const r = await api("/api/el/connect", { key: el.key, remember: $("el-remember").checked || remembered });
      el.on = true; $("el-opts").hidden = false; $("el-forget").hidden = false; $("el-key").value = ""; $("el-key").placeholder = "connected";
      $("el-voice").innerHTML = r.voices.map(v => `<option value="${esc(v.id)}">${esc(v.name)}</option>`).join("");
      log("voice", `ElevenLabs connected · ${r.voices.length} voices${r.remembered ? " · key remembered on this computer" : " · key kept in this page only"}`, "ok");
    } catch (e) { log("voice", e.message, "no"); if (!remembered) alert(e.message); }
    $("el-connect").disabled = false;
  }
  $("el-connect").onclick = () => elConnect(false);
  $("el-forget").onclick = async () => { await api("/api/el/forget", {}); el.on = false; el.key = ""; $("el-opts").hidden = true; $("el-forget").hidden = true; $("el-key").placeholder = "ElevenLabs API key"; log("voice", "ElevenLabs disconnected; key removed", "live"); };

  // ------------------------------------------------------------------ share
  // ------------------------------------------------------------------ $ORACLE7 registry: one specialist, one burned $ORACLE7
  const MEMO_PROGRAM = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr";
  function loadWeb3() {
    if (window.solanaWeb3) return Promise.resolve(window.solanaWeb3);
    return new Promise((ok, no) => { const s = document.createElement("script"); s.src = "/static/vendor/solana-web3-1.95.3.iife.min.js";
      s.onload = () => ok(window.solanaWeb3); s.onerror = () => no(new Error("could not load the Solana library")); document.head.appendChild(s); });
  }
  // the transaction one wallet signs: [burn exactly 1 $ORACLE7 (register only)] + [memo with the specialist's fingerprint]
  async function buildRegistryTx(w, conn, owner, m, kind) {
    const { blockhash, lastValidBlockHeight } = await conn.getLatestBlockhash("finalized");
    const tx = new w.Transaction({ feePayer: owner, blockhash, lastValidBlockHeight });
    if (kind === "register") {
      const mint = new w.PublicKey(m.mint);
      const accs = await conn.getParsedTokenAccountsByOwner(owner, { mint });
      const acc = accs.value.find(a => BigInt(a.account.data.parsed.info.tokenAmount.amount) >= BigInt(m.burn_raw));
      if (!acc) throw new Error("this wallet holds less than 1 $ORACLE7, so it cannot register a specialist");
      const data = new Uint8Array(10); data[0] = 15;                       // BurnChecked: amount (u64 LE), decimals (u8)
      new DataView(data.buffer).setBigUint64(1, BigInt(m.burn_raw), true); data[9] = m.decimals;
      tx.add(new w.TransactionInstruction({ programId: acc.account.owner, data,
        keys: [{ pubkey: acc.pubkey, isSigner: false, isWritable: true }, { pubkey: mint, isSigner: false, isWritable: true },
               { pubkey: owner, isSigner: true, isWritable: false }] }));
    }
    tx.add(new w.TransactionInstruction({ programId: new w.PublicKey(MEMO_PROGRAM), data: new TextEncoder().encode(m.memo),
      keys: [{ pubkey: owner, isSigner: true, isWritable: false }] }));
    return { tx, blockhash, lastValidBlockHeight };
  }
  async function simulateTx(tx) {
    const b64 = tx.serialize({ requireAllSignatures: false, verifySignatures: false }).toString("base64");
    const r = await api("/api/solana/rpc", { jsonrpc: "2.0", id: 1, method: "simulateTransaction",
      params: [b64, { encoding: "base64", sigVerify: false, replaceRecentBlockhash: true, commitment: "confirmed" }] });
    if (r.error) throw new Error("Solana: " + (r.error.message || JSON.stringify(r.error)));
    return r.result.value;
  }
  async function solanaRecord(id, kind) {
    const out = $("reg-" + id);
    try {
      const m = await api(`/api/registry/memo?id=${encodeURIComponent(id)}&kind=${kind}`);
      if (kind === "register" && !confirm(`Register ${id} on Solana?\n\nYour wallet will be asked to sign ONE transaction that burns exactly 1 $ORACLE7 and records:\n${m.memo}\n\nThe burn cannot be undone.`)) return;
      const w = await loadWeb3();
      const p = (window.phantom && window.phantom.solana) || (window.solana && window.solana.isPhantom ? window.solana : null);
      if (!p) throw new Error("no Phantom wallet in this browser (install it, or sign the memo from the CLI: registry-memo " + id + ")");
      out.textContent = "connecting to your wallet…";
      const owner = (await p.connect()).publicKey;
      const conn = new w.Connection(location.origin + "/api/solana/rpc", { commitment: "confirmed" });   // relayed by the local server
      const { tx, lastValidBlockHeight } = await buildRegistryTx(w, conn, owner, m, kind);
      out.textContent = "checking the transaction on Solana before your wallet sees it…";
      const sim = await simulateTx(tx);                      // the exact transaction, executed on a copy of mainnet state
      if (sim.err) throw new Error("this transaction would fail on Solana, so it was not sent: " + JSON.stringify(sim.err) + (sim.logs || []).filter(l => /Error|error|insufficient/i.test(l)).slice(0, 2).join(" "));
      out.textContent = "approve it in your wallet…";
      const { signature } = await p.signAndSendTransaction(tx);
      out.textContent = "sent; waiting for confirmation… " + signature;
      let done = false;                                      // poll the status (no websocket through the relay)
      for (let i = 0; i < 60 && !done; i++) {
        await new Promise(r => setTimeout(r, 2000));
        const st = (await conn.getSignatureStatuses([signature])).value[0];
        if (st && st.err) throw new Error("the transaction failed on Solana: " + JSON.stringify(st.err));
        done = !!(st && (st.confirmationStatus === "confirmed" || st.confirmationStatus === "finalized"));
        if (!done && !st && (await conn.getBlockHeight()) > lastValidBlockHeight) throw new Error("the transaction expired before it landed; try again");
      }
      if (!done) throw new Error("not confirmed after 2 minutes; check it on Solana Explorer: " + signature);
      const r = await api("/api/registry/record", { id, kind, signature });
      out.innerHTML = `${kind === "register" ? "Registered: 1 $ORACLE7 burned" : "Attested"} · <a href="https://explorer.solana.com/tx/${esc(signature)}" target="_blank" rel="noopener">transaction</a> · ${r.records.length} record(s)`;
      log("registry", `${id}: ${kind} confirmed on Solana (${signature.slice(0, 12)}…)`, "ok");
    } catch (e) { out.textContent = e.message; log("registry", id + ": " + e.message, "no"); }
  }
  async function solanaCheck(id) {
    const out = $("reg-" + id); out.textContent = "reading the chain…";
    try {
      const c = await api("/api/registry/check", { id });
      out.innerHTML = `<b>${c.registered ? "Verified on Solana" : "Not registered"}</b> · ${c.attestations} attestation(s) · ${c.oracle7_burned} $ORACLE7 burned · vouching wallets hold ${c.vouching_oracle7} $ORACLE7` +
        (c.records.length ? "<br>" + c.records.map(r => r.error ? esc(r.error) : `${esc(r.kind)} by ${esc((r.signer || "").slice(0, 8))}… ${r.matches_files ? "matches its files" : "<b>does not match</b>"} · holds ${r.oracle7} · <a href="${esc(r.explorer)}" target="_blank" rel="noopener">tx</a>`).join("<br>") : "");
      log("registry", `${id}: ${c.registered ? "verified on Solana" : "not registered"}, ${c.attestations} attestation(s)`, c.registered ? "ok" : "");
    } catch (e) { out.textContent = e.message; log("registry", e.message, "no"); }
  }

  async function pack(id) {
    const r = await api("/api/package", { id });
    $("sh-out").hidden = false;
    $("sh-out").textContent = `Packaged ${id} (${r.state}) → ${r.zip}\n\nTo share it with the community registry, with your own Hugging Face account:\n${r.command}`;
    log("share", "packaged " + id + " → " + r.zip, "ok");
  }
  $("sh-import").onclick = async () => {
    try { const r = await api("/api/import", { path: $("sh-path").value.trim() }); log("import", r.id + ": " + r.note, "ok"); loadYours(); }
    catch (e) { log("import", e.message, "no"); alert(e.message); }
  };

  // ------------------------------------------------------------------ start: scan, connect, add files
  const readingsTable = rd => `<table class="readings">${rd.map(r => `<tr><td>${esc(r.entity)} · ${esc(r.signal)}</td><td>${esc(r.text)}</td><td>${esc(r.source)}</td></tr>`).join("")}</table>`;
  function watchSource(id, progEl, what) {
    const poll = async () => {
      const p = await api("/api/exam?id=" + encodeURIComponent(id));
      if (p.state === "running") { progEl.textContent = `checking: ${p.phase || ""} ${p.done || 0}/${p.total || "?"}`; setTimeout(poll, 700); return; }
      if (p.state === "error") { progEl.textContent = p.error; log("check", id + ": " + p.error, "no"); return; }
      const v = p.result || {};
      if (v.decision === "ADMIT") {
        progEl.textContent = `${what} joined your model · read ${v.with_specialist.ok}/${v.n} probes back · ${v.core.taken} of ${v.core.n} general questions taken`;
        log("grow", `${id} joined your model (source check passed)`, "live");
        explorer && explorer.addModule("S", "Yours: " + id); explorer && explorer.trace([["S", "Yours: " + id]], false);
      } else { progEl.textContent = "check failed: " + (v.reasons || []).join("; "); log("check", id + ": " + (v.reasons || []).join("; "), "no"); }
      refreshState(); loadSpecs();
    };
    poll();
  }
  async function doScan() {
    showTab("start"); $("st-scan-prog").textContent = "reading…"; log("scan", "reading this computer", "live");
    try {
      const r = await api("/api/scan", {});
      $("st-scan-out").innerHTML = readingsTable(r.readings); $("st-scan-save").hidden = false; $("st-scan-prog").textContent = r.readings.length + " readings";
      log("scan", r.readings.length + " readings: " + r.readings.map(x => x.entity + " " + x.signal).join(", "), "ok");
    } catch (e) { $("st-scan-prog").textContent = e.message; log("scan", e.message, "no"); }
  }
  $("st-scan").onclick = doScan;
  $("st-scan-save").onclick = async () => {
    const r = await api("/api/scan/save", {}); log("new", "reader " + r.id + " made; checking it", "live");
    watchSource(r.id, $("st-scan-prog"), "This computer");
  };
  function serverForm() {
    const m = /^([^@\s]+)@([^\s:]+)$/.exec($("st-host").value.trim());
    if (!m) throw new Error("write it as user@host");
    return { name: $("st-name").value.trim() || m[2], user: m[1], host: m[2], port: +($("st-port").value.replace(/\D/g, "") || 22), key: $("st-key").value.trim() };
  }
  $("st-srv").onsubmit = async e => {
    e.preventDefault(); $("st-srv-prog").textContent = "connecting…";
    try {
      const f = serverForm(); log("connect", `${f.user}@${f.host}:${f.port} (read-only commands)`, "live");
      const r = await api("/api/server", f);
      $("st-srv-out").innerHTML = readingsTable(r.readings); $("st-srv-save").hidden = false; $("st-srv-prog").textContent = r.readings.length + " readings from " + f.host;
      log("connect", r.readings.length + " readings from " + f.host, "ok");
    } catch (err) { $("st-srv-prog").textContent = err.message; log("connect", err.message, "no"); }
  };
  $("st-srv-save").onclick = async () => {
    try { const f = serverForm(), r = await api("/api/server/save", f); log("new", "reader " + r.id + " made; checking it", "live"); watchSource(r.id, $("st-srv-prog"), f.name); }
    catch (err) { $("st-srv-prog").textContent = err.message; }
  };
  async function addFiles(list) {
    const files = [];
    for (const f of list) {
      if (!/\.(csv|tsv|txt|md)$/i.test(f.name)) { log("files", f.name + ": not a .csv/.tsv/.txt/.md file, skipped", "no"); continue; }
      if (f.size > 5e6) { log("files", f.name + ": over 5 MB, skipped", "no"); continue; }
      files.push({ name: f.name, text: await f.text() });
    }
    if (!files.length) { $("st-files-prog").textContent = "add .csv, .tsv, .txt or .md files"; return; }
    $("st-files-prog").textContent = "adding " + files.length + " file(s)…";
    try {
      const r = await api("/api/files/add", { name: $("st-fname").value.trim() || "my files", files });
      log("files", `${r.saved.join(", ")} → ${r.id}; checking it`, "live"); watchSource(r.id, $("st-files-prog"), $("st-fname").value.trim() || "Your files");
    } catch (e) { $("st-files-prog").textContent = e.message; log("files", e.message, "no"); }
  }
  $("st-files").onchange = e => addFiles(e.target.files);
  const drop = $("st-drop");
  ["dragenter", "dragover"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach(ev => drop.addEventListener(ev, e => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", e => addFiles(e.dataTransfer.files));

  $("mc-form").onsubmit = async e => {
    e.preventDefault(); $("mc-prog").textContent = "connecting…";
    const name = $("mc-name").value.trim();
    try {
      const r = await api("/api/mcp/connect", { name, command: $("mc-cmd").value.trim(), url: $("mc-url").value.trim(), token: $("mc-token").value.trim() });
      $("mc-prog").textContent = `${r.tools.length} tools on ${name}`; log("mcp", `connected ${name}: ${r.tools.map(t => t.name).join(", ")}`, "ok");
      $("mc-tools").innerHTML = `<table class="readings">${r.tools.map(t => `<tr><td><label><input type="checkbox" data-tool="${esc(t.name)}" checked> ${esc(t.name)}</label></td><td>${esc(t.description)}</td><td>${esc((t.required || []).join(", ") || "no arguments")}</td></tr>`).join("")}</table>` +
        `<textarea id="mc-ex" class="mono short" placeholder="example questions (optional), one per line, with what the answer must contain after =>&#10;e.g. what files are in my reports folder? => budget.xlsx"></textarea>` +
        `<div class="row"><button class="btn primary" id="mc-save">Make a specialist from these tools</button></div>`;
      $("mc-save").onclick = async () => {
        const tools = [...$("mc-tools").querySelectorAll("[data-tool]:checked")].map(c => c.dataset.tool);
        const examples = $("mc-ex").value.split("\n").map(l => l.trim()).filter(Boolean).map(l => { const [q, w] = l.split("=>"); return { q: q.trim(), want: (w || "").trim() || null }; });
        try { const s = await api("/api/mcp/save", { name, tools, examples }); log("new", `${s.id}: ${tools.length} tools; checking it`, "live"); watchSource(s.id, $("mc-prog"), name + " tools"); }
        catch (err) { $("mc-prog").textContent = err.message; }
      };
    } catch (err) { $("mc-prog").textContent = err.message; log("mcp", err.message, "no"); }
  };

  // ------------------------------------------------------------------ sensors (connect, test, watch; readings kept 24 h on this computer)
  let quantities = {}, snTimer = null;
  const PLACE = { http: "http://192.168.1.40/data  (JSON or Prometheus metrics)", mqtt: "broker:1883/garden/node1", serial: "COM3@9600  or  /dev/ttyUSB0@9600",
                  file: "C:\\logs\\garden.csv  (the newest line is read)", simulated: "(no address needed)" };
  $("sn-kind").onchange = () => { const k = $("sn-kind").value; $("sn-addr").placeholder = PLACE[k]; $("sn-addr").disabled = k === "simulated"; $("sn-user").hidden = $("sn-pass").hidden = k !== "mqtt"; };
  $("sn-kind").onchange();
  function spark(points) {
    if (points.length < 2) return "";
    const vs = points.map(p => p[1]), lo = Math.min(...vs), hi = Math.max(...vs), t0 = points[0][0], t1 = points[points.length - 1][0] || t0 + 1;
    const xy = points.map(p => `${((p[0] - t0) / Math.max(1, t1 - t0) * 200).toFixed(1)},${(28 - (p[1] - lo) / Math.max(1e-9, hi - lo) * 26).toFixed(1)}`).join(" ");
    return `<svg viewBox="0 0 200 30" preserveAspectRatio="none" aria-hidden="true"><polyline points="${xy}" fill="none" stroke="#c0602e" stroke-width="1.5" vector-effect="non-scaling-stroke"/></svg>`;
  }
  async function loadSensors() {
    try {
      const r = await api("/api/sensors"); quantities = r.quantities;
      if (!r.items.length) { $("sn-list").innerHTML = `<p class="muted">No sensors yet. Connect one below, or try the simulated garden node.</p>`; return; }
      const tiles = await Promise.all(r.items.map(async s => {
        const qs = await Promise.all(Object.entries(s.latest).map(async ([q, l]) => {
          const pts = (await api(`/api/sensor/series?id=${encodeURIComponent(s.id)}&q=${encodeURIComponent(q)}`)).points;
          return `<div class="q"><span>${esc(q)}</span><b>${esc(l.v)}<small>${esc(l.unit)}</small></b></div>${spark(pts)}`;
        }));
        const st = s.status || {}, age = st.at ? Math.round(Date.now() / 1000 - st.at) : null;
        return `<div class="sn"><h5>${esc(s.name)}<small>${esc(s.kind)}${s.kind === "simulated" ? ' · <span class="sim">SIMULATED</span>' : ""}</small></h5>${qs.join("") || '<p class="muted">no readings yet</p>'}` +
          `<div class="meta"><span class="${st.ok === false ? "bad" : ""}">${st.ok === false ? esc(st.error) : age !== null ? "read " + age + " s ago · every " + s.interval + " s" : "starting…"}</span>` +
          `<span>${s.rejected ? `<span class="bad">${s.rejected} rejected</span> · ` : ""}${esc(s.state)} · <button data-rm="${esc(s.id)}">remove</button></span></div></div>`;
      }));
      $("sn-list").innerHTML = tiles.join("");
      $("sn-list").querySelectorAll("[data-rm]").forEach(b => b.onclick = async () => {
        if (!confirm("Remove this sensor, its readings and its reader?")) return;
        await api("/api/sensor/remove", { id: b.dataset.rm }); log("sensor", "removed " + b.dataset.rm, "live"); loadSensors(); refreshState();
      });
    } catch (e) { log("sensor", e.message, "no"); }
  }
  function sensorForm() { return { name: $("sn-name").value.trim() || "my sensor", kind: $("sn-kind").value, address: $("sn-addr").value.trim(), interval: +($("sn-int").value.replace(/\D/g, "") || 30), user: $("sn-user").value, password: $("sn-pass").value }; }
  $("sn-form").onsubmit = async e => {
    e.preventDefault(); const f = sensorForm(); $("sn-prog").textContent = "reading it once…"; log("sensor", `testing ${f.kind} ${f.address}`, "live");
    try {
      const r = await api("/api/sensor/test", f);
      const opts = q => `<option value="">skip</option>` + Object.keys(quantities).map(k => `<option value="${esc(k)}" ${k === q ? "selected" : ""}>${esc(k)} (${esc(quantities[k])})</option>`).join("") + `<option value="other">other…</option>`;
      $("sn-prog").textContent = `${r.fields.length} numbers found in ${r.source}`;
      $("sn-fields").innerHTML = `<table class="readings">${r.fields.map((x, i) => `<tr><td>${esc(x.path)}</td><td>${esc(x.value)}</td><td><select data-i="${i}">${opts(x.guess)}</select></td></tr>`).join("")}</table>` +
        `<div class="row"><button class="btn primary" id="sn-save">Add sensor</button><span class="muted">Keep the readings you want and say what each measures; impossible values are rejected by that quantity's physical range.</span></div>`;
      $("sn-save").onclick = async () => {
        const fields = [...$("sn-fields").querySelectorAll("select")].map(s => {
          let q = s.value; if (q === "other") q = (prompt("What does " + r.fields[+s.dataset.i].path + " measure? (e.g. tank level)") || "").trim().toLowerCase();
          return q ? { path: r.fields[+s.dataset.i].path, quantity: q } : null; }).filter(Boolean);
        try {
          const a = await api("/api/sensor/add", { ...sensorForm(), fields });
          log("sensor", `${a.id}: polling every ${sensorForm().interval} s; checking its reader`, "live"); $("sn-fields").innerHTML = ""; $("sn-form").reset(); $("sn-kind").onchange();
          watchSource(a.id, $("sn-prog"), f.name); loadSensors();
        } catch (err) { $("sn-prog").textContent = err.message; }
      };
    } catch (err) { $("sn-prog").textContent = err.message; log("sensor", err.message, "no"); }
  };
  function openSensors(sim) {
    showTab("sensors");
    if (sim) { $("sn-name").value = "garden node"; $("sn-kind").value = "simulated"; $("sn-kind").onchange(); $("sn-form").requestSubmit(); }
    else $("sn-name").focus();
  }
  $("st-sensor").onclick = () => openSensors(false);
  $("st-sensor-sim").onclick = () => openSensors(true);

  // ------------------------------------------------------------------ verify this install (hashes, Merkle root, Solana anchor)
  async function doVerify() {
    showTab("specialists"); $("v-out").hidden = false; $("v-out").innerHTML = `<p class="muted">Hashing every shipped part…</p>`; log("verify", "recomputing the release hashes on this computer", "live");
    try {
      const v = await api("/api/verify", {});
      const ok = v.root_matches && !v.changed.length;
      $("v-out").innerHTML = `<div class="head ${ok ? "pass" : "fail"}">${ok ? "VERIFIED" : "DOES NOT MATCH"} · ${v.verified} of ${v.parts} parts · ${v.specialists_verified} specialist folders</div>` +
        `<p class="mono small">published root ${esc(v.published_root)}<br>computed root&nbsp; ${esc(v.computed_root)}</p>` +
        (v.changed.length ? `<p class="fail">Changed: ${esc(v.changed.join(", "))}</p>` : "") + (v.missing.length ? `<p class="fail">Missing: ${esc(v.missing.join(", "))}</p>` : "") +
        (v.extra_local.length ? `<p class="muted">Not in the release (yours or added): ${esc(v.extra_local.join(", "))}</p>` : "") +
        (v.anchor && v.anchor.signature ? `<button class="btn" id="v-chain">Check the anchor on Solana</button> <span class="muted">read-only; asks a public Solana RPC</span>` : `<p class="muted">The on-chain anchor for this release is not recorded in RELEASE_HASHES.json.</p>`);
      log("verify", `${ok ? "verified" : "mismatch"}: ${v.verified}/${v.parts} parts; root ${v.computed_root.slice(0, 16)}…`, ok ? "ok" : "no");
      const b = $("v-chain");
      if (b) b.onclick = async () => {
        b.disabled = true; log("verify", "reading the anchor transaction on Solana", "live");
        try {
          const c = await api("/api/verify/chain", {});
          b.insertAdjacentHTML("afterend", `<p class="${c.root_on_chain ? "pass" : "fail"}">${c.root_on_chain ? "The root is on-chain" : "The root is NOT in that transaction"}: slot ${c.slot}, ${c.block_time ? new Date(c.block_time * 1000).toUTCString() : ""} · <a href="${esc(c.explorer)}" target="_blank" rel="noopener">view the transaction</a></p>`);
          log("verify", c.root_on_chain ? "anchor confirmed on Solana, slot " + c.slot : "anchor does not carry this root", c.root_on_chain ? "ok" : "no");
        } catch (e) { b.insertAdjacentHTML("afterend", `<p class="fail">${esc(e.message)}</p>`); log("verify", e.message, "no"); }
      };
    } catch (e) { $("v-out").innerHTML = `<p class="fail">${esc(e.message)}</p>`; log("verify", e.message, "no"); }
  }
  $("v-run").onclick = doVerify;

  // ------------------------------------------------------------------ conversations panel (collapsible; kept on this computer)
  let convItems = [];
  function setSide(open) {
    document.body.classList.toggle("side-open", open); $("side-toggle").setAttribute("aria-expanded", String(open));
    store.set("o7wb.side", open ? "1" : "0");
  }
  $("side-toggle").onclick = () => setSide(!document.body.classList.contains("side-open"));
  async function loadConvs() {
    try { const r = await api("/api/convs"); convItems = r.items; $("cv-keep").checked = r.keep; renderConvs(); } catch (e) { log("history", e.message, "no"); }
  }
  function renderConvs() {
    const f = $("cv-find").value.trim().toLowerCase();
    const items = convItems.filter(c => !f || c.title.toLowerCase().includes(f));
    $("cv-list").innerHTML = items.map(c => `<li class="${c.id === SID ? "on" : ""}" data-id="${esc(c.id)}"><button class="cv-open">${esc(c.title)}</button>` +
      `<small>${esc(new Date(c.updated * 1000).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }))} · ${c.turns} turn${c.turns === 1 ? "" : "s"}</small>` +
      `<span class="cv-act"><button data-a="rename">Rename</button><button data-a="remember" title="Make this conversation a temporary specialist">Make specialist</button><button data-a="delete">Delete</button></span></li>`).join("") ||
      `<li class="muted">${f ? "No conversation matches." : "Your conversations appear here."}</li>`;
    $("cv-list").querySelectorAll("li[data-id]").forEach(li => {
      const id = li.dataset.id;
      li.querySelector(".cv-open").onclick = () => openConv(id);
      li.querySelector('[data-a="rename"]').onclick = async () => { const t = prompt("Name this conversation", convItems.find(c => c.id === id).title); if (t) { await api("/api/conv/rename", { id, title: t }); loadConvs(); } };
      li.querySelector('[data-a="delete"]').onclick = async () => { if (!confirm("Delete this conversation from this computer?")) return; await api("/api/conv/delete", { id }); log("history", "deleted a conversation", "live"); if (id === SID) newConv(); loadConvs(); };
      li.querySelector('[data-a="remember"]').onclick = () => rememberConv(id);
    });
  }
  $("cv-find").oninput = renderConvs;
  function resetThread() {
    $("thread").querySelectorAll(".turn").forEach(n => n.remove());
    const hello = $("thread").querySelector(".hello"); if (hello) hello.hidden = false;
    turns.length = 0; filmTurns = new Set(); filmSeen = new Set(); explorer && explorer.clearTrace();
  }
  function newConv() { SID = newId(); store.set("o7wb.conv", SID); resetThread(); renderConvs(); log("history", "new conversation", "live"); $("q").focus(); }
  async function openConv(id) {
    const c = await api("/api/conv?id=" + encodeURIComponent(id));
    SID = id; store.set("o7wb.conv", id); resetThread();
    c.turns.forEach(t0 => { const t = { ...t0, n: turns.length + 1 }; turns.push(t); renderTurn(turnBox(t.q), t, false); });
    const last = c.turns[c.turns.length - 1]; if (last && explorer) explorer.trace(last.trace, last.status !== "answered");
    $("thread").scrollTop = $("thread").scrollHeight; renderConvs(); renderFilmList();
    if (c.turns.length) log("history", `opened "${c.title}" (${c.turns.length} turns); the core carries on its context`, "live");
  }
  async function rememberConv(id, days) {
    days = days || +(prompt("Keep this conversation as a temporary specialist for how many days?", "7") || 0);
    if (!days) return;
    try {
      const r = await api("/api/conv/specialist", { id, days });
      log("remember", `${r.id}: a temporary specialist until ${new Date(r.expires * 1000).toLocaleString()}; checking it`, "live");
      watchSource(r.id, { set textContent(v) { log("remember", v, /joined/.test(v) ? "ok" : ""); } }, "This conversation");
    } catch (e) { log("remember", e.message, "no"); alert(e.message); }
  }
  $("cv-new").onclick = newConv;
  $("cv-keep").onchange = async () => { const r = await api("/api/conv/keep", { on: $("cv-keep").checked }); log("history", r.keep ? "conversations are kept on this computer" : "conversations are no longer kept", "live"); };
  $("cv-del-all").onclick = async () => { if (!confirm("Delete every saved conversation from this computer?")) return; await api("/api/conv/delete_all", {}); log("history", "all conversations deleted", "live"); newConv(); loadConvs(); };

  // ------------------------------------------------------------------ commands typed in the chat (/help lists them)
  async function command(text) {
    const [cmd, ...rest] = text.trim().split(/\s+/), arg = rest.join(" ");
    log("command", text, "live");
    switch (cmd.toLowerCase()) {
      case "/scan": return doScan();
      case "/connect": showTab("start"); if (arg) { const [h, port, key] = rest; $("st-host").value = h || ""; $("st-port").value = port || ""; $("st-key").value = key || ""; $("st-srv").requestSubmit(); } else $("st-host").focus(); return;
      case "/files": showTab("start"); return $("st-files").click();
      case "/mcp": showTab("start"); return $("mc-name").focus();
      case "/new": showTab("build"); $("b-id").value = rest[0] || ""; $("b-words").value = rest.slice(1).join(" "); return rest[0] ? $("b-new").requestSubmit() : $("b-id").focus();
      case "/exam": if (!rest[0]) return log("command", "/exam <id> dev|heldout", "no"); showTab("build"); await openEditor(rest[0]); return exam(rest[1] === "heldout" ? "heldout" : "dev");
      case "/specialists": showTab("specialists"); $("s-find").value = arg; return renderSpecs();
      case "/systems": return showTab("systems");
      case "/gaps": if (/^(on|off)$/.test(arg)) { $("g-on").checked = arg === "on"; await $("g-on").onchange(); } return showTab("gaps");
      case "/code": showTab("code"); $("c-what").value = arg; return arg ? $("c-compose").click() : $("c-what").focus();
      case "/film": showTab("film"); return renderFilmList();
      case "/share": showTab("share"); return rest[0] ? pack(rest[0]) : null;
      case "/clear": resetThread(); return;
      case "/verify": return doVerify();
      case "/registry": showTab("share"); return rest[0] ? setTimeout(() => solanaCheck(rest[0]), 300) : null;
      case "/sensors": return openSensors(false);
      case "/history": setSide(!document.body.classList.contains("side-open")); return;
      case "/new-chat": return newConv();
      case "/remember": return rememberConv(SID, +rest[0] || 0);
      case "/help": return ask("/help", true);
      default: log("command", "unknown command " + cmd + " - type /help", "no");
    }
  }

  // ------------------------------------------------------------------ start
  (async () => {
    try {
      const st = await refreshState(); log("ready", `Oracle7 ${head} on this machine · diagram of the release`, "ok");
      if (st.elevenlabs_remembered) elConnect(true);
      setSide(store.get("o7wb.side") === "1");
      await loadConvs();
      if (convItems.some(c => c.id === SID)) await openConv(SID);
      await loadSpecs(); await loadSystems(); await loadYours();
      log("ready", `${specData.items.length} specialists · ${specData.failed_exams} failed exams published · ${specData.yours.length} of yours`, "ok");
    } catch (e) { log("error", e.message, "no"); }
  })();
})();
