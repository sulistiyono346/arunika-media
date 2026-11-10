// ARN-40 "Bayangkan kamu... kamu pilih apa?" — 3D sinematik gelap (three.js r160, lokal).
// Deterministik: window.renderFrame(t) menggambar frame waktu t (detik) ke <canvas id="out"> 1080x1920.
import * as THREE from './three.module.js';

const W = 1080, H = 1920;
const NAVY = 0x14215B, TEAL = 0x12C2B0, YEL = 0xFFB800;
const CNAVY = '#14215B', CTEAL = '#12C2B0', CYEL = '#FFB800';
const T = await (await fetch('timing.json')).json();
const CH = T.chunks, SC = T.scenes, TOTAL = T.total;
const cs = i => CH[i].s;          // awal chunk i (detik video)
const CLOSE = SC[14];

// ---------- util ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;
const ease = u => { u = clamp(u); return u * u * (3 - 2 * u); };
const easeOut = u => { u = clamp(u); return 1 - Math.pow(1 - u, 3); };
const ramp = (t, a, d = 0.3) => ease((t - a) / d);
function mulberry(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const noise1 = x => { const i = Math.floor(x), f = x - i; return lerp(hash(i), hash(i + 1), f * f * (3 - 2 * f)); };
const fmt = n => Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');

// ---------- renderer ----------
const glc = document.createElement('canvas'); glc.width = W; glc.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.15;
const out = document.getElementById('out'); const ctx = out.getContext('2d');
const small = document.createElement('canvas'); small.width = 180; small.height = 320; const sctx = small.getContext('2d');

await Promise.all([
  new FontFace('PB', 'url(Poppins-Bold.ttf)').load().then(f => document.fonts.add(f)),
  new FontFace('PM', 'url(Poppins-Medium.ttf)').load().then(f => document.fonts.add(f)),
]);
const logo = new Image(); logo.src = 'arunika-logo-putih.png'; await logo.decode();

// ---------- tekstur ----------
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const softTex = canvasTex(128, 128, (g, w, h) => { const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.35, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); });
const smokeTex = canvasTex(128, 128, (g, w, h) => { const R = mulberry(7); for (let i = 0; i < 14; i++) { const x = 30 + R() * 68, y = 30 + R() * 68, rr = 18 + R() * 26; const r = g.createRadialGradient(x, y, 0, x, y, rr); r.addColorStop(0, 'rgba(255,255,255,.35)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); } });
const cloudTex = canvasTex(1024, 1024, (g, w, h) => { g.fillStyle = '#1b2d58'; g.fillRect(0, 0, w, h); const R = mulberry(3); for (let i = 0; i < 700; i++) { const x = R() * w, y = R() * h, rr = 20 + R() * 90; const c = 60 + R() * 60; for (const dx of [-w, 0, w]) for (const dy of [-h, 0, h]) { const r = g.createRadialGradient(x + dx, y + dy, 0, x + dx, y + dy, rr); r.addColorStop(0, `rgba(${c},${c + 25},${c + 70},.35)`); r.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = r; g.fillRect(x + dx - rr, y + dy - rr, rr * 2, rr * 2); } } });
cloudTex.wrapS = cloudTex.wrapT = THREE.RepeatWrapping; cloudTex.repeat.set(6, 6);

const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.0, ...o });
const emis = (color, k = 1) => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: color, emissiveIntensity: k, roughness: 1 });
const addMat = (color, op = 1) => new THREE.SpriteMaterial({ map: softTex, color, transparent: true, opacity: op, blending: THREE.AdditiveBlending, depthWrite: false });
function sprite(color, s, op = 1) { const m = new THREE.Sprite(addMat(color, op)); m.scale.set(s, s, 1); return m; }

// ---------- Aru 3D (desain Syal Bendera) ----------
function makeAru() {
  const g = new THREE.Group();
  const skin = std(0xFFD5B5, { roughness: 0.5 }), navyM = std(NAVY, { roughness: 0.7 }), tealM = std(TEAL, { roughness: 0.55 }), yelM = std(YEL, { roughness: 0.55 });
  const head = new THREE.Group(); head.position.y = 1.0; g.add(head); g.userData.head = head;
  head.add(new THREE.Mesh(new THREE.IcosahedronGeometry(1, 4), skin));
  for (const s of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), skin); e.position.set(s * 0.98, -0.05, 0); head.add(e); }
  const eyeM = std(0x0d1433, { roughness: 0.25 }), hiM = emis(0xffffff, 1.6), blushM = std(0xFFA48C, { roughness: 0.8 });
  g.userData.eyes = [];
  for (const s of [-1, 1]) {
    const eye = new THREE.Group(); eye.position.set(s * 0.34, 0.05, 0.9); eye.rotation.y = s * 0.33; head.add(eye); g.userData.eyes.push(eye);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), eyeM); ball.scale.set(0.13, 0.17, 0.08); eye.add(ball);
    const hi = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 6), hiM); hi.position.set(0.035, 0.06, 0.07); eye.add(hi);
    const bl = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8), blushM); bl.scale.set(0.15, 0.08, 0.04); bl.position.set(s * 0.56, -0.3, 0.8); bl.rotation.y = s * 0.6; head.add(bl);
    const brow = new THREE.Mesh(new THREE.CapsuleGeometry(0.035, 0.2, 4, 8), navyM); brow.rotation.z = Math.PI / 2; brow.position.set(s * 0.33, 0.36, 0.93); brow.rotation.y = s * 0.3; head.add(brow); (g.userData.brows ||= []).push(brow);
  }
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.028, 8, 20, Math.PI), std(0x5a2030)); mouth.position.set(0, -0.33, 0.95); mouth.rotation.z = Math.PI; head.add(mouth); g.userData.mouth = mouth;
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.7, 0.7, 6, 16), navyM); body.position.y = -0.55; body.scale.set(1, 1, 0.85); g.add(body);
  const scarf = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.2, 12, 32), tealM); scarf.rotation.x = Math.PI / 2; scarf.position.y = 0.02; g.add(scarf);
  const flag = new THREE.Group(); flag.position.set(0.42, -0.2, 0.62); flag.rotation.set(0.15, -0.2, -0.25); g.add(flag); g.userData.flag = flag;
  const f1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.06), tealM); f1.position.set(0.2, 0, 0); flag.add(f1);
  const f2 = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.2, 0.06), yelM); f2.position.set(0.17, -0.22, 0); flag.add(f2);
  g.userData.arms = [];
  for (const s of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(s * 0.72, -0.25, 0); g.add(arm); g.userData.arms.push(arm);
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.5, 4, 10), navyM); up.position.y = -0.3; arm.add(up);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.19, 14, 10), skin); hand.position.y = -0.72; arm.add(hand);
    arm.rotation.z = s * 0.15; arm.rotation.x = -0.9;
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.7, 4, 10), std(0x4d4a5a)); leg.position.set(s * 0.3, -1.25, 0.45); leg.rotation.x = Math.PI / 2; g.add(leg);
  }
  return g;
}
function setAruFace(aru, mood) { // mood: 0 cemas, 1 lega
  const m = aru.userData.mouth; m.rotation.z = mood > 0.5 ? Math.PI : 0; m.position.y = mood > 0.5 ? -0.26 : -0.4;
  aru.userData.brows.forEach((b, i) => { const s = i ? 1 : -1; b.rotation.x = 0; b.rotation.order = 'YXZ'; b.rotation.z = Math.PI / 2 + s * (mood > 0.5 ? 0.12 : -0.28); b.position.y = mood > 0.5 ? 0.4 : 0.37; });
}
function makeToy(R, hatColor) {
  const g = new THREE.Group();
  const head = new THREE.Mesh(new THREE.IcosahedronGeometry(0.42, 3), std(0xe8e6ea, { roughness: 0.45 })); head.position.y = 0.42; g.add(head);
  if (hatColor !== null) { const hat = new THREE.Mesh(new THREE.SphereGeometry(0.44, 16, 8, 0, Math.PI * 2, 0, Math.PI / 2), std(hatColor)); hat.position.y = 0.5; g.add(hat); }
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.32, 0.3, 4, 10), std([0x2a3550, 0x3b4766, 0x1f2c4f, 0x51607e][Math.floor(R() * 4)])); body.position.y = -0.2; g.add(body);
  return g;
}

