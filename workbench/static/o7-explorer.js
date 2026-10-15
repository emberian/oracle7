/* Oracle7 architecture explorer (Workbench copy: preserveDrawingBuffer for films, addModule for your specialists) — themeable. Requires THREE (r128) + OrbitControls.
   Usage: const ex = O7Explorer(hostEl, { palette: {...}, onSelect(id) {} });
   Data: the release head w540 (chain of 317 folds) and the specialist ledger on Box C, 2026-10-14.
   trace(steps) lights the exact path one answer took: steps = [[stageId, moduleName|null], ...]. */
(function () {
  const STAGES = [
    { id: "L5", name: "Self-model", y: 8.0, r: 2.4, blurb: "The model reading and explaining its own record.", mods: [
      ["Self record & atlas", "w33 · w110 · w117"], ["Self-explanation", "w412: explains itself from its records"],
      ["Self-improvement voice", "30 epoch folds, w10 → w342"], ["Charter & milestones", "open capability milestones"]] },
    { id: "L4", name: "Speak & verify", y: 6.4, r: 3.0, blurb: "Turning a bound answer into cited text, and refusing what fails a check.", mods: [
      ["Receipts", "w536: a relation answer names the record it read, both ends with ids"],
      ["Final-answer checks", "w532–w534: sign kept, private questions, false date premise, thousands, units, word sense"],
      ["Same-name check", "w538: stays with the thing the conversation is about"],
      ["Supporting sentence", "w538: a quoted sentence that lost its numbers is dropped"],
      ["Answer checks", "w539 · w540: a name is not arithmetic; a count names what it counts; a question's direction; a zero read back; a definition is not a private answer"],
      ["Precision guard", "declines what it cannot verify, and says why"], ["Speaker", "evidence-bound"]] },
    { id: "L3", name: "Conversation state", y: 4.8, r: 3.5, blurb: "What the conversation is about, and what was already said.", mods: [
      ["Conversation engine", "subject, topic, last answer and last result, per session"],
      ["Follow-up resolver", "\"When was he born?\" is read against the last answer"],
      ["Two-part turns", "w533 · w537: each part goes through the whole pipeline"],
      ["Hand-offs", "w533: a follow-up goes back to the specialist that answered"],
      ["Conversation acts", "greetings, thanks, clarification"], ["Dialogue organ", "w480: what did I ask, you didn't answer me"]] },
    { id: "L2", name: "Route", y: 3.2, r: 3.9, blurb: "Choosing what answers: a specialist, an organ, or the stored text.", mods: [
      ["Exact router", "w524: typed question shapes to one relation"],
      ["General reader", "w539 · w540: one Wikidata fact away, on reading declines; held-out 81 of 82"],
      ["Family precedence", "w536: relation specialists answer relation questions first (34 more right, 0 lost)"],
      ["Specialist call", "picks the admitted specialist for the domain"], ["Organ dispatch", "w480: math, relation, dialogue, code"],
      ["Factoid & reading", "w420 · w432 · w434 · w442"], ["Deliberation", "where / when / who over stored text"],
      ["Capability routes", "summarize, compare, timeline, explain…"], ["Compose", "w426: inference over two sentences"],
      ["Path memory", "research: learned route credit; off until it wins a sealed test"],
      ["Front parser", "about half of open trivia phrasings are not parsed (census 10-13); declined, never guessed", "hazard"]] },
    { id: "L1", name: "Parse", y: 1.6, r: 3.5, blurb: "From words to a typed request.", mods: [
      ["Construction grammar", "K8 grammar, runtime N"], ["Typed request / λ-IR", "M13E4 runtime, frozen"], ["Obligations IR", "program_ir_v1"],
      ["Splitting", "runtimes AJ · AK · and-parts w533"], ["Frame", "w34"]] },
    { id: "L0", name: "Intake", y: 0.0, r: 3.0, blurb: "Where a request arrives and leaves.", mods: [
      ["Front door", "chat(text, session): sessions, provenance"], ["Harness v21", "response contract"], ["Salience arbitrator", "harness v20"],
      ["Live demo", "a public talk page · nothing typed is stored"]] },
    { id: "S", name: "Specialists", y: -1.8, r: 4.3, blurb: "267 small verified programs. Each was admitted by a held-out exam it saw once; 23 failed and stayed out. On their exams: 15,478 right, 14 wrong.", spec: true, mods: [
      ["Relation readers", "161: moons, directors, novels, painters, composers…"], ["Physical science", "densities, units, energy, thermo, optics, decay…"],
      ["Earth & life", "geology, ecology, botany, medicine, genetics…"], ["Computing", "python, sql, git, linux, networking…"],
      ["Space", "orbits, spacecraft, space comms, planetary"], ["Everyday", "cooking, gardening, first aid, finance…"],
      ["Humanities", "literature, law, music, world history…"], ["Exam ledger", "every admission and failure, published"]] },
    { id: "E", name: "Engines", y: -3.6, r: 3.7, blurb: "Computing what should never be memorised.", engine: true, mods: [
      ["Calculator", "w29 · w458: calculator or refuse"], ["Algebra", "w55"], ["Deduction", "w54 · closure runtime AD"], ["Dates", "runtimes Y · AB"],
      ["TeX reader", "w428"], ["Math organ", "exact moves, independently checked"], ["Code organ", "w482 · w486: run on your examples, graded"],
      ["Word problems", "w488: single-step schemas"], ["Weight from mass", "w538: W = m·g from a stated mass"], ["Operator host", "w59 · w61 · w65"]] },
    { id: "V", name: "Knowledge vault", y: -5.4, r: 5.2, blurb: "Everything it knows, each sentence addressable and cited.", store: true, mods: [
      ["Deep store", "6,339,707 pages · 20,529,863 sentences"], ["Relation edges", "edges.sqlite, 2.2 GB"], ["ConceptNet", "3,422,938 edges"],
      ["Wiktionary", "1,486,439 entries"], ["WordNet", "kinds, hypernyms"], ["Textbook store", "20 books · 143,355 typed items"], ["Relation store", "Wikidata · 10.35M entities"]] },
  ];
  const LOOP = [["Failure inbox", "structured failure records", 270], ["Fold worker", "repairs drafted from the inbox", 215], ["Candidate", "one in flight at a time", 150],
    ["GATE", "4,114 held-out checks; nothing may get worse", 90, "gate"], ["HEAD_MANIFEST", "every consumer resolves the tip here", 35],
    ["Sealed tests", "written before the build, run once (12–19)", 5], ["Served head", "w540", 342], ["Benchmark organ", "rotating unseen windows", 318], ["Stimuli organ", "random conversation pressure", 294]];
  const FAMILY = [["oracle7-deepspace", "98.9% on fresh spacecraft faults"], ["oracle7-vision", "MNIST 98.58% · cites its examples"], ["oracle7-trafficcop", "30/32 held-out routes"],
    ["oracle7-chameleon", "builds sites · 0 false completions"], ["oracle7-artist", "composes from cited parts"]];

  function O7Explorer(host, opt) {
    opt = opt || {};
    const P = Object.assign({ ink: 0x15100d, line: 0x342820, accent: 0x2f7d73, store: 0x2a3b52, hazard: 0xc49132, fresh: 0xc0602e, bad: 0x9a3b1d, spec: 0x946d1e, lit: 0xc0602e, muted: 0x6a5a47, discOpacity: 0.05, lineOpacity: 0.6 }, opt.palette || {});
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const canvas = document.createElement("canvas"); canvas.className = "o7-canvas"; host.appendChild(canvas);
    const labelsEl = document.createElement("div"); labelsEl.className = "o7-labels"; host.appendChild(labelsEl);
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
    const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(38, 1, 0.1, 500);
    const controls = new THREE.OrbitControls(camera, canvas);
    controls.enableDamping = true; controls.dampingFactor = 0.08; controls.minDistance = 8; controls.maxDistance = 80; controls.enableZoom = opt.zoom !== false;
    controls.autoRotate = !reduce; controls.autoRotateSpeed = 0.35;
    canvas.addEventListener("pointerdown", () => { controls.autoRotate = false; });

    function line(points, color, opacity, dashed) {
      const g = new THREE.BufferGeometry().setFromPoints(points);
      const m = dashed ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.25, gapSize: 0.18 }) : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
      const l = new THREE.Line(g, m); if (dashed) l.computeLineDistances(); return l;
    }
    const circle = (r, seg) => { const p = []; for (let i = 0; i <= seg; i++) { const a = i / seg * Math.PI * 2; p.push(new THREE.Vector3(Math.cos(a) * r, 0, Math.sin(a) * r)); } return p; };
    const labels = [];
    function label(text, getPos, cls, show, extra) { const el = document.createElement("div"); el.className = "o7l " + (cls || ""); el.textContent = text; labelsEl.appendChild(el); const L = Object.assign({ el, getPos, show: show || (() => true) }, extra || {}); labels.push(L); return L; }

    const st = { mode: opt.mode || "improve", selected: opt.select === undefined ? "L2" : opt.select, showAll: false, spread: 0, spreadT: 0, cube: false };
    const stageObjs = [], idx = s => STAGES.length - 1 - STAGES.indexOf(s), stageY = s => s.y + st.spread * (idx(s) - 3) * 0.9;
    STAGES.forEach(s => {
      const g = new THREE.Group(); scene.add(g);
      const col = s.store ? P.store : P.line;
      const disc = new THREE.Mesh(new THREE.CircleGeometry(s.r, 64).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: s.store ? P.store : P.accent, transparent: true, opacity: P.discOpacity, side: THREE.DoubleSide, depthWrite: false }));
      disc.userData.stage = s.id; g.add(disc);
      g.add(line(circle(s.r, 96), col, P.lineOpacity)); g.add(line(circle(s.r * 0.35, 48), col, 0.2));
      const mods = [];
      s.mods.forEach((m, i) => {
        const a = i / s.mods.length * Math.PI * 2 + s.y * 0.3, hz = m[2] === "hazard", x = Math.cos(a) * s.r, z = Math.sin(a) * s.r;
        const geo = s.engine ? new THREE.BoxGeometry(0.28, 0.28, 0.28) : s.spec ? new THREE.SphereGeometry(0.17, 12, 8) : new THREE.OctahedronGeometry(hz ? 0.26 : 0.17);
        const base = hz ? P.hazard : s.store ? P.store : s.spec ? P.spec : P.accent;
        const node = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: base }));
        node.position.set(x, 0, z); node.userData.stage = s.id; g.add(node);
        g.add(line([new THREE.Vector3(0, 0, 0), new THREE.Vector3(x, 0, z)], col, hz ? 0.55 : 0.14));
        let Lr = null;
        Lr = label(m[0], () => new THREE.Vector3(x, g.position.y + 0.1, z), hz ? "hazard" : s.store ? "store" : s.spec ? "spec" : "", () => st.showAll || st.selected === s.id || (hz && !st.quiet) || (Lr && Lr.lit));
        mods.push({ x, z, hz, name: m[0], node, base, L: Lr });
      });
      const LL = label(s.name, () => new THREE.Vector3(s.r + 0.4, g.position.y, 0), "layer", null, { stage: s.id });
      LL.el.style.pointerEvents = "auto"; LL.el.style.cursor = "pointer";
      LL.el.addEventListener("click", () => { api.select(s.id); opt.onSelect && opt.onSelect(s.id); });
      stageObjs.push({ s, g, disc, mods });
    });
    const V = stageObjs.find(o => o.s.store);
    { const n = 6000, pos = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) { const r = Math.sqrt(Math.random()) * 5.1, a = Math.random() * Math.PI * 2; pos[i * 3] = Math.cos(a) * r; pos[i * 3 + 1] = (Math.random() - 0.5) * 0.5 * (1 - r / 6); pos[i * 3 + 2] = Math.sin(a) * r; }
      const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      V.cloud = new THREE.Points(geo, new THREE.PointsMaterial({ color: P.store, size: 0.035, transparent: true, opacity: 0.6 })); V.g.add(V.cloud); }
    label("20,529,863 cited sentences", () => new THREE.Vector3(0, V.g.position.y - 0.7, 5.4), "store");
    const spine = line([new THREE.Vector3(0, -3.8, 0), new THREE.Vector3(0, 8.6, 0)], P.accent, 0.7); scene.add(spine);

    const LC = { y: 2.1, rx: 8.2, ry: 7.4 };
    const loopPt = (deg, out) => { const a = deg * Math.PI / 180; return (out || new THREE.Vector3()).set(Math.cos(a) * LC.rx, LC.y + Math.sin(a) * LC.ry, 0); };
    const loopPts = []; for (let i = 0; i <= 160; i++) loopPts.push(loopPt(i / 160 * 360));
    const loopLine = line(loopPts, P.accent, 0.5, true); scene.add(loopLine);
    const gateMesh = new THREE.Mesh(new THREE.TorusGeometry(0.75, 0.05, 8, 48), new THREE.MeshBasicMaterial({ color: P.accent })); gateMesh.position.copy(loopPt(90)); scene.add(gateMesh);
    LOOP.forEach(L => { const p = loopPt(L[2]);
      if (L[3] !== "gate") { const b = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.34, 0.34), new THREE.MeshBasicMaterial({ color: P.accent })); b.position.copy(p); scene.add(b); }
      label(L[0], () => p.clone().add(new THREE.Vector3(0, L[3] === "gate" ? 1.0 : 0.25, 0)), L[3] === "gate" ? "gate" : "loop", () => st.mode === "improve" || st.showAll || L[3] === "gate"); });
    label("Self-improvement loop", () => loopPt(160).add(new THREE.Vector3(-0.4, 0, 0)), "big loop", () => st.mode === "improve");
    const lp = new THREE.Mesh(new THREE.SphereGeometry(0.18, 16, 12), new THREE.MeshBasicMaterial({ color: P.accent })); scene.add(lp);
    const rejects = [];

    const famObjs = FAMILY.map((f, i) => {
      const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 1), new THREE.MeshBasicMaterial({ color: P.accent, wireframe: true }));
      m.add(new THREE.Mesh(new THREE.SphereGeometry(0.16, 12, 8), new THREE.MeshBasicMaterial({ color: P.ink }))); scene.add(m);
      const tether = line([new THREE.Vector3(), new THREE.Vector3(0, 1, 0)], P.accent, 0.25, true); scene.add(tether);
      label(f[0], () => m.position.clone().add(new THREE.Vector3(0, 0.55, 0)), "fam", () => st.mode === "family" || st.showAll);
      label(f[1], () => m.position.clone().add(new THREE.Vector3(0, -0.25, 0)), "famsub", () => st.mode === "family");
      return { m, tether, a0: i / FAMILY.length * Math.PI * 2 };
    });
    const famOrbit = line(circle(11.5, 128), P.muted, 0.25, true); famOrbit.position.y = 3.2; scene.add(famOrbit);

    const SEPH = { keter: [0, 6.6], chokmah: [1.7, 5.6], binah: [-1.7, 5.6], chesed: [1.7, 4.4], geburah: [-1.7, 4.4], tiferet: [0, 3.3], netzach: [1.7, 2.2], hod: [-1.7, 2.2], yesod: [0, 1.2], malkuth: [0, 0] };
    const PATHS = [["keter","chokmah"],["keter","binah"],["keter","tiferet"],["chokmah","binah"],["chokmah","tiferet"],["chokmah","chesed"],["binah","tiferet"],["binah","geburah"],["chesed","geburah"],["chesed","tiferet"],["chesed","netzach"],["geburah","tiferet"],["geburah","hod"],["tiferet","netzach"],["tiferet","yesod"],["tiferet","hod"],["netzach","hod"],["netzach","yesod"],["netzach","malkuth"],["hod","yesod"],["hod","malkuth"],["yesod","malkuth"]];
    const MID = new Set(["keter", "tiferet", "yesod", "malkuth"]);
    const cube = new THREE.Group(); cube.visible = false; scene.add(cube);
    [0, 60, 120].forEach((deg, ti) => {
      const a = deg * Math.PI / 180, tp = s => { const [x0, y] = SEPH[s]; const x = MID.has(s) ? 0 : x0 * 0.6; return new THREE.Vector3(x * Math.cos(a), y * (8 / 6.6), -x * Math.sin(a)); };
      const pts = []; PATHS.forEach(([p, q]) => { if (!(MID.has(p) && MID.has(q)) || ti === 0) pts.push(tp(p), tp(q)); });
      cube.add(new THREE.LineSegments(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: P.fresh, transparent: true, opacity: 0.85 })));
    });
    label("Reasoning cube (proposed)", () => new THREE.Vector3(0, 10.1, 0), "new big", () => st.cube);

    const rq = new THREE.Mesh(new THREE.SphereGeometry(0.2, 16, 12), new THREE.MeshBasicMaterial({ color: P.ink })); scene.add(rq);
    let rqT = 0, rqStop = false;
    const Y = id => stageObjs.find(o => o.s.id === id).g.position.y;
    const modPt = (sid, name) => { const o = stageObjs.find(o => o.s.id === sid); const d = o.mods.find(m => m.name === name) || o.mods[0]; return new THREE.Vector3(d.x, o.g.position.y, d.z); };
    function rqPath() {
      const up = id => new THREE.Vector3(0, Y(id), 0);
      if (st.cube) return [up("L0"), up("L1"), up("L2"), new THREE.Vector3(0, Y("E"), 0), new THREE.Vector3(2.5, Y("V"), 1.5), up("L3"), up("L4"), up("L0")];
      // a typical answer: parse, read the conversation, route to a specialist, read its record, check, speak. Some are declined at the guard.
      return rqStop ? [up("L0"), up("L1"), up("L3"), modPt("L2", "Specialist call"), modPt("S", "Relation readers"), modPt("V", "Relation store"), modPt("L4", "Precision guard"), modPt("L4", "Precision guard"), up("L0")]
                    : [up("L0"), up("L1"), up("L3"), modPt("L2", "Specialist call"), modPt("S", "Relation readers"), modPt("V", "Relation store"), modPt("L4", "Receipts"), up("L4"), up("L0")];
    }

    const traceLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: P.lit, transparent: true, opacity: 0.95 }));
    traceLine.visible = false; scene.add(traceLine);
    function clearTrace() {
      stageObjs.forEach(o => o.mods.forEach(m => { if (m.L.lit) { m.L.lit = false; m.L.el.classList.remove("lit"); m.node.material.color.setHex(m.base); m.node.scale.setScalar(1); } }));
      st.trace = null;
    }
    const api = {
      data: { STAGES, LOOP, FAMILY },
      trace(steps, declined) {
        clearTrace();
        const refs = [];
        (steps || []).forEach(([sid, name]) => { const o = stageObjs.find(x => x.s.id === sid); if (!o) return;
          const m = name ? o.mods.find(x => x.name === name) || null : null;
          const last = refs[refs.length - 1]; if (last && last.o === o && last.m === m) return; refs.push({ o, m }); });
        if (!refs.length) return [];
        st.trace = refs; st.traceT = 0; st.traceDeclined = !!declined; st.mode = "trace"; controls.autoRotate = false;
        return refs.filter(r => r.m).map(r => [r.o.s.name, r.m.name]);
      },
      clearTrace() { clearTrace(); if (st.mode === "trace") st.mode = opt.mode || "improve"; },
      setQuiet(on) { st.quiet = !!on; },
      setMode(m) { st.mode = m; },
      get mode() { return st.mode; },
      select(id) { st.selected = id; stageObjs.forEach(o => { o.disc.material.opacity = o.s.id === id ? P.discOpacity * 3.5 : P.discOpacity; }); labels.forEach(L => { if (L.stage) L.el.classList.toggle("sel", L.stage === id); }); },
      setSpread(on) { st.spreadT = on ? 1 : 0; if (reduce) st.spread = st.spreadT; },
      setCube(on) { st.cube = !!on; cube.visible = st.cube; },
      setShowAll(on) { st.showAll = !!on; },
      canvas,
      // a specialist you admitted joins the Specialists ring, outside the release's own groups
      addModule(sid, name) {
        const o = stageObjs.find(x => x.s.id === sid); if (!o || o.mods.some(m => m.name === name)) return;
        const k = o.mods.filter(m => m.mine).length, a = -Math.PI / 2 + k * 0.42, R = o.s.r + 1.3, x = Math.cos(a) * R, z = Math.sin(a) * R;
        const node = new THREE.Mesh(new THREE.OctahedronGeometry(0.24), new THREE.MeshBasicMaterial({ color: P.fresh }));
        node.position.set(x, 0, z); node.userData.stage = sid; o.g.add(node);
        o.g.add(line([new THREE.Vector3(Math.cos(a) * o.s.r, 0, Math.sin(a) * o.s.r), new THREE.Vector3(x, 0, z)], P.fresh, 0.7, true));
        const m = { x, z, hz: false, name, node, base: P.fresh, mine: true }; let Lr = null;
        Lr = label(name, () => new THREE.Vector3(x, o.g.position.y + 0.1, z), "mine", () => true); m.L = Lr; o.mods.push(m);
      },
      // what is on screen, for drawing a film frame: every visible label with its pixel position and class
      labelsOnScreen() { return labels.filter(L => L.el.style.display !== "none").map(L => ({ text: L.el.textContent, x: parseFloat(L.el.style.left) || 0, y: parseFloat(L.el.style.top) || 0, cls: L.el.className })); },
      setView(v) { const VIEWS = { iso: [20, 11, 24], side: [0.01, 2.6, 34], top: [0.01, 44, 0.02] }; camera.position.set(...VIEWS[v]); controls.target.set(0, 1.6, 0); controls.update(); },
    };
    const ray = new THREE.Raycaster(), mouse = new THREE.Vector2(); let downAt = null;
    canvas.addEventListener("pointerdown", e => { downAt = [e.clientX, e.clientY]; });
    canvas.addEventListener("pointerup", e => {
      if (!downAt || Math.hypot(e.clientX - downAt[0], e.clientY - downAt[1]) > 5) return;
      const r = canvas.getBoundingClientRect(); mouse.set((e.clientX - r.left) / r.width * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      ray.setFromCamera(mouse, camera); const hit = ray.intersectObjects(stageObjs.map(o => o.g), true).find(h => h.object.userData.stage);
      if (hit) { api.select(hit.object.userData.stage); opt.onSelect && opt.onSelect(hit.object.userData.stage); }
    });
    function resize() { const w = host.clientWidth, h = host.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
    new ResizeObserver(resize).observe(host);

    const v = new THREE.Vector3(); let last = performance.now(), loopDeg = 270, cycle = 0;
    function frame(now) {
      const dt = Math.max(0, Math.min(0.05, (now - last) / 1000)), s = now / 1000; last = now;
      st.spread += (st.spreadT - st.spread) * Math.min(1, dt * 4);
      stageObjs.forEach(o => { o.g.position.y = stageY(o.s); });
      if (!reduce) V.cloud.rotation.y += dt * 0.05;
      spine.geometry.setFromPoints([new THREE.Vector3(0, Y("V"), 0), new THREE.Vector3(0, Y("L5") + 0.6, 0)]);
      if (!reduce) loopDeg -= dt * 40; if (loopDeg < -90) loopDeg += 360;
      const d = ((loopDeg % 360) + 360) % 360; loopPt(d, lp.position);
      lp.visible = st.mode === "improve"; loopLine.material.opacity = st.mode === "improve" ? 0.7 : 0.25;
      gateMesh.rotation.y = s * 0.8; gateMesh.scale.setScalar(1 + 0.08 * Math.sin(s * 3));
      if (st.mode === "improve" && Math.abs(d - 90) < dt * 40 + 0.01) {
        cycle++;
        if (cycle % 3 === 0) { lp.material.color.setHex(P.bad); const rj = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8), new THREE.MeshBasicMaterial({ color: P.bad, transparent: true })); rj.position.copy(lp.position); rj.userData.v = new THREE.Vector3(1.8, 2.4, 1.2); scene.add(rj); rejects.push(rj); opt.onGate && opt.onGate(false); }
        else { lp.material.color.setHex(P.accent); opt.onGate && opt.onGate(true); }
      }
      if (d < 60 || d > 280) lp.material.color.setHex(P.accent);
      for (let i = rejects.length - 1; i >= 0; i--) { const r = rejects[i]; r.position.addScaledVector(r.userData.v, dt); r.userData.v.y -= dt * 3; r.material.opacity -= dt * 0.6; if (r.material.opacity <= 0) { scene.remove(r); rejects.splice(i, 1); } }
      famObjs.forEach((f, i) => { const a = f.a0 + (reduce ? 0 : s * 0.08); f.m.position.set(Math.cos(a) * 11.5, 3.2 + Math.sin(s * 0.7 + i) * 0.3, Math.sin(a) * 11.5); f.m.rotation.y = s * 0.5;
        f.tether.geometry.setFromPoints([f.m.position, new THREE.Vector3(0, Y("L2"), 0)]); f.tether.computeLineDistances(); f.tether.material.opacity = st.mode === "family" ? 0.6 : 0.12; });
      famOrbit.material.opacity = st.mode === "family" ? 0.45 : 0.15;
      rq.visible = st.mode === "answer" || st.mode === "trace";
      traceLine.visible = st.mode === "trace";
      if (st.mode === "trace" && st.trace) {
        const pts = st.trace.map(r => r.m ? new THREE.Vector3(r.m.x, r.o.g.position.y, r.m.z) : new THREE.Vector3(0, r.o.g.position.y, 0));
        const n = pts.length - 1;
        if (n <= 0) { rq.position.copy(pts[0]); } else {
          st.traceT = reduce ? n : Math.min(n, st.traceT + dt * 1.5);
          const i = Math.min(n - 1, Math.floor(st.traceT)), k = st.traceT - i;
          rq.position.copy(pts[i]).lerp(pts[i + 1], Math.min(1, k));
          const drawn = pts.slice(0, i + 1).concat([rq.position.clone()]);
          traceLine.geometry.setFromPoints(drawn);
          st.trace.forEach((r, j) => { if (r.m && j <= st.traceT + 0.01 && !r.m.L.lit) { r.m.L.lit = true; r.m.L.el.classList.add("lit"); r.m.node.material.color.setHex(P.lit); r.m.node.scale.setScalar(1.9); } });
        }
        rq.material.color.setHex(st.traceDeclined ? P.hazard : P.lit);
      }
      if (st.mode === "answer") {
        const path = rqPath(); if (!reduce) rqT += dt * 0.9;
        if (rqT >= path.length - 1) { rqT = 0; rqStop = Math.random() < 0.3; }
        const i = Math.max(0, Math.min(path.length - 2, Math.floor(rqT))), k = Math.min(1, Math.max(0, rqT - i)); rq.position.copy(path[i]).lerp(path[Math.min(path.length - 1, i + 1)], k);
        rq.material.color.setHex(!st.cube && rqStop && i >= 6 ? P.hazard : st.cube ? P.fresh : P.ink);
      }
      controls.update(); renderer.render(scene, camera);
      const w = host.clientWidth, h = host.clientHeight;
      labels.forEach(L => { if (!L.show()) { L.el.style.display = "none"; return; } v.copy(L.getPos()).project(camera);
        if (v.z > 1) { L.el.style.display = "none"; return; } L.el.style.display = ""; L.el.style.left = ((v.x + 1) / 2 * w) + "px"; L.el.style.top = ((1 - v.y) / 2 * h) + "px"; });
      requestAnimationFrame(frame);
    }
    resize(); api.setView(opt.view || "iso"); if (st.selected) api.select(st.selected);
    requestAnimationFrame(frame);
    return api;
  }
  O7Explorer.data = { STAGES, LOOP, FAMILY };
  window.O7Explorer = O7Explorer;
})();