// ---------- KABIN ----------
const cabin = new THREE.Scene(); cabin.background = new THREE.Color(0x060b1e); cabin.fog = new THREE.Fog(0x0a1330, 6, 26);
{
  const shell = new THREE.Mesh(new THREE.CylinderGeometry(3.0, 3.0, 60, 40, 1, true), std(0x6d7a98, { side: THREE.BackSide, roughness: 0.8 }));
  shell.rotation.x = Math.PI / 2; shell.position.set(0, 0.6, -20); cabin.add(shell);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(6, 60), std(0x1a2560, { roughness: 0.9 })); floor.rotation.x = -Math.PI / 2; floor.position.set(0, -1.5, -20); cabin.add(floor);
  const aisle = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 60), std(0x23337a, { roughness: 0.9 })); aisle.rotation.x = -Math.PI / 2; aisle.position.set(0, -1.49, -20); cabin.add(aisle);
  for (const s of [-1, 1]) { const strip = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.05, 60), emis(0xcfe0ff, 2.2)); strip.position.set(s * 0.9, 3.2, -20); cabin.add(strip);
    const bin = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.6, 60), std(0x8a96b2)); bin.position.set(s * 2.2, 2.6, -20); bin.rotation.z = s * 0.5; cabin.add(bin); }
  // kursi & penumpang (deretan)
  const R = mulberry(11);
  const seatM = std(0x1f3a8f, { roughness: 0.75 }), headrestM = std(0x2c4aa8);
  const seatBack = new THREE.BoxGeometry(0.62, 1.15, 0.22), seatBase = new THREE.BoxGeometry(0.62, 0.22, 0.6), hr = new THREE.BoxGeometry(0.5, 0.28, 0.12);
  const xs = [-2.05, -1.35, 1.35, 2.05];
  const winGlass = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0x2f7dff, emissiveIntensity: 1.1, roughness: 1 });
  cabin.userData.winMats = [winGlass];
  for (let row = 0; row < 18; row++) {
    const z = 1.2 - row * 1.45;
    for (const x of xs) {
      const back = new THREE.Mesh(seatBack, seatM); back.position.set(x, -0.35, z + 0.32); cabin.add(back);
      const base = new THREE.Mesh(seatBase, seatM); base.position.set(x, -0.85, z); cabin.add(base);
      const h = new THREE.Mesh(hr, headrestM); h.position.set(x, 0.35, z + 0.3); cabin.add(h);
      if (row === 0 && x === -2.05) continue; // kursi Aru
      if (row > 0 && R() < 0.85) { const hats = [0xc0392b, 0xF2B233, 0xffffff, TEAL, 0x2b4fa0, null, null]; const toy = makeToy(R, hats[Math.floor(R() * hats.length)]); toy.position.set(x, 0.15, z + 0.12); toy.rotation.y = (R() - 0.5) * 0.4; cabin.add(toy); }
    }
    for (const s of [-1, 1]) { const sh = new THREE.Shape(); const w = 0.36, hh = 0.5, r = 0.16; sh.moveTo(-w / 2 + r, -hh / 2); sh.lineTo(w / 2 - r, -hh / 2); sh.quadraticCurveTo(w / 2, -hh / 2, w / 2, -hh / 2 + r); sh.lineTo(w / 2, hh / 2 - r); sh.quadraticCurveTo(w / 2, hh / 2, w / 2 - r, hh / 2); sh.lineTo(-w / 2 + r, hh / 2); sh.quadraticCurveTo(-w / 2, hh / 2, -w / 2, hh / 2 - r); sh.lineTo(-w / 2, -hh / 2 + r); sh.quadraticCurveTo(-w / 2, -hh / 2, -w / 2 + r, -hh / 2);
      const win = new THREE.Mesh(new THREE.ShapeGeometry(sh), winGlass); win.position.set(s * 2.83, 0.55, z - 0.2); win.rotation.y = -s * Math.PI / 2 * 0.92; cabin.add(win); }
  }
  // jendela besar Aru (dekat kamera, dengan pemandangan luar)
  const viewTex = canvasTex(256, 384, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#061033'); gr.addColorStop(0.55, '#14306e'); gr.addColorStop(1, '#2a4f9a'); g.fillStyle = gr; g.fillRect(0, 0, w, h); const R2 = mulberry(5); for (let i = 0; i < 40; i++) { g.fillStyle = `rgba(255,255,255,${R2() * .6})`; g.fillRect(R2() * w, R2() * h * 0.4, 1.5, 1.5); } g.fillStyle = 'rgba(120,150,210,.35)'; for (let i = 0; i < 30; i++) { g.beginPath(); g.ellipse(R2() * w, h * 0.72 + R2() * h * 0.25, 40 + R2() * 60, 10 + R2() * 12, 0, 0, 7); g.fill(); } g.fillStyle = '#9aa6c4'; g.beginPath(); g.moveTo(0, h * 0.5); g.lineTo(w, h * 0.62); g.lineTo(w, h * 0.66); g.lineTo(0, h * 0.58); g.fill(); g.fillStyle = '#7c87a6'; g.beginPath(); g.ellipse(w * 0.55, h * 0.67, 34, 20, 0, 0, 7); g.fill(); });
  const bigWinMat = new THREE.MeshStandardMaterial({ map: viewTex, emissiveMap: viewTex, emissive: 0xffffff, emissiveIntensity: 1.0, roughness: 1 });
  const bwShape = new THREE.Shape(); { const w = 0.7, hh = 0.95, r = 0.3; bwShape.moveTo(-w / 2 + r, -hh / 2); bwShape.lineTo(w / 2 - r, -hh / 2); bwShape.quadraticCurveTo(w / 2, -hh / 2, w / 2, -hh / 2 + r); bwShape.lineTo(w / 2, hh / 2 - r); bwShape.quadraticCurveTo(w / 2, hh / 2, w / 2 - r, hh / 2); bwShape.lineTo(-w / 2 + r, hh / 2); bwShape.quadraticCurveTo(-w / 2, hh / 2, -w / 2, hh / 2 - r); bwShape.lineTo(-w / 2, -hh / 2 + r); bwShape.quadraticCurveTo(-w / 2, -hh / 2, -w / 2 + r, -hh / 2); }
  const bg = new THREE.ShapeGeometry(bwShape); const uv = bg.attributes.uv, p = bg.attributes.position; for (let i = 0; i < uv.count; i++) uv.setXY(i, p.getX(i) / 0.7 + 0.5, p.getY(i) / 0.95 + 0.5);
  const bigWin = new THREE.Mesh(bg, bigWinMat); bigWin.position.set(-2.8, 0.6, 0.85); bigWin.rotation.y = Math.PI / 2 * 0.9; cabin.add(bigWin); cabin.userData.bigWinMat = bigWinMat;
  const frame = new THREE.Mesh(new THREE.TorusGeometry(0.5, 0.06, 8, 32), std(0xb9c2d6)); frame.scale.set(0.78, 1.0, 1); frame.position.copy(bigWin.position).add(new THREE.Vector3(0.02, 0, 0)); frame.rotation.y = bigWin.rotation.y; cabin.add(frame);
  // Aru
  const aru = makeAru(); aru.scale.setScalar(0.42); aru.position.set(-2.05, 0.05, 1.25); aru.rotation.y = Math.PI; cabin.add(aru); cabin.userData.aru = aru;
  // lampu
  cabin.add(new THREE.HemisphereLight(0x8fa6e0, 0x101830, 0.9));
  const top = new THREE.DirectionalLight(0xdfe8ff, 1.3); top.position.set(0.5, 5, 2); cabin.add(top);
  const winL = new THREE.PointLight(0x3d8bff, 6, 6, 1.4); winL.position.set(-2.3, 0.6, 0.8); cabin.add(winL); cabin.userData.winLight = winL;
  const fill = new THREE.PointLight(0xffe2c0, 2.5, 10, 1.5); fill.position.set(0.2, 1.8, -1.5); cabin.add(fill);
  const face = new THREE.PointLight(0xffd6b0, 5, 5, 1.3); face.position.set(-0.7, 0.95, 0.45); cabin.add(face);
  // asap
  const N = 260, pos = new Float32Array(N * 3); const R3 = mulberry(21); const seeds = [];
  for (let i = 0; i < N; i++) { seeds.push([R3() * 5 - 2.5, R3(), R3() * 26 - 22, R3()]); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const smoke = new THREE.Points(sg, new THREE.PointsMaterial({ map: smokeTex, color: 0xb9bfcc, size: 1.8, transparent: true, opacity: 0, depthWrite: false, sizeAttenuation: true }));
  smoke.frustumCulled = false; cabin.add(smoke); cabin.userData.smoke = { pts: smoke, seeds, pos };
}

// ---------- PESAWAT ----------
function makePlane() {
  const g = new THREE.Group();
  const body = std(0x8d96ab, { roughness: 0.5, metalness: 0.2 }), dark = std(0x3a4258), belly = std(0x9aa1b3, { roughness: 0.5 });
  const fus = new THREE.Mesh(new THREE.CapsuleGeometry(0.55, 8.4, 8, 24), body); fus.rotation.z = Math.PI / 2; g.add(fus);
  const hump = new THREE.Mesh(new THREE.SphereGeometry(1, 24, 12), body); hump.scale.set(2.3, 0.62, 0.48); hump.position.set(2.7, 0.25, 0); g.add(hump);
  const wl = new THREE.Mesh(new THREE.BoxGeometry(7.2, 0.05, 1.12), emis(0xffe9c2, 1.8)); wl.position.set(-0.3, 0.15, 0); g.add(wl);
  const wl2 = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.04, 0.98), emis(0xffe9c2, 1.6)); wl2.position.set(2.8, 0.55, 0); g.add(wl2);
  const ck = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.1, 0.7), dark); ck.position.set(4.55, 0.38, 0); g.add(ck);
  const wingShape = new THREE.Shape([[1.0, 0.4], [-2.6, 6.2], [-3.4, 6.2], [-1.6, 0.4]].map(p => new THREE.Vector2(p[0], p[1])));
  const wingGeo = new THREE.ExtrudeGeometry(wingShape, { depth: 0.08, bevelEnabled: false }); wingGeo.rotateX(Math.PI / 2);
  for (const s of [1, -1]) { const w = new THREE.Mesh(wingGeo, body); w.scale.z = s; w.position.y = -0.18; g.add(w); }
  const stabShape = new THREE.Shape([[-3.9, 0.3], [-5.0, 2.2], [-5.4, 2.2], [-4.9, 0.3]].map(p => new THREE.Vector2(p[0], p[1])));
  const stabGeo = new THREE.ExtrudeGeometry(stabShape, { depth: 0.05, bevelEnabled: false }); stabGeo.rotateX(Math.PI / 2);
  for (const s of [1, -1]) { const w = new THREE.Mesh(stabGeo, body); w.scale.z = s; w.position.y = 0.1; g.add(w); }
  const finShape = new THREE.Shape([[-3.5, 0.3], [-4.9, 0.3], [-5.5, 2.7], [-4.85, 2.7]].map(p => new THREE.Vector2(p[0], p[1])));
  const fin = new THREE.Mesh(new THREE.ExtrudeGeometry(finShape, { depth: 0.08, bevelEnabled: false }), body); fin.position.z = -0.04; g.add(fin);
  // 4 mesin: 1 kiri luar, 2 kiri dalam, 3 kanan dalam, 4 kanan luar (kanan = +z)
  g.userData.engines = [];
  const spans = [-3.9, -2.2, 2.2, 3.9];
  spans.forEach((zs, i) => {
    const xle = 1.0 + (-3.6) * (Math.abs(zs) - 0.4) / 5.8;
    const eg = new THREE.Group(); eg.position.set(xle + 0.05, -0.55, zs); g.add(eg);
    const pod = new THREE.Mesh(new THREE.CylinderGeometry(0.27, 0.22, 1.1, 18), belly); pod.rotation.z = Math.PI / 2; eg.add(pod);
    const pyl = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.3, 0.06), body); pyl.position.set(-0.2, 0.25, 0); eg.add(pyl);
    const intake = new THREE.Mesh(new THREE.CircleGeometry(0.24, 18), std(0x0c1222)); intake.rotation.y = Math.PI / 2; intake.position.x = 0.56; eg.add(intake);
    const ring = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.035, 8, 20), emis(0xffa040, 2.5)); ring.rotation.y = Math.PI / 2; ring.position.x = -0.56; eg.add(ring);
    const jet1 = sprite(0xff9a3c, 1.1, 0.9); jet1.position.x = -0.9; eg.add(jet1);
    const jet2 = sprite(0xffd8a0, 0.55, 1); jet2.position.x = -0.65; eg.add(jet2);
    const elmo = sprite(0x49b4ff, 1.2, 0); elmo.position.x = 0.62; eg.add(elmo);
    g.userData.engines.push({ grp: eg, ring, jet1, jet2, elmo });
  });
  // St. Elmo di tepi depan sayap
  g.userData.elmoWing = [];
  for (const s of [1, -1]) for (let k = 2; k < 7; k++) { const u = k / 6; const sp = sprite(0x5cc0ff, 1.0, 0); sp.position.set(1.0 + (-3.6) * u, -0.14, s * (0.4 + 5.8 * u)); g.add(sp); g.userData.elmoWing.push(sp); }
  const nose = sprite(0x5cc0ff, 1.4, 0); nose.position.set(4.9, 0.3, 0); g.add(nose); g.userData.elmoWing.push(nose);
  const navR = sprite(0xff3030, 0.6, 1); navR.position.set(-3.0, -0.14, -6.2); g.add(navR);
  const navG = sprite(0x30ff70, 0.6, 1); navG.position.set(-3.0, -0.14, 6.2); g.add(navG);
  const strobe = sprite(0xffffff, 1.2, 0); strobe.position.set(-5.5, 2.7, 0); g.add(strobe); g.userData.strobe = strobe;
  return g;
}
function setEngines(pl, states, t) { // states[i] 0..1 nyala
  pl.userData.engines.forEach((e, i) => { const s = states[i]; const fl = 0.85 + 0.15 * noise1(t * 18 + i * 7);
    e.jet1.material.opacity = 0.85 * s * fl; e.jet2.material.opacity = s * fl; e.ring.material.emissiveIntensity = 0.1 + 2.6 * s; e.jet1.scale.setScalar(0.4 + 0.8 * s); });
}
function setElmo(pl, k, t) {
  pl.userData.elmoWing.forEach((sp, i) => { const f = noise1(t * 9 + i * 3.1); sp.material.opacity = k * (0.25 + 0.75 * f); sp.scale.setScalar((0.8 + 1.0 * f) * (i === pl.userData.elmoWing.length - 1 ? 1.6 : 1)); });
  pl.userData.engines.forEach((e, i) => { const f = noise1(t * 11 + i * 5); e.elmo.material.opacity = k * (0.3 + 0.7 * f); e.elmo.scale.setScalar(0.8 + 0.8 * f); });
}

// ---------- LANGIT MALAM (eksterior) ----------
function skyDome(top = 0x030820, mid = 0x10245a, bot = 0x1d3a78) {
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, uniforms: { a: { value: new THREE.Color(top) }, b: { value: new THREE.Color(mid) }, c: { value: new THREE.Color(bot) } },
    vertexShader: 'varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'uniform vec3 a,b,c; varying vec3 vp; void main(){ float h=vp.y; vec3 col = h>0.05? mix(b,a,clamp((h-0.05)/0.5,0.,1.)) : mix(c,b,clamp((h+0.15)/0.2,0.,1.)); gl_FragColor=vec4(col,1.); }' });
  const s = new THREE.Mesh(new THREE.SphereGeometry(900, 32, 16), m); s.frustumCulled = false; return s;
}
function stars(n, seed) { const R = mulberry(seed); const p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const th = R() * Math.PI * 2, ph = 0.08 + R() * 1.2; p[i * 3] = Math.cos(th) * Math.cos(ph) * 800; p[i * 3 + 1] = Math.sin(ph) * 800; p[i * 3 + 2] = Math.sin(th) * Math.cos(ph) * 800; }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); return new THREE.Points(g, new THREE.PointsMaterial({ color: 0xcfdcff, size: 2.2, sizeAttenuation: false, transparent: true, opacity: 0.8, fog: false })); }

const ext = new THREE.Scene(); ext.fog = new THREE.FogExp2(0x10204a, 0.0045);
{
  ext.add(skyDome()); ext.add(stars(500, 9));
  const deck = new THREE.Mesh(new THREE.PlaneGeometry(3000, 3000), new THREE.MeshStandardMaterial({ map: cloudTex, color: 0x9fb4e6, roughness: 1 })); deck.rotation.x = -Math.PI / 2; deck.position.y = -30; ext.add(deck); ext.userData.deck = deck;
  const R = mulberry(4); const puffM = std(0x3b5590, { roughness: 1, flatShading: true });
  for (let i = 0; i < 90; i++) { const p = new THREE.Mesh(new THREE.IcosahedronGeometry(1, 1), puffM); p.scale.set(8 + R() * 14, 2 + R() * 3, 6 + R() * 10); p.position.set(R() * 400 - 200, -29 + R() * 2, R() * 400 - 300); ext.add(p); }
  const mtM = std(0x0d1836, { roughness: 1, flatShading: true }); ext.userData.mts = [];
  for (let i = 0; i < 9; i++) { const h = 18 + R() * 14; const m = new THREE.Mesh(new THREE.ConeGeometry(14 + R() * 10, h, 7), mtM); m.position.set(150 + R() * 140, -30 + h / 2 - 4, -60 + i * 16 + R() * 8); ext.add(m); ext.userData.mts.push(m); }
  const moon = sprite(0x9fc0ff, 160, 0.35); moon.position.set(-300, 220, -500); moon.material.fog = false; ext.add(moon);
  ext.add(new THREE.HemisphereLight(0x5a78c8, 0x0a1430, 1.1));
  const dl = new THREE.DirectionalLight(0xbcd0ff, 1.1); dl.position.set(-3, 6, -4); ext.add(dl);
  const pl = makePlane(); ext.add(pl); ext.userData.plane = pl;
  const elmoL = new THREE.PointLight(0x49b4ff, 0, 14, 1.2); elmoL.position.set(-1, 0.6, 3); pl.add(elmoL); ext.userData.elmoL = elmoL;
}

// ---------- KOKPIT ----------
const cock = new THREE.Scene(); cock.background = new THREE.Color(0x03060f); cock.fog = new THREE.Fog(0x03060f, 4, 14);
{
  const winTex = canvasTex(512, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#040a24'); gr.addColorStop(1, '#173270'); g.fillStyle = gr; g.fillRect(0, 0, w, h); const R = mulberry(8); for (let i = 0; i < 60; i++) { g.fillStyle = `rgba(255,255,255,${R() * .7})`; g.fillRect(R() * w, R() * h * .6, 1.5, 1.5); } });
  const wm = new THREE.MeshStandardMaterial({ map: winTex, emissiveMap: winTex, emissive: 0xffffff, emissiveIntensity: 0.9 });
  for (const s of [-1, 1]) { const win = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 0.8), wm); win.position.set(s * 0.8, 1.55, -1.9); win.rotation.y = -s * 0.25; cock.add(win); }
  const frameM = std(0x1b2235, { roughness: 0.9 });
  const post = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.9, 0.08), frameM); post.position.set(0, 1.55, -1.95); cock.add(post);
  const roof = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.2, 2.5), frameM); roof.position.set(0, 2.05, -0.8); cock.add(roof);
  const panel = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.55, 0.9), std(0x151c2e)); panel.position.set(0, 0.85, -1.55); panel.rotation.x = -0.35; cock.add(panel);
  const R = mulberry(12); cock.userData.screens = [];
  for (let i = 0; i < 6; i++) { const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.34, 0.26), emis([0x12C2B0, 0x2ea0ff, 0xffa040][i % 3], 1.4)); scr.position.set(-1.25 + i * 0.5, 0.99, -1.18); scr.rotation.x = -0.35; cock.add(scr); cock.userData.screens.push(scr); }
  for (let i = 0; i < 0; i++) { const b = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.02, 0.04), emis([0xff4030, 0x30ff80, 0xffb800][Math.floor(R() * 3)], 2)); b.position.set(-1.4 + R() * 2.8, 1.92, -0.5 - R() * 1.2); cock.add(b); }
  const seat = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.3, 0.25), std(0x2a2f3e)); seat.position.set(-0.55, 0.5, 0.45); cock.add(seat);
  // kapten (tokoh mainan, tanpa wajah nyata)
  const cap = new THREE.Group(); cap.position.set(-0.55, 0.75, 0.05); cock.add(cap); cock.userData.capt = cap;
  const shirt = std(0xe9edf3, { roughness: 0.55 });
  const tb = new THREE.Mesh(new THREE.CapsuleGeometry(0.33, 0.35, 6, 14), shirt); tb.position.y = 0.05; cap.add(tb);
  for (const s of [-1, 1]) { const ep = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.03, 0.08), std(0xd9a52c, { metalness: 0.6, roughness: 0.35 })); ep.position.set(s * 0.28, 0.35, 0); ep.rotation.z = s * -0.3; cap.add(ep); }
  const hd = new THREE.Mesh(new THREE.IcosahedronGeometry(0.3, 4), std(0xf0dcc6, { roughness: 0.5 })); hd.position.y = 0.72; cap.add(hd);
  const hatTop = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.3, 0.16, 24), std(0x101a3e)); hatTop.position.y = 0.96; cap.add(hatTop);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(0.305, 0.305, 0.05, 24), std(0xd9a52c, { metalness: 0.7, roughness: 0.3 })); band.position.y = 0.9; cap.add(band);
  const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.025, 20, 1, false, 0, Math.PI), std(0x0a0f24)); brim.position.set(0, 0.88, -0.22); brim.rotation.y = Math.PI / 2; brim.scale.set(1, 1, 0.9); cap.add(brim);
  const arm = new THREE.Group(); arm.position.set(0.3, 0.3, 0); cap.add(arm); cock.userData.captArm = arm;
  const ua = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.38, 4, 10), shirt); ua.position.y = -0.2; arm.add(ua);
  const hand = new THREE.Mesh(new THREE.SphereGeometry(0.1, 12, 8), std(0xf0dcc6)); hand.position.y = -0.45; arm.add(hand);
  const mic = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.16, 0.06), std(0x111111)); mic.position.y = -0.55; arm.add(mic);
  arm.rotation.set(2.2, 0, -0.35);
  cock.add(new THREE.HemisphereLight(0x5a6fb0, 0x0a0a14, 0.5));
  const amber = new THREE.PointLight(0xff9a40, 3, 5, 1.5); amber.position.set(0, 1.1, -0.8); cock.add(amber); cock.userData.amber = amber;
  const blue = new THREE.PointLight(0x49a0ff, 4, 6, 1.2); blue.position.set(0, 1.6, -1.6); cock.add(blue); cock.userData.blue = blue;
  const back = new THREE.DirectionalLight(0x8aa0ff, 1.6); back.position.set(1, 2, 3); cock.add(back); const kp = new THREE.PointLight(0xffe0c0, 3, 4, 1.2); kp.position.set(0.4, 1.9, 0.9); cock.add(kp);
  cock.userData.elmo = [];
  for (let i = 0; i < 10; i++) { const sp = sprite(0x5cc0ff, 0.3, 0); sp.position.set(-1.4 + i * 0.31, 1.2 + (i % 3) * 0.25, -1.85); cock.add(sp); cock.userData.elmo.push(sp); }
}

// ---------- PETA JAWA ----------
const MAP = { lon0: 104.2, lon1: 111.7, lat0: -4.6, w: 12, h: 18 };
MAP.lat1 = MAP.lat0 - (MAP.lon1 - MAP.lon0) * 1.5;
const m2x = lon => (lon - MAP.lon0) / (MAP.lon1 - MAP.lon0) * MAP.w - MAP.w / 2;
const m2z = lat => (MAP.lat0 - lat) / (MAP.lat0 - MAP.lat1) * MAP.h - MAP.h / 2;
const JAVA = [[105.2, -6.8], [105.8, -6.0], [106.4, -6.0], [106.8, -6.08], [107.3, -5.95], [107.9, -6.2], [108.4, -6.4], [108.6, -6.7], [109.2, -6.85], [110.0, -6.9], [110.4, -6.95], [110.9, -6.4], [111.5, -6.6], [112.1, -6.9], [112.7, -6.9], [112.7, -8.3], [111.5, -8.25], [110.5, -8.1], [109.5, -7.75], [108.7, -7.7], [108.0, -7.75], [107.4, -7.5], [106.5, -7.4], [106.0, -7.0], [105.4, -6.85]];
const PLANE_LL = [107.1, -9.3], HALIM = [106.89, -6.27], GAL = [108.05, -7.25], SEA = [105.9, -11.2];
const mapCanvas = document.createElement('canvas'); mapCanvas.width = 1024; mapCanvas.height = 1536; const mgBase = mapCanvas.getContext('2d');
const layerC = document.createElement('canvas'); layerC.width = 1024; layerC.height = 1536; const mg = layerC.getContext('2d');
const mapTex = new THREE.CanvasTexture(mapCanvas); mapTex.colorSpace = THREE.SRGBColorSpace; mapTex.anisotropy = 4;
const px = lon => (lon - MAP.lon0) / (MAP.lon1 - MAP.lon0) * 1024, py = lat => (MAP.lat0 - lat) / (MAP.lat0 - MAP.lat1) * 1536;
function route1(u) { const a = PLANE_LL, b = HALIM; const c = [107.4, -7.6]; const v = 1 - u; return [v * v * a[0] + 2 * v * u * c[0] + u * u * b[0], v * v * a[1] + 2 * v * u * c[1] + u * u * b[1]]; }
function route2(u) { const a = PLANE_LL, b = SEA; const c = [107.6, -11.4]; const v = 1 - u; return [v * v * a[0] + 2 * v * u * c[0] + u * u * b[0], v * v * a[1] + 2 * v * u * c[1] + u * u * b[1]]; }
function drawMap(p1, p2, t) {
  const b0 = mgBase; const gr = b0.createLinearGradient(0, 0, 0, 1536); gr.addColorStop(0, '#0a1a44'); gr.addColorStop(1, '#040b22'); b0.fillStyle = gr; b0.fillRect(0, 0, 1024, 1536);
  const g = mg; g.clearRect(0, 0, 1024, 1536);
  b0.strokeStyle = 'rgba(90,140,220,.12)'; b0.lineWidth = 2; for (let i = 0; i <= 1024; i += 64) { b0.beginPath(); b0.moveTo(i, 0); b0.lineTo(i, 1536); b0.stroke(); } for (let j = 0; j <= 1536; j += 64) { b0.beginPath(); b0.moveTo(0, j); b0.lineTo(1024, j); b0.stroke(); }
  g.beginPath(); JAVA.forEach(([lo, la], i) => i ? g.lineTo(px(lo), py(la)) : g.moveTo(px(lo), py(la))); g.closePath();
  g.fillStyle = '#123a5e'; g.fill(); g.shadowColor = CTEAL; g.shadowBlur = 24; g.strokeStyle = CTEAL; g.lineWidth = 5; g.stroke(); g.shadowBlur = 0;
  // garis pegunungan
  g.setLineDash([10, 10]); g.strokeStyle = 'rgba(230,240,255,.55)'; g.lineWidth = 4; g.beginPath(); [[106.0, -6.7], [106.75, -6.72], [107.0, -6.85], [107.6, -7.2], [108.05, -7.25], [108.6, -7.1], [109.2, -7.25], [110.0, -7.4], [110.5, -7.5]].forEach(([lo, la], i) => i ? g.lineTo(px(lo), py(la)) : g.moveTo(px(lo), py(la))); g.stroke(); g.setLineDash([]);
  g.font = '36px PB'; g.textAlign = 'center';
  g.fillStyle = 'rgba(180,205,255,.55)'; g.fillText('LAUT JAWA', px(107.6), py(-5.3)); g.font = '36px PB'; g.fillText('SAMUDRA HINDIA', px(107.3), py(-12.3));
  g.font = '28px PB'; g.fillStyle = 'rgba(220,235,255,.8)'; g.fillText('PEGUNUNGAN JAWA', px(107.9), py(-6.62));
  // rute
  const drawRoute = (f, p, col) => { if (p <= 0) return; g.setLineDash([16, 14]); g.lineDashOffset = -t * 40; g.strokeStyle = col; g.lineWidth = 7; g.shadowColor = col; g.shadowBlur = 14; g.beginPath(); for (let k = 0; k <= 60 * p; k++) { const [lo, la] = f(k / 60); k ? g.lineTo(px(lo), py(la)) : g.moveTo(px(lo), py(la)); } g.stroke(); g.setLineDash([]); g.shadowBlur = 0; };
  drawRoute(route1, p1, '#ffffff'); drawRoute(route2, p2, '#7fb8ff');
  // titik
  const dot = (ll, col, r, lab, dy) => { g.shadowColor = col; g.shadowBlur = 26; g.fillStyle = col; g.beginPath(); g.arc(px(ll[0]), py(ll[1]), r, 0, 7); g.fill(); g.shadowBlur = 0; g.strokeStyle = col; g.lineWidth = 3; g.beginPath(); g.arc(px(ll[0]), py(ll[1]), r + 8 + 6 * Math.sin(t * 4), 0, 7); g.stroke(); g.font = '36px PB'; g.fillStyle = '#fff'; g.fillText(lab, px(ll[0]), py(ll[1]) + dy); };
  dot(HALIM, CTEAL, 13, 'JAKARTA (HALIM)', -30); dot(GAL, '#ff4b3a', 13, 'GALUNGGUNG', 50);
  // pesawat
  g.save(); g.translate(px(PLANE_LL[0]), py(PLANE_LL[1])); g.fillStyle = '#fff'; g.shadowColor = '#fff'; g.shadowBlur = 16; g.beginPath(); g.moveTo(0, -26); g.lineTo(6, -6); g.lineTo(26, 6); g.lineTo(6, 4); g.lineTo(4, 18); g.lineTo(11, 24); g.lineTo(-11, 24); g.lineTo(-4, 18); g.lineTo(-6, 4); g.lineTo(-26, 6); g.lineTo(-6, -6); g.closePath(); g.fill(); g.restore();
  g.globalCompositeOperation = 'destination-in'; const fm = g.createLinearGradient(px(109.0), 0, px(109.8), 0); fm.addColorStop(0, 'rgba(0,0,0,1)'); fm.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = fm; g.fillRect(0, 0, 1024, 1536); g.globalCompositeOperation = 'source-over';
  b0.drawImage(layerC, 0, 0);
  mapTex.needsUpdate = true;
}
const mapS = new THREE.Scene(); mapS.background = new THREE.Color(0x030716); mapS.fog = new THREE.Fog(0x030716, 14, 34);
{
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(MAP.w, MAP.h), new THREE.MeshBasicMaterial({ map: mapTex })); plane.rotation.x = -Math.PI / 2; mapS.add(plane);
  const mtM = std(0x1f5a78, { flatShading: true, roughness: 0.8 }); const R = mulberry(31);
  [[106.73, -6.72, .5], [106.98, -6.78, .55], [107.73, -7.32, .45], [108.4, -6.89, .55], [109.2, -7.24, .6], [107.6, -7.05, .35], [106.3, -6.85, .35]].forEach(([lo, la, h]) => { const m = new THREE.Mesh(new THREE.ConeGeometry(h * 0.7, h, 6), mtM); m.position.set(m2x(lo), h / 2, m2z(la)); m.rotation.y = R() * 3; mapS.add(m); });
  const gal = new THREE.Mesh(new THREE.ConeGeometry(0.45, 0.6, 7), std(0x8a2a22, { flatShading: true, emissive: 0x501010 })); gal.position.set(m2x(GAL[0]), 0.3, m2z(GAL[1])); mapS.add(gal);
  const ash = sprite(0x6a6f7a, 1.6, 0.0); ash.material.blending = THREE.NormalBlending; ash.position.set(m2x(GAL[0]), 1.0, m2z(GAL[1])); mapS.add(ash);
  mapS.add(new THREE.HemisphereLight(0x8fb0ff, 0x081020, 1.4)); const d = new THREE.DirectionalLight(0xffffff, 1.2); d.position.set(-2, 6, 4); mapS.add(d);
}

// ---------- LANDASAN (POV kokpit) ----------
const rw = new THREE.Scene(); rw.fog = new THREE.FogExp2(0x0a1430, 0.0025);
{
  rw.add(skyDome(0x050b26, 0x15285c, 0x2a3f74));
  const gnd = new THREE.Mesh(new THREE.PlaneGeometry(2000, 2000), std(0x070c18, { roughness: 1 })); gnd.rotation.x = -Math.PI / 2; rw.add(gnd);
  const strip = new THREE.Mesh(new THREE.PlaneGeometry(9, 900), std(0x1a1f2c, { roughness: 1 })); strip.rotation.x = -Math.PI / 2; strip.position.set(0, 0.02, -450); rw.add(strip);
  for (let i = 0; i < 40; i++) { const c = new THREE.Mesh(new THREE.PlaneGeometry(0.35, 6), emis(0xdfe6f2, 0.5)); c.rotation.x = -Math.PI / 2; c.position.set(0, 0.03, -10 - i * 22); rw.add(c); }
  const N = 120, pts = new Float32Array(N * 2 * 3), cols = [];
  for (let i = 0; i < N; i++) for (const s of [-1, 1]) { const k = i * 2 + (s > 0 ? 1 : 0); pts[k * 3] = s * 4.8; pts[k * 3 + 1] = 0.15; pts[k * 3 + 2] = 30 - i * 8; }
  const lg = new THREE.BufferGeometry(); lg.setAttribute('position', new THREE.BufferAttribute(pts, 3));
  rw.add(new THREE.Points(lg, new THREE.PointsMaterial({ map: softTex, color: 0xffd27a, size: 3.2, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })));
  const R = mulberry(41), C = 1400, cp = new Float32Array(C * 3); for (let i = 0; i < C; i++) { cp[i * 3] = (R() - 0.5) * 900; cp[i * 3 + 1] = 0.2; cp[i * 3 + 2] = -R() * 900 - 20; if (Math.abs(cp[i * 3]) < 25) cp[i * 3] += 60 * Math.sign(cp[i * 3] || 1); }
  const cg = new THREE.BufferGeometry(); cg.setAttribute('position', new THREE.BufferAttribute(cp, 3));
  rw.add(new THREE.Points(cg, new THREE.PointsMaterial({ map: softTex, color: 0xffb860, size: 4.0, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false })));
  rw.add(new THREE.HemisphereLight(0x4060a0, 0x050810, 0.6));
}

// ---------- GUNUNG GALUNGGUNG ----------
const vol = new THREE.Scene(); vol.fog = new THREE.FogExp2(0x0d1838, 0.006);
{
  vol.add(skyDome(0x030820, 0x13285e, 0x24407a)); vol.add(stars(400, 17));
  const tg = new THREE.PlaneGeometry(800, 800, 60, 60); const p = tg.attributes.position; const R = mulberry(51);
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), y = p.getY(i); p.setZ(i, 4 * noise1(x * 0.05 + 3) * noise1(y * 0.05 + 7) + 2 * R()); } tg.computeVertexNormals();
  const terr = new THREE.Mesh(tg, std(0x0e1d33, { flatShading: true, roughness: 1 })); terr.rotation.x = -Math.PI / 2; vol.add(terr);
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(5, 34, 26, 11, 3), std(0x1b2438, { flatShading: true, roughness: 1 })); cone.position.set(0, 13, -60); vol.add(cone);
  const lava = sprite(0xff5a20, 16, 0.85); lava.position.set(0, 27, -60); vol.add(lava); vol.userData.lava = lava;
  const mtM = std(0x111b30, { flatShading: true, roughness: 1 });
  [[-70, -110, 30], [80, -130, 36], [-130, -170, 26], [140, -90, 22]].forEach(([x, z, h]) => { const m = new THREE.Mesh(new THREE.ConeGeometry(h * 1.3, h, 8), mtM); m.position.set(x, h / 2, z); vol.add(m); });
  const N = 520, pos = new Float32Array(N * 3), seeds = []; const R2 = mulberry(61); for (let i = 0; i < N; i++) seeds.push([R2(), R2(), R2(), R2()]);
  const ag = new THREE.BufferGeometry(); ag.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const ash = new THREE.Points(ag, new THREE.PointsMaterial({ map: smokeTex, color: 0x545b6a, size: 34, transparent: true, opacity: 0.85, depthWrite: false })); ash.frustumCulled = false; vol.add(ash); vol.userData.ash = { pos, seeds, pts: ash };
  vol.add(new THREE.HemisphereLight(0x5a78c8, 0x0a1430, 0.9)); const dl = new THREE.DirectionalLight(0xbcd0ff, 1.4); dl.position.set(-3, 6, 4); vol.add(dl);
  const lit = new THREE.PointLight(0xbfe0ff, 0, 160, 1); lit.position.set(10, 60, -60); vol.add(lit); vol.userData.lit = lit;
  const red = new THREE.PointLight(0xff5a20, 30, 80, 1.2); red.position.set(0, 32, -60); vol.add(red);
  const sp = makePlane(); sp.scale.setScalar(1.4); vol.add(sp); vol.userData.plane = sp;
}

// ---------- kamera ----------
const cam = new THREE.PerspectiveCamera(40, W / H, 0.05, 2500);
function look(p, tg, fov = 40, roll = 0) { cam.position.set(...p); cam.up.set(Math.sin(roll), Math.cos(roll), 0); cam.lookAt(...tg); cam.fov = fov; cam.updateProjectionMatrix(); }
const V = (a, b, u) => a.map((x, i) => lerp(x, b[i], u));
const proj = (obj, v) => { const p = v.clone(); if (obj) obj.localToWorld(p); p.project(cam); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; };
const shake = (t, k) => [k * (noise1(t * 7) - 0.5), k * (noise1(t * 6 + 30) - 0.5), 0];

// ---------- 2D overlay ----------
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function textW(s, f) { ctx.font = f; return ctx.measureText(s).width; }
function subtitle(t) {
  if (t >= CLOSE) return;
  let c = null; for (const k of CH) if (t >= k.s && t < Math.min(k.show_end, CLOSE)) c = k; if (!c) return;
  const a = (c.s === 0 ? 1 : ramp(t, c.s, 0.08)) * (1 - ramp(t, Math.min(c.show_end, CLOSE) - 0.06, 0.06));
  let fs = 54; const txt = c.text, kw = c.kw; let i = kw ? txt.indexOf(kw) : -1;
  const parts = i < 0 ? [[txt, 0]] : [[txt.slice(0, i), 0], [kw, 1], [txt.slice(i + kw.length), 0]];
  let tw; do { ctx.font = `${fs}px PB`; tw = parts.reduce((s, [p, k]) => s + ctx.measureText(p).width + (k ? 28 : 0), 0); if (tw > 800) fs -= 2; } while (tw > 800 && fs > 36);
  let x = W / 2 - tw / 2; const y = 1475; const pop = c.s === 0 ? 1 : 1 + 0.06 * (1 - easeOut((t - c.s) / 0.15));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, y); ctx.scale(pop, pop); ctx.translate(-W / 2, -y); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  for (const [p, k] of parts) { const w = ctx.measureText(p).width;
    if (k) { ctx.fillStyle = CYEL; rr(x, y - fs * 0.68, w + 28, fs * 1.32, 12); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(p, x + 14, y + 2); x += w + 28; }
    else { ctx.shadowColor = 'rgba(0,0,0,.85)'; ctx.shadowBlur = 14; ctx.fillStyle = '#fff'; ctx.fillText(p, x, y + 2); ctx.shadowBlur = 0; x += w; } }
  ctx.restore();
}
function source(t, a, b, s) { if (t < a || t >= b) return; const al = ramp(t, a, 0.25) * (1 - ramp(t, b - 0.2, 0.2)); ctx.save(); ctx.globalAlpha = al * 0.85; ctx.font = '27px PM'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillStyle = '#dfe6f5'; ctx.fillText('Sumber: ' + s, W / 2, 1640); ctx.restore(); }
function smallText(t, a, b, s, y, f = '30px PM', col = '#e8eefc') { if (t < a || t >= b) return; const al = ramp(t, a, 0.3) * (1 - ramp(t, b - 0.25, 0.25)); ctx.save(); ctx.globalAlpha = al; ctx.font = f; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 10; ctx.fillStyle = col; ctx.fillText(s, W / 2, y); ctx.restore(); }
function pill(t) { // judul layar frame 0
  if (t > 3.6) return; const a = 1 - ramp(t, 3.25, 0.35);
  ctx.save(); ctx.globalAlpha = a; ctx.font = '54px PB'; const s1 = 'Kenapa radar bisa ', s2 = 'BUTA', s3 = '?';
  const w = ctx.measureText(s1 + s2 + s3).width; const x0 = W / 2 - w / 2 - 36, y0 = 292, h = 108;
  ctx.fillStyle = 'rgba(10,18,52,.82)'; rr(x0, y0, w + 72, h, 54); ctx.fill(); ctx.strokeStyle = 'rgba(18,194,176,.9)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; let x = x0 + 36; const y = y0 + h / 2 + 4;
  ctx.fillStyle = '#fff'; ctx.fillText(s1, x, y); x += ctx.measureText(s1).width; ctx.fillStyle = CYEL; ctx.fillText(s2, x, y); x += ctx.measureText(s2).width; ctx.fillStyle = '#fff'; ctx.fillText(s3, x, y);
  ctx.restore();
}
function hudBox(x, y, w, h, a, border = 'rgba(120,170,255,.55)') { ctx.globalAlpha = a; ctx.fillStyle = 'rgba(6,12,34,.78)'; rr(x, y, w, h, 16); ctx.fill(); ctx.strokeStyle = border; ctx.lineWidth = 2.5; ctx.stroke(); }
function clockAlt(t, alt, red = false, a = 1) { // jam kiri atas + mini altimeter kanan atas
  ctx.save(); const pa = a;
  hudBox(140, 150, 300, 112, pa); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  ctx.font = '22px PM'; ctx.fillStyle = 'rgba(200,215,255,.8)'; ctx.fillText('24 JUNI 1982', 164, 180);
  const colon = (Math.floor(t * 2) % 2 === 0) ? '.' : ' '; ctx.font = '46px PB'; ctx.fillStyle = '#fff'; ctx.fillText('20' + colon + '40', 164, 228);
  ctx.font = '28px PB'; ctx.fillStyle = CTEAL; ctx.fillText('WIB', 300, 230);
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(410, 226, 16, 0, 7); ctx.strokeStyle = '#fff'; ctx.lineWidth = 3; ctx.stroke(); const an = t * Math.PI * 2 / 1; ctx.beginPath(); ctx.moveTo(410, 226); ctx.lineTo(410 + 12 * Math.sin(an), 226 - 12 * Math.cos(an)); ctx.stroke();
  hudBox(640, 150, 300, 112, pa, red ? 'rgba(255,80,60,.9)' : 'rgba(120,170,255,.55)');
  ctx.font = '22px PM'; ctx.fillStyle = red ? '#ff8a7a' : 'rgba(200,215,255,.8)'; ctx.fillText('KETINGGIAN', 664, 180);
  ctx.font = '46px PB'; ctx.fillStyle = red ? '#ff5a48' : '#fff'; ctx.fillText(fmt(alt), 664, 228); ctx.font = '26px PB'; ctx.fillStyle = red ? '#ff8a7a' : CTEAL; ctx.fillText('kaki', 664 + textW(fmt(alt), '46px PB') + 12, 232);
  // tape kecil
  ctx.save(); rr(905, 160, 24, 92, 6); ctx.clip(); ctx.strokeStyle = 'rgba(200,215,255,.7)'; ctx.lineWidth = 2; const off = (alt / 20) % 12; for (let k = -2; k < 10; k++) { const yy = 160 + k * 12 + off; ctx.beginPath(); ctx.moveTo(908, yy); ctx.lineTo(k % 2 ? 918 : 926, yy); ctx.stroke(); } ctx.restore();
  ctx.restore();
}
function bigAlt(t, alt, opts = {}) { // altimeter besar
  const a = opts.a ?? 1; ctx.save(); ctx.globalAlpha = a; if (opts.sc) { ctx.translate(W / 2, opts.y0); ctx.scale(opts.sc, opts.sc); ctx.translate(-W / 2, -520); } const x = 260, y = 520, w = 560, h = 520;
  ctx.fillStyle = 'rgba(8,10,26,.78)'; rr(x, y, w, h, 28); ctx.fill(); ctx.strokeStyle = opts.red ? 'rgba(255,70,50,.95)' : 'rgba(120,170,255,.6)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '30px PB'; ctx.fillStyle = opts.red ? '#ff7a68' : '#cfe0ff'; ctx.fillText('KETINGGIAN', x + w / 2, y + 58);
  // tape
  const tx = x + 40, tw = 150, ty = y + 100, th = 380; ctx.save(); rr(tx, ty, tw, th, 14); ctx.clip(); ctx.fillStyle = 'rgba(255,255,255,.05)'; ctx.fillRect(tx, ty, tw, th);
  const pxPerFt = th / 6000; ctx.font = '22px PM'; ctx.textAlign = 'left';
  for (let f = Math.floor((alt - 4000) / 500) * 500; f < alt + 4000; f += 500) { const yy = ty + th / 2 - (f - alt) * pxPerFt; ctx.strokeStyle = 'rgba(220,230,255,.6)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(tx, yy); ctx.lineTo(tx + (f % 1000 ? 22 : 40), yy); ctx.stroke(); if (f % 1000 === 0 && f >= 0) { ctx.fillStyle = 'rgba(220,230,255,.75)'; ctx.fillText(fmt(f), tx + 50, yy); } }
  if (opts.limit) { const yy = ty + th / 2 - (opts.limit - alt) * pxPerFt; ctx.fillStyle = 'rgba(255,50,40,.28)'; ctx.fillRect(tx, yy, tw, th); ctx.strokeStyle = '#ff3b2f'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(tx, yy); ctx.lineTo(tx + tw, yy); ctx.stroke(); }
  ctx.restore();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.moveTo(tx + tw + 4, ty + th / 2); ctx.lineTo(tx + tw + 24, ty + th / 2 - 14); ctx.lineTo(tx + tw + 24, ty + th / 2 + 14); ctx.fill();
  ctx.textAlign = 'center'; ctx.font = '84px PB'; ctx.fillStyle = opts.red ? '#ff4a38' : '#fff'; ctx.shadowColor = opts.red ? '#ff2010' : '#4080ff'; ctx.shadowBlur = 22; ctx.fillText(fmt(alt), x + 370, y + 260); ctx.shadowBlur = 0;
  ctx.font = '34px PB'; ctx.fillStyle = opts.red ? '#ff8a7a' : CTEAL; ctx.fillText('kaki', x + 370, y + 330);
  if (opts.vs) { ctx.font = '26px PM'; ctx.fillStyle = '#cfe0ff'; ctx.fillText(opts.vs, x + 370, y + 390); }
  if (opts.limit && opts.limitA) { ctx.globalAlpha = a * opts.limitA; ctx.fillStyle = '#ff3b2f'; rr(x + 230, y + 420, 290, 60, 14); ctx.fill(); ctx.fillStyle = '#fff'; ctx.font = '28px PB'; ctx.fillText('BATAS ' + fmt(opts.limit), x + 375, y + 452); }
  ctx.restore();
}
function engineIcons(t, st, a = 1, y = 160) {
  ctx.save(); ctx.globalAlpha = a; const w = 600, x = W / 2 - w / 2; ctx.fillStyle = 'rgba(6,12,34,.8)'; rr(x, y, w, 120, 20); ctx.fill(); ctx.strokeStyle = 'rgba(120,170,255,.5)'; ctx.lineWidth = 2.5; ctx.stroke();
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '22px PM'; ctx.fillStyle = '#cfe0ff'; ctx.fillText('MESIN', W / 2, y + 26);
  for (let i = 0; i < 4; i++) { const cx = x + 90 + i * 140, cy = y + 76; const on = st[i]; const col = on > 0.5 ? '#2ee88a' : '#ff3b2f';
    ctx.shadowColor = col; ctx.shadowBlur = 18; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(cx - 26, cy, 12, 0, 7); ctx.fill(); ctx.shadowBlur = 0; ctx.fillStyle = '#fff'; ctx.font = '30px PB'; ctx.fillText(String(i + 1), cx + 8, cy + 2); }
  ctx.restore();
}
function label(x, y, num, text, col, a = 1, scale = 1) { // kartu pilihan kecil ala referensi
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(scale, scale); ctx.font = '30px PB'; const tw = ctx.measureText(text).width; const w = tw + 92, h = 60;
  ctx.fillStyle = 'rgba(8,12,30,.92)'; rr(-w / 2, -h / 2, w, h, 12); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.55)'; ctx.lineWidth = 2; ctx.stroke();
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(-w / 2 + 34, 0, 18, 0, 7); ctx.fill(); ctx.fillStyle = CNAVY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '26px PB'; ctx.fillText(num, -w / 2 + 34, 2);
  ctx.fillStyle = '#fff'; ctx.font = '30px PB'; ctx.textAlign = 'left'; ctx.fillText(text, -w / 2 + 64, 2); ctx.restore();
}
function radar(t, cx, cy, R, a, ashK = 0, warnK = 0) {
  ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = '#031a12'; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();
  ctx.strokeStyle = 'rgba(60,230,150,.35)'; ctx.lineWidth = 2; for (let k = 1; k <= 4; k++) { ctx.beginPath(); ctx.arc(cx, cy, R * k / 4, 0, 7); ctx.stroke(); }
  ctx.beginPath(); ctx.moveTo(cx - R, cy); ctx.lineTo(cx + R, cy); ctx.moveTo(cx, cy - R); ctx.lineTo(cx, cy + R); ctx.stroke();
  const an = t * 2.2; const gr = ctx.createConicGradient(an - 0.9, cx, cy); gr.addColorStop(0, 'rgba(60,255,160,0)'); gr.addColorStop(0.14, 'rgba(60,255,160,.45)'); gr.addColorStop(0.145, 'rgba(60,255,160,0)'); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.fill();
  ctx.strokeStyle = 'rgba(120,255,190,.9)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + R * Math.cos(an), cy + R * Math.sin(an)); ctx.stroke();
  if (ashK > 0) { ctx.globalAlpha = a * ashK; ctx.setLineDash([12, 10]); ctx.strokeStyle = '#c9ced8'; ctx.lineWidth = 4; ctx.fillStyle = 'rgba(150,155,170,.28)'; ctx.beginPath(); for (let k = 0; k <= 24; k++) { const th = k / 24 * Math.PI * 2; const r = R * 0.33 * (1 + 0.25 * Math.sin(th * 3 + 1)); const xx = cx + R * 0.05 + r * Math.cos(th) * 1.3, yy = cy - R * 0.38 + r * Math.sin(th) * 0.8; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.closePath(); ctx.fill(); ctx.stroke(); ctx.setLineDash([]); }
  if (warnK > 0) { ctx.globalAlpha = a * warnK; ctx.strokeStyle = CYEL; ctx.lineWidth = 6; ctx.setLineDash([]); ctx.beginPath(); for (let k = 0; k <= 24; k++) { const th = k / 24 * Math.PI * 2; const r = R * 0.33 * (1 + 0.25 * Math.sin(th * 3 + 1)); const xx = cx + R * 0.05 + r * Math.cos(th) * 1.3, yy = cy - R * 0.38 + r * Math.sin(th) * 0.8; k ? ctx.lineTo(xx, yy) : ctx.moveTo(xx, yy); } ctx.closePath(); ctx.stroke(); }
  ctx.fillStyle = '#fff'; ctx.globalAlpha = a; ctx.beginPath(); ctx.moveTo(cx, cy - 16); ctx.lineTo(cx + 11, cy + 12); ctx.lineTo(cx - 11, cy + 12); ctx.fill();
  ctx.strokeStyle = 'rgba(60,230,150,.7)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.stroke();
  ctx.restore();
}
function badge(x, y, text, bg, fg, a) { ctx.save(); ctx.globalAlpha = a; ctx.font = '30px PB'; const w = ctx.measureText(text).width + 44; ctx.fillStyle = bg; rr(x - w / 2, y - 30, w, 60, 30); ctx.fill(); ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, x, y + 2); ctx.restore(); }
function follow(t) { if (t < 10 || t >= 15) return; const a = ramp(t, 10, 0.3) * (1 - ramp(t, 14.7, 0.3)); ctx.save(); ctx.globalAlpha = a * 0.9; ctx.font = '23px PM'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillStyle = '#e8eefc'; ctx.fillText('Follow @kabar.arunika untuk cerita kamu-pilih-apa berikutnya', W / 2, 1725); ctx.restore(); }
// kaca buram tergores abu (POV pendaratan)
const frost = document.createElement('canvas'); frost.width = W; frost.height = H; { const g = frost.getContext('2d'); const R = mulberry(77);
  for (let i = 0; i < 9000; i++) { g.fillStyle = `rgba(220,225,235,${R() * 0.09})`; const r = 2 + R() * 9; g.fillRect(R() * W, R() * H, r, r); }
  g.strokeStyle = 'rgba(235,240,250,.16)'; for (let i = 0; i < 700; i++) { g.lineWidth = 0.6 + R() * 1.6; const x = R() * W, y = R() * H, l = 20 + R() * 120, an = -0.4 + R() * 0.8; g.beginPath(); g.moveTo(x, y); g.lineTo(x + l * Math.cos(an), y + l * Math.sin(an)); g.stroke(); } }
function cockpitFrame() { ctx.save(); ctx.fillStyle = '#05070d'; ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.moveTo(70, 380); ctx.lineTo(500, 320); ctx.lineTo(510, 1180); ctx.lineTo(90, 1240); ctx.closePath(); ctx.moveTo(580, 320); ctx.lineTo(1010, 380); ctx.lineTo(990, 1240); ctx.lineTo(570, 1180); ctx.closePath(); ctx.fill('evenodd');
  ctx.fillStyle = '#0b1020'; ctx.fillRect(0, 1260, W, 660); ctx.fillStyle = '#1a2236'; rr(80, 1300, 920, 120, 18); ctx.fill(); for (let i = 0; i < 5; i++) { ctx.fillStyle = ['#0f5f58', '#1a4f9a', '#8a5a18'][i % 3]; rr(120 + i * 175, 1320, 140, 80, 10); ctx.fill(); } ctx.restore(); }

// ---------- frame ----------
function sceneOf(t) { let k = 0; for (let i = 0; i < SC.length; i++) if (t >= SC[i]) k = i; return k; }
const hidden = new Set();
function setVis(o, v) { o.visible = v; }

window.renderFrame = function (t) {
  const k = sceneOf(t); const t0 = SC[k], t1 = k + 1 < SC.length ? SC[k + 1] : TOTAL; const lt = t - t0, u = clamp(lt / (t1 - t0));
  let scene = null; const aru = cabin.userData.aru; const pl = ext.userData.plane;
  // default status Aru
  aru.userData.head.rotation.set(0, 0, 0); setAruFace(aru, 0); aru.userData.arms.forEach((a, i) => { a.rotation.set(-0.9, 0, (i ? 1 : -1) * 0.15); });
  aru.userData.flag.rotation.z = -0.25 + 0.06 * Math.sin(t * 3);
  cabin.userData.smoke.pts.material.opacity = 0; cabin.userData.bigWinMat.emissiveIntensity = 1.0; cabin.userData.winLight.intensity = 6;
  let post = { flash: 0, dark: 0 };
  // jendela berpendar biru (St. Elmo) — kuat dari awal
  const elmoBlink = 0.7 + 0.3 * noise1(t * 8);
  if (k === 0) { // HOOK: Aru di kursi jendela, dolly-in
    scene = cabin; cabin.userData.bigWinMat.emissiveIntensity = 1.4 * elmoBlink + 0.4; cabin.userData.winLight.intensity = 9 * elmoBlink;
    const h = aru.userData.head; const hp = new THREE.Vector3(); h.getWorldPosition(hp);
    if (t < 1.6) { const e = ease(t / 1.6); h.rotation.y = -0.45; look(V([-0.55, 0.62, 0.35], [-0.75, 0.58, 0.5], e).map((x, i) => x + shake(t, 0.01)[i]), [hp.x + 0.05, hp.y - 0.08, hp.z - 0.05], 58); }
    else { const e = ease((t - 1.6) / 3.6); h.rotation.y = lerp(-0.3, 0.55, ease((t - 1.8) / 1.0)); h.rotation.x = -0.05; look(V([-1.0, 0.7, 0.15], [-1.2, 0.66, 0.3], e).map((x, i) => x + shake(t, 0.01)[i]), [-2.3, 0.5, 0.95], 56); }
    if (t > 2.9) setAruFace(aru, 0);
  } else if (k === 1) { // kabin berasap
    scene = cabin; const e = ease(u); look([lerp(0.15, 0.05, e), lerp(-0.6, -0.5, e), lerp(3.6, 1.8, e)], [0, 0.3, -12], 46);
    const sm = cabin.userData.smoke; const fill = ease(lt / 2.5); sm.pts.material.opacity = 0.1 + 0.16 * fill;
    sm.seeds.forEach((s, i) => { const yTop = 3.0 - (2.0 + 2.5 * s[1]) * fill; sm.pos[i * 3] = s[0] + 0.3 * Math.sin(t * 0.5 + i); sm.pos[i * 3 + 1] = yTop + 0.3 * Math.sin(t * 0.7 + i * 2); sm.pos[i * 3 + 2] = s[2] + t * 0.15 * (s[3] - 0.5); });
    sm.pts.geometry.attributes.position.needsUpdate = true; sm.pts.material.color.setHex(0xc4c2b4);
  } else if (k === 2) {
    if (t < cs(6) + 1.0) { // over-shoulder Aru ke jendela berpendar
      scene = cabin; cabin.userData.bigWinMat.emissiveIntensity = 1.5 * elmoBlink + 0.6; cabin.userData.winLight.intensity = 12 * elmoBlink;
      aru.userData.head.rotation.y = 1.0; const e = ease(lt / 1.2); look([lerp(-1.2, -1.35, e), 1.0, lerp(2.5, 2.25, e)], [-2.75, 0.5, 0.8], 50);
      const sm = cabin.userData.smoke; sm.pts.material.opacity = 0.25;
    } else if (t < cs(7) - 0.15) { // luar: sayap & mesin St. Elmo
      scene = ext; const e = ease((t - cs(6) - 1.0) / 1.0); pl.position.set(0, 0, 0); pl.rotation.set(0, 0, 0);
      look([lerp(0.2, 0.5, e), 0.95, 0.75], [-2.0, -0.7, 5.0], 55, 0.04); setEngines(pl, [1, 1, 1, 1], t); setElmo(pl, 0.8, t); ext.userData.elmoL.intensity = 3 * elmoBlink;
    } else { scene = 'radar'; }
  } else if (k === 3) { // mesin padam
    scene = ext; pl.position.set(0, 0, 0); pl.rotation.set(0, 0, 0.0);
    const off = i => (i === 3 ? cs(8) + 0.45 : cs(9) + 0.35 + [0.5, 0.25, 0][i] * 1.0);
    const st = [0, 1, 2, 3].map(i => t < off(i) ? 1 : clamp(1 - (t - off(i)) / 0.25));
    setEngines(pl, st, t); setElmo(pl, 0.55, t); ext.userData.elmoL.intensity = 6 * elmoBlink;
    const e = ease(u); look([lerp(-18, -16, e), lerp(5, 4.2, e), lerp(15, 14, e)], [-0.6, -0.6, 1.4], 44);
    post.st = st.map(s => s > 0.5 ? 1 : 0);
  } else if (k === 4) { // kokpit, kapten bicara
    scene = cock; const e = ease(u); const c = cock.userData.capt; c.rotation.y = 0.15;
    look([lerp(0.95, 0.8, e), lerp(1.65, 1.6, e), lerp(2.6, 2.2, e)], [-0.35, 1.25, -0.9], 52);
    cock.userData.elmo.forEach((sp, i) => { const f = noise1(t * 10 + i * 2); sp.material.opacity = 0.6 * f; sp.scale.setScalar(0.2 + 0.4 * f); });
    cock.userData.blue.intensity = 3 + 3 * elmoBlink; cock.userData.amber.intensity = 2.5;
    cock.userData.screens.forEach((s, i) => s.material.emissiveIntensity = (i % 2 ? 0.6 : 1.3) * (0.8 + 0.2 * noise1(t * 3 + i)));
  } else if (k === 5) { // meluncur turun, pegunungan di depan
    scene = ext; const e = ease(u); pl.position.set(lerp(0, 8, u), lerp(0, -3, u), 0); pl.rotation.set(0, 0, -0.08);
    setEngines(pl, [0, 0, 0, 0], t); setElmo(pl, 0.25, t); ext.userData.elmoL.intensity = 0;
    const p = pl.position; look([p.x + lerp(-16, -13, e), p.y + lerp(6, 5, e), p.z + lerp(6, 4, e)], [p.x + 25, p.y - 7, p.z - 1], 46);
    ext.userData.deck.material.map.offset.x = t * 0.004;
  } else if (k === 6 || k === 7) { // peta
    scene = mapS; const p1 = k === 6 ? ease((t - cs(16)) / 1.6) : 1; const p2 = k === 7 ? ease((t - cs(18)) / 1.8) : 0; drawMap(p1, p2, t);
    const pxp = m2x(PLANE_LL[0]), pzp = m2z(PLANE_LL[1]);
    if (k === 6) { const e = ease(u); const cx = -0.75, cz = pzp - 3.0; look([cx + lerp(-0.2, 0.2, e), lerp(19.0, 18.2, e), cz + lerp(5.6, 5.2, e)], [cx, 0, cz], 50); }
    else { const e = ease(u); const an = lerp(0, -0.12, e); const cx = lerp(-0.75, -1.0, e), cz = pzp - lerp(3.0, 1.2, e); look([cx + 0.2 + Math.sin(an) * 5.2, 18.2, cz + Math.cos(an) * 5.2], [cx, 0, cz], 50); }
    post.map = { k, p1, p2 };
  } else if (k === 8 || k === 9) { // Aru + kartu 1/2
    scene = cabin; const blink = Math.floor((t - SC[8]) / 0.6) % 2; aru.userData.head.rotation.y = k === 8 ? lerp(-0.95, -0.1, ease((t - cs(21) - 0.2) / 1.4)) : -0.5 + 0.35 * Math.sin((t - SC[9]) * 2.2);
    aru.userData.head.rotation.x = -0.05;
    if (k === 9) aru.userData.arms.forEach((a, i) => a.rotation.set(-0.5, 0, (i ? 1 : -1) * 0.5));
    const e = ease((t - SC[8]) / (SC[10] - SC[8]));
    look([lerp(-0.6, -0.8, e), lerp(0.66, 0.62, e), lerp(0.3, 0.45, e)], [-2.0, 0.42, 1.2], 58);
    post.cards = { blink, k };
  } else if (k === 10) { // kokpit, altimeter + batas 12.000
    scene = cock; const e = ease(u); look([lerp(0.3, 0.15, e), lerp(1.45, 1.35, e), lerp(0.6, 0.1, e)], [-0.2, 1.0, -1.3], 40);
    cock.userData.elmo.forEach(sp => sp.material.opacity = 0); cock.userData.blue.intensity = 3; cock.userData.amber.intensity = 0.6;
    post.dark = 0.35;
  } else if (k === 11) { // mesin menyala lagi
    scene = ext; pl.position.set(0, 0, 0); pl.rotation.set(0, 0, 0); setElmo(pl, 0, t); ext.userData.elmoL.intensity = 0;
    const on4 = cs(28); const others = [cs(30) + 0.55, cs(30) + 0.3, cs(30) + 0.05];
    const ig = (a) => t < a ? 0 : clamp((t - a) / 0.5) * (t - a < 0.5 ? 0.6 + 0.4 * noise1(t * 40) : 1);
    const st = [ig(others[0]), ig(others[1]), ig(others[2]), ig(on4)]; setEngines(pl, st, t);
    if (t < cs(30)) { const e = ease((t - SC[11]) / (cs(30) - SC[11])); look([lerp(-4.4, -3.8, e), lerp(-1.0, -0.95, e), lerp(5.9, 5.6, e)], [-1.3, -0.6, 3.9], 44); }
    else { const e = ease((t - cs(30)) / (SC[12] - cs(30))); look([lerp(-13, -15, e), lerp(3.8, 4.5, e), lerp(12, 13, e)], [0, -0.6, 1.0], 44); }
    post.st = st.map((s, i) => (i === 3 ? t >= on4 : s > 0.3) ? 1 : 0); post.flash = t > on4 && t < on4 + 0.2 ? 0.12 * (1 - (t - on4) / 0.2) : 0;
  } else if (k === 12) { // pendaratan Halim + kabin lega
    if (t < cs(32) + 0.2) { scene = rw; const e = ease((t - SC[12]) / (cs(32) + 0.2 - SC[12])); look([0 + shake(t, 0.15)[0], lerp(22, 9, e), lerp(140, 70, e)], [0, 0, lerp(-200, -260, e)], 52); post.landing = true; }
    else { scene = cabin; setAruFace(aru, 1); aru.userData.head.rotation.set(-0.05, -0.5, 0); aru.userData.arms.forEach((a, i) => a.rotation.set(-2.6, 0, (i ? 1 : -1) * 0.35)); const e = ease((t - cs(32) - 0.2) / 1.6); look([lerp(-0.6, -0.8, e), 0.64, lerp(0.35, 0.45, e)], [-2.0, 0.45, 1.2], 58); cabin.userData.bigWinMat.emissiveIntensity = 0.5; cabin.userData.winLight.intensity = 3; }
  } else if (k === 13) { // Galunggung
    scene = vol; const e = ease(u); look([lerp(-30, -18, e), lerp(30, 34, e), lerp(70, 55, e)], [0, 32, -60], 50);
    const ash = vol.userData.ash; ash.seeds.forEach((s, i) => { const age = (s[0] + t * 0.05) % 1; const h = 26 + age * 90; const spread = 4 + age * 55; ash.pos[i * 3] = Math.cos(s[1] * 6.28) * spread * s[2] + age * 30; ash.pos[i * 3 + 1] = h + (s[3] - 0.5) * 10 * age; ash.pos[i * 3 + 2] = -60 + Math.sin(s[1] * 6.28) * spread * s[2]; }); ash.pts.geometry.attributes.position.needsUpdate = true;
    const fl = noise1(t * 6) > 0.82 ? 1 : 0; vol.userData.lit.intensity = 220 * fl; post.flash = 0.05 * fl;
    const sp = vol.userData.plane; sp.position.set(lerp(-60, 40, u), 70, -35); sp.rotation.set(0, 0.25, 0); setEngines(sp, [1, 1, 1, 1], t); setElmo(sp, 0, t);
    vol.userData.lava.material.opacity = 0.7 + 0.3 * noise1(t * 5);
  } else { scene = 'close'; }

  // ---- render 3D ----
  if (scene && typeof scene !== 'string') {
    renderer.render(scene, cam); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.drawImage(glc, 0, 0);
    // bloom murah
    sctx.filter = 'brightness(0.7) contrast(2.2) blur(5px)'; sctx.clearRect(0, 0, 180, 320); sctx.drawImage(glc, 0, 0, 180, 320); sctx.filter = 'none';
    ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.55; ctx.imageSmoothingEnabled = true; ctx.drawImage(small, 0, 0, W, H); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  } else { ctx.fillStyle = '#040817'; ctx.fillRect(0, 0, W, H); }
  if (post.landing) { ctx.globalAlpha = 0.6; ctx.drawImage(frost, 0, 0); ctx.globalAlpha = 0.07; ctx.fillStyle = '#c8d2e6'; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; cockpitFrame(); }
  if (post.dark) { ctx.fillStyle = `rgba(2,4,12,${post.dark})`; ctx.fillRect(0, 0, W, H); }
  // vinyet
  const vg = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.25, W / 2, H * 0.5, H * 0.75); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,8,.72)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  // bayangan bawah agar subtitle terbaca
  const bg = ctx.createLinearGradient(0, 1250, 0, 1920); bg.addColorStop(0, 'rgba(0,0,10,0)'); bg.addColorStop(1, 'rgba(0,0,10,.6)'); ctx.fillStyle = bg; ctx.fillRect(0, 1250, W, 670);

  // ---- grafik per adegan ----
  if (k === 0) { pill(t); if (t >= 2.0) { const a = ramp(t, 2.0, 0.2); const alt = 37000 + 10 * Math.round(3 * Math.sin(t * 3.1) + 2 * Math.sin(t * 7.3)); clockAlt(t, alt, false, a); } source(t, 2.3, SC[1], 'BA Flight 9 · Wikipedia'); }
  if (k === 1) { clockAlt(t, 37000 + 10 * Math.round(3 * Math.sin(t * 3.1)), false, 1 - ramp(t, SC[2] - 0.3, 0.3)); source(t, SC[1] + 0.2, SC[2], '24 Juni 1982 · Wikipedia'); }
  if (scene === 'radar') { const a = ramp(t, cs(7) - 0.15, 0.15); ctx.fillStyle = '#02100b'; ctx.globalAlpha = a; ctx.fillRect(0, 0, W, H); ctx.globalAlpha = 1; radar(t, W / 2, 880, 400, a);
    smallText(t, cs(7) - 0.1, SC[3], 'RADAR CUACA', 400, '34px PB', '#7dffc0'); smallText(t, cs(7) + 0.6, SC[3], 'tidak ada awan terdeteksi', 1340, '30px PM', '#bfffe0'); }
  if (k === 3) { engineIcons(t, post.st, ramp(t, SC[3], 0.2)); }
  if (k === 4) { const a = ramp(t, cs(11), 0.3); if (a > 0) { ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = 'rgba(6,12,34,.85)'; rr(170, 300, 740, 150, 22); ctx.fill(); ctx.strokeStyle = CTEAL; ctx.lineWidth = 3; ctx.stroke(); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '24px PM'; ctx.fillStyle = CTEAL; ctx.fillText('PENGUMUMAN KAPTEN (ASLI)', W / 2, 340); ctx.font = 'italic 38px PB'; ctx.fillStyle = '#fff'; ctx.fillText('“We have a small problem.”', W / 2, 400); ctx.restore(); }
    source(t, SC[4] + 0.3, SC[5], 'Kapten Eric Moody, 24 Jun 1982 · AirlineRatings'); }
  if (k === 5) { const alt = lerp(37000, 20000, ease(u * 1.05)); bigAlt(t, Math.round(alt / 10) * 10, { red: true, a: ramp(t, SC[5] + 0.1, 0.25), vs: 'TANPA MESIN', sc: 0.72, y0: 160 }); source(t, cs(14), SC[6], 'Butuh min. ±11.500 kaki · Wikipedia'); }
  if (post.map) { const m = post.map; const pa = proj(null, new THREE.Vector3(m2x(route1(0.62)[0]), 0.2, m2z(route1(0.62)[1]))); const pb = proj(null, new THREE.Vector3(m2x(route2(0.55)[0]), 0.2, m2z(route2(0.55)[1])));
    const cl = (p, hw) => [clamp(p[0], 150 + hw, 930 - hw), clamp(p[1], 430, 1300)]; const qa = cl([pa[0] - 170, pa[1] - 70], 200), qb = cl([pb[0] + 40, pb[1] + 20], 135);
    if (t >= cs(16)) label(qa[0], qa[1], '1', 'LEWATI GUNUNG', CTEAL, ramp(t, cs(16), 0.25), 1 + 0.15 * (1 - easeOut((t - cs(16)) / 0.3)));
    if (m.k === 7 && t >= cs(18)) label(qb[0], qb[1], '2', 'KE LAUT', CYEL, ramp(t, cs(18), 0.25), 1 + 0.15 * (1 - easeOut((t - cs(18)) / 0.3))); }
  if (post.cards) { const c = post.cards; const hp = new THREE.Vector3(); aru.userData.head.getWorldPosition(hp);
    const l1 = proj(null, hp.clone().add(new THREE.Vector3(0.2, 0.62, -0.3))), l2 = proj(null, hp.clone().add(new THREE.Vector3(0.0, 0.62, 0.7)));
    const a = ramp(t, SC[8], 0.3); const bob = Math.sin(t * 2) * 8;
    label(345, 560 + bob, '1', 'LEWATI GUNUNG', CTEAL, a * (c.blink === 0 ? 1 : 0.45), c.blink === 0 ? 1.12 : 1);
    label(775, 560 - bob, '2', 'KE LAUT', CYEL, a * (c.blink === 1 ? 1 : 0.45), c.blink === 1 ? 1.12 : 1);
    if (c.k === 9) smallText(t, SC[9] + 0.2, SC[10], 'Tulis 1 atau 2 sebelum lihat jawabannya', 1640, '30px PM');
    if (c.k === 9 && t > cs(24) + 1.4) { const p = clamp((t - (cs(24) + 1.4)) / (SC[10] - cs(24) - 1.4)); ctx.save(); ctx.strokeStyle = CYEL; ctx.lineWidth = 8; ctx.beginPath(); ctx.arc(W / 2, 1000, 40, -Math.PI / 2, -Math.PI / 2 + p * Math.PI * 2); ctx.stroke(); ctx.restore(); } }
  if (k === 10) { const alt = Math.round(lerp(16000, 13500, ease(u)) / 10) * 10; bigAlt(t, alt, { red: alt < 14500, a: ramp(t, SC[10], 0.25), limit: 12000, limitA: ramp(t, cs(26), 0.3), vs: 'TANPA MESIN' }); source(t, SC[10] + 0.3, SC[11], 'AirlineRatings · Wikipedia'); }
  if (k === 11) { engineIcons(t, post.st, 1); if (t >= cs(28)) badge(W / 2, 500, 'MESIN MENYALA', CTEAL, CNAVY, ramp(t, cs(28), 0.12)); ctx.save(); const a = 1; hudBox(640, 320, 300, 112, a); ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.font = '22px PM'; ctx.fillStyle = 'rgba(200,215,255,.8)'; ctx.fillText('KETINGGIAN', 664, 350); ctx.font = '46px PB'; ctx.fillStyle = '#fff'; ctx.fillText('13.500', 664, 398); ctx.font = '26px PB'; ctx.fillStyle = CTEAL; ctx.fillText('kaki', 830, 402); ctx.restore();
    source(t, cs(28), SC[12], '±13.500 kaki (±4.100 m) · Guinness World Records'); }
  if (k === 12) { const n = Math.round(263 * easeOut((t - cs(31)) / 1.1)); if (t >= cs(31)) { ctx.save(); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '190px PB'; ctx.fillStyle = CYEL; ctx.shadowColor = 'rgba(255,184,0,.7)'; ctx.shadowBlur = 40; ctx.fillText(String(Math.max(0, n)), W / 2, 330); ctx.shadowBlur = 0; ctx.font = '44px PB'; ctx.fillStyle = '#fff'; ctx.fillText('orang selamat', W / 2, 450); ctx.restore(); }
    source(t, cs(31), SC[13], 'Halim, Jakarta · AirlineRatings'); }
  if (k === 13) { const a = ramp(t, cs(35) - 0.1, 0.3); if (a > 0) { radar(t, W / 2, 760, 250, a, ramp(t, cs(35) + 0.6, 0.4), ramp(t, cs(36), 0.4)); if (t > cs(35) + 0.6) smallText(t, cs(35) + 0.6, CLOSE, t < cs(36) ? 'awan abu: tak terdeteksi' : '', 1060, '30px PB', '#d8dce6');
      if (t > cs(36)) badge(W / 2, 1080, 'PERINGATAN ABU VULKANIK', CYEL, CNAVY, ramp(t, cs(36), 0.3)); }
    source(t, cs(36), CLOSE, 'VAAC (ICAO, 1990-an) · WMO'); }
  if (scene === 'close') { const a = ramp(t, CLOSE, 0.2); ctx.save(); ctx.globalAlpha = a; const lw = 300, lh = lw * logo.height / logo.width; ctx.drawImage(logo, W / 2 - lw / 2, 760, lw, lh);
    ctx.font = '52px PB'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; const s1 = '1 atau 2? Tulis di ', s2 = 'komentar'; const w1 = ctx.measureText(s1).width, w2 = ctx.measureText(s2).width; let x = W / 2 - (w1 + w2 + 28) / 2; ctx.fillStyle = '#fff'; ctx.fillText(s1, x, 1000); x += w1; ctx.fillStyle = CYEL; rr(x, 1000 - 37, w2 + 28, 74, 14); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(s2, x + 14, 1003); ctx.restore(); }
  follow(t);
  subtitle(t);
  // transisi: kedip gelap singkat tiap ganti adegan (bukan di frame 0)
  if (k > 0 && lt < 0.12) { ctx.fillStyle = `rgba(2,4,12,${0.6 * (1 - lt / 0.12)})`; ctx.fillRect(0, 0, W, H); }
  if (post.flash) { ctx.fillStyle = `rgba(200,225,255,${post.flash})`; ctx.fillRect(0, 0, W, H); }
};
window.READY = true;
