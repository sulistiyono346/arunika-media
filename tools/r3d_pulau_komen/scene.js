// Pulau Komen — Hari 2: Kopdes. three.js r160, deterministik: window.renderFrame(t).
import * as THREE from './three.module.js';

const W = 1080, H = 1920;
const T = await (await fetch('timing.json')).json();
const ENV = await (await fetch('env.json')).json();
const CH = T.chunks, P = T.para_start, WD = T.words, TOTAL = T.total, LEAD = T.lead;
const PEND = 454;                      // follower IG per 13 Nov (Metricool IGEV01)

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;
const ease = u => { u = clamp(u); return u * u * (3 - 2 * u); };
const easeOut = u => { u = clamp(u); return 1 - Math.pow(1 - u, 3); };
const back = u => { u = clamp(u); const c = 1.70158; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
const ramp = (t, a, d = 0.35) => ease((t - a) / d);
const pop = (t, a, d = 0.35) => back((t - a) / d);
// waktu kata ke-n yang teksnya mengandung s (setelah waktu min)
const wordT = (s, after = 0) => { const w = WD.find(w => w.s >= after && w.w.toLowerCase().includes(s.toLowerCase())); return w ? w.s : after; };
const mouthAt = t => { const i = Math.floor((t - LEAD) * ENV.fps); return i >= 0 && i < ENV.env.length ? ENV.env[i] : 0; };

// ---------- renderer ----------
const glc = document.createElement('canvas'); glc.width = W; glc.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
const out = document.getElementById('out'); const ctx = out.getContext('2d');
await Promise.all([
  new FontFace('PB', 'url(Poppins-Bold.ttf)').load().then(f => document.fonts.add(f)),
  new FontFace('PM', 'url(Poppins-Medium.ttf)').load().then(f => document.fonts.add(f)),
]);
const logo = new Image(); logo.src = 'arunika-logo-putih.png'; await logo.decode();

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x8fd3f5);
scene.fog = new THREE.Fog(0x8fd3f5, 60, 140);
const cam = new THREE.PerspectiveCamera(40, W / H, 0.1, 400);
const hemi = new THREE.HemisphereLight(0xdff4ff, 0xe8c98c, 1.25); scene.add(hemi);
const sun = new THREE.DirectionalLight(0xffffff, 2.0); sun.position.set(8, 16, 10); sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024); Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 50 }); sun.shadow.camera.updateProjectionMatrix();
scene.add(sun);
const M = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.85, flatShading: true, ...o });
const box = (w, h, d, c) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), typeof c === 'number' ? M(c) : c); m.castShadow = m.receiveShadow = true; return m; };
const cyl = (rt, rb, h, seg, c) => { const m = new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), typeof c === 'number' ? M(c) : c); m.castShadow = m.receiveShadow = true; return m; };
const at = (m, x, y, z) => { m.position.set(x, y, z); return m; };
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t; }

// ---------- laut & pulau ----------
const sea = new THREE.Mesh(new THREE.CircleGeometry(300, 64), new THREE.MeshStandardMaterial({ color: 0x1e9bd7, roughness: 0.35 }));
sea.rotation.x = -Math.PI / 2; sea.position.y = -0.35; sea.receiveShadow = true; scene.add(sea);
const shallow = new THREE.Mesh(new THREE.CircleGeometry(16.5, 48), new THREE.MeshStandardMaterial({ color: 0x48d1cc, roughness: 0.4, transparent: true, opacity: 0.85 }));
shallow.rotation.x = -Math.PI / 2; shallow.position.y = -0.3; scene.add(shallow);
const island = cyl(12.5, 14, 0.7, 28, 0xf2d79b); island.position.y = -0.3; scene.add(island);
const grass = cyl(6.5, 7, 0.12, 20, 0x8fcf6a); grass.position.set(-1.5, 0.08, -3); scene.add(grass);
function palm(x, z, s = 1, lean = 0.15) {
  const g = new THREE.Group(); g.position.set(x, 0, z); g.scale.setScalar(s);
  for (let i = 0; i < 6; i++) { const seg = cyl(0.18 - i * 0.012, 0.2 - i * 0.012, 0.7, 6, 0x8a6239); seg.position.set(lean * i * i * 0.12, 0.35 + i * 0.66, 0); seg.rotation.z = -lean * i * 0.18; g.add(seg); }
  const top = new THREE.Group(); top.position.set(lean * 25 * 0.12, 4.1, 0); g.add(top);
  for (let i = 0; i < 6; i++) { const lf = box(2.4, 0.06, 0.55, 0x2f9e4b); lf.position.x = 1.1; const p = new THREE.Group(); p.rotation.y = i * Math.PI / 3; p.rotation.z = -0.35; lf.rotation.z = -0.25; p.add(lf); top.add(p); }
  for (let i = 0; i < 3; i++) { const c = new THREE.Mesh(new THREE.IcosahedronGeometry(0.2, 0), M(0x6b4a22)); c.position.set(Math.cos(i * 2.1) * 0.25, -0.2, Math.sin(i * 2.1) * 0.25); top.add(c); }
  scene.add(g); return g;
}
palm(-7, -2, 1.1); palm(7.5, -4, 1.2, -0.12); palm(-5, -8, 0.95); palm(4, -9.5, 1.0);
for (const [x, z, s] of [[-9, 3, 0.7], [9, 2, 0.55], [6, 6, 0.4], [-3, 8, 0.45]]) { const r = new THREE.Mesh(new THREE.DodecahedronGeometry(s, 0), M(0x9a9a9a)); r.position.set(x, s * 0.4, z); r.castShadow = true; scene.add(r); }
// bangkai kapal Jarwo
const wreck = new THREE.Group(); wreck.position.set(10, 0, -1); wreck.rotation.set(0.15, 0.6, 0.3);
wreck.add(box(3.4, 0.9, 1.3, 0x8b5a2b)); const mast = box(0.15, 2.2, 0.15, 0x6e4321); mast.position.set(0.3, 1.2, 0); mast.rotation.z = 0.5; wreck.add(mast); scene.add(wreck);

// ---------- Kapten Jarwo (low-poly) ----------
function makeJarwo() {
  const g = new THREE.Group();
  const skin = M(0xa8714a), white = M(0xf4f4f0), navy = M(0x1d2b5e), black = M(0x1b1b1b), boot = M(0x4a3020);
  const stripe = new THREE.MeshStandardMaterial({ roughness: 0.85, flatShading: true, map: canvasTex(64, 64, (c, w, h) => { for (let i = 0; i < 8; i++) { c.fillStyle = i % 2 ? '#1d2b5e' : '#f4f4f0'; c.fillRect(0, i * 8, w, 8); } }) });
  const body = box(1.3, 1.25, 0.9, stripe); body.position.y = 1.65; g.add(body);
  const belt = box(1.32, 0.12, 0.92, 0x5a3a1e); belt.position.y = 1.05; g.add(belt);
  g.userData.legs = [];
  for (const s of [-1, 1]) {
    const leg = new THREE.Group(); leg.position.set(s * 0.33, 1.0, 0); g.add(leg); g.userData.legs.push(leg);
    const l = box(0.48, 0.75, 0.55, navy); l.position.y = -0.4; leg.add(l);
    const b = box(0.52, 0.28, 0.7, boot); b.position.set(0, -0.86, 0.06); leg.add(b);
  }
  g.userData.arms = [];
  for (const s of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(s * 0.82, 2.15, 0); g.add(arm); g.userData.arms.push(arm);
    const a = box(0.36, 0.95, 0.4, stripe); a.position.y = -0.45; arm.add(a);
    const hnd = box(0.36, 0.3, 0.36, skin); hnd.position.y = -1.05; arm.add(hnd);
  }
  const head = new THREE.Group(); head.position.y = 2.75; g.add(head); g.userData.head = head;
  const hd = box(1.25, 1.2, 1.1, skin); head.add(hd);
  const nose = box(0.32, 0.32, 0.3, M(0x96613d)); nose.position.set(0, -0.02, 0.62); head.add(nose);
  for (const s of [-1, 1]) {
    const e = box(0.32, 0.36, 0.08, white); e.position.set(s * 0.27, 0.22, 0.56); head.add(e);
    const p = box(0.15, 0.18, 0.06, black); p.position.set(s * 0.25, 0.2, 0.61); head.add(p);
    const br = box(0.38, 0.1, 0.08, black); br.position.set(s * 0.27, 0.47, 0.57); br.rotation.z = s * -0.12; head.add(br); (g.userData.brows ||= []).push(br);
    const mu = box(0.52, 0.2, 0.14, black); mu.position.set(s * 0.26, -0.24, 0.6); mu.rotation.z = s * 0.25; head.add(mu);
  }
  const mouth = box(0.42, 0.12, 0.06, M(0x5a1e1e)); mouth.position.set(0, -0.42, 0.56); head.add(mouth); g.userData.mouth = mouth;
  const hat = new THREE.Group(); hat.position.y = 0.66; head.add(hat);
  const crown = cyl(0.72, 0.66, 0.42, 10, white); crown.position.y = 0.2; hat.add(crown);
  const band = cyl(0.67, 0.67, 0.14, 10, navy); band.position.y = 0.06; hat.add(band);
  const brim = box(1.2, 0.08, 0.42, black); brim.position.set(0, 0.0, 0.62); hat.add(brim);
  const badge = cyl(0.13, 0.13, 0.05, 10, M(0xd4a62a, { metalness: 0.4 })); badge.rotation.x = Math.PI / 2; badge.position.set(0, 0.22, 0.7); hat.add(badge);
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return g;
}
const jarwo = makeJarwo(); scene.add(jarwo);

// ---------- spanduk KOPDES ----------
const bannerTex = canvasTex(1024, 300, (c, w, h) => {
  c.fillStyle = '#d7262e'; c.fillRect(0, 0, w, h / 2); c.fillStyle = '#ffffff'; c.fillRect(0, h / 2, w, h / 2);
  c.lineWidth = 14; c.strokeStyle = '#14215B'; c.strokeRect(7, 7, w - 14, h - 14);
  c.font = 'bold 120px PB'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillStyle = '#ffffff'; c.fillText('KOPDES', w / 2, h * 0.27);
  c.font = 'bold 64px PB'; c.fillStyle = '#d7262e'; c.fillText('PULAU KOMEN', w / 2, h * 0.75);
});
const banner = new THREE.Group();
const cloth = new THREE.Mesh(new THREE.PlaneGeometry(4.4, 1.3), new THREE.MeshStandardMaterial({ map: bannerTex, side: THREE.DoubleSide, roughness: 0.9 }));
cloth.position.y = 5.0; banner.add(cloth);
for (const s of [-1, 1]) { const p = cyl(0.07, 0.07, 5.6, 6, 0x7a5230); p.position.set(s * 2.25, 2.8, 0); banner.add(p); }
scene.add(banner);

// ---------- koperasi (dibangun bertahap) ----------
const coop = new THREE.Group(); coop.position.set(0, 0, -5.5); scene.add(coop);
const coopBase = new THREE.Group(); coop.add(coopBase);
coopBase.add(at(box(7, 0.3, 4.5, 0xbfa77a), 0, 0.15, 0));
const wallM = M(0xf6efe0); const roofM = M(0xd7262e);
const wb = box(7, 3, 0.3, wallM); wb.position.set(0, 1.8, -2.1); coopBase.add(wb);
for (const s of [-1, 1]) { const ws = box(0.3, 3, 4.2, wallM); ws.position.set(s * 3.35, 1.8, 0); coopBase.add(ws); }
const roof = new THREE.Mesh(new THREE.ConeGeometry(5.4, 2, 4), roofM); roof.rotation.y = Math.PI / 4; roof.scale.set(1, 1, 0.68); roof.position.y = 4.3; roof.castShadow = true; coopBase.add(roof);
const signTex = canvasTex(1024, 220, (c, w, h) => { c.fillStyle = '#14215B'; c.fillRect(0, 0, w, h); c.fillStyle = '#FFB800'; c.font = 'bold 92px PB'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('KOPERASI PULAU KOMEN', w / 2, h / 2 + 4); });
const sign = new THREE.Mesh(new THREE.PlaneGeometry(6.4, 1.35), new THREE.MeshStandardMaterial({ map: signTex })); sign.position.set(0, 3.55, 2.2); coopBase.add(sign);
const counter = box(6.2, 1.1, 0.6, 0x8b5a2b); counter.position.set(0, 0.85, 1.9); coopBase.add(counter);
// 5 fungsi = 5 properti
const props = [];
function addProp(make, x, z) { const g = new THREE.Group(); g.position.set(x, 0, z); make(g); coop.add(g); props.push(g); return g; }
addProp(g => { for (let i = 0; i < 3; i++) { const s = box(0.7, 0.9, 0.5, [0xe9e2c8, 0xd9c79a, 0xe9e2c8][i]); s.position.set(-0.8 + i * 0.8, 1.85, 1.9); g.add(s); } const o = cyl(0.18, 0.18, 0.6, 8, 0xf2b705); o.position.set(1.4, 1.7, 1.9); g.add(o); }, -1.8, 0);                       // sembako
addProp(g => { const s = box(1.1, 1.1, 0.9, 0x3a4a6b); s.position.set(0, 0.85, 0); g.add(s); const d = cyl(0.25, 0.25, 0.08, 12, 0xd4a62a); d.rotation.x = Math.PI / 2; d.position.set(0, 0.9, 0.48); g.add(d); }, 4.6, 1.6);            // simpan pinjam (brankas)
addProp(g => { for (let i = 0; i < 4; i++) { const c = box(0.9, 0.55, 0.7, 0xb5824a); c.position.set((i % 2) * 1.0, 0.3 + Math.floor(i / 2) * 0.58, 0); g.add(c); const v = box(0.7, 0.12, 0.5, [0xd62828, 0xe7c64b, 0x5aa9d6, 0xd62828][i]); v.position.set((i % 2) * 1.0, 0.62 + Math.floor(i / 2) * 0.58, 0); g.add(v); } }, -5.6, 1.2); // panen
addProp(g => { const f = box(1.6, 2.2, 1.3, 0xdff3fb); f.position.set(0, 1.1, 0); g.add(f); const l = box(0.08, 0.9, 0.08, 0x9aa); l.position.set(0.6, 1.3, 0.68); g.add(l); const sn = box(0.5, 0.5, 0.05, 0x5aa9d6); sn.position.set(-0.2, 1.7, 0.67); g.add(sn); }, 4.9, -1.2);   // gudang pendingin
addProp(g => { const k = box(2.0, 1.8, 1.6, 0xffffff); k.position.set(0, 0.9, 0); g.add(k); const c1 = box(0.7, 0.22, 0.06, 0x23a455); c1.position.set(0, 1.25, 0.82); g.add(c1); const c2 = box(0.22, 0.7, 0.06, 0x23a455); c2.position.set(0, 1.25, 0.82); g.add(c2); }, -5.2, -1.4); // klinik
// saran: rak hasil pulau, kapal patungan, papan catatan uang
const fishStand = new THREE.Group(); fishStand.position.set(-2.6, 0, 1.6); scene.add(fishStand);
fishStand.add(at(box(2.2, 0.9, 0.9, 0x8b5a2b), 0, 0.45, 0));
for (let i = 0; i < 3; i++) { const f = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.7, 5), M(0x6f9fc8)); f.rotation.z = Math.PI / 2; f.position.set(-0.6 + i * 0.35, 1.0, 0); fishStand.add(f); }
for (let i = 0; i < 2; i++) { const k = new THREE.Mesh(new THREE.IcosahedronGeometry(0.28, 0), M(0x6b4a22)); k.position.set(0.45 + i * 0.4, 1.05, 0); fishStand.add(k); }
const salt = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.5, 6), M(0xffffff)); salt.position.set(0.0, 1.15, 0.25); fishStand.add(salt);
const boat = new THREE.Group(); scene.add(boat);
boat.add(at(box(3.6, 0.8, 1.4, 0x2f6fb5), 0, 0.1, 0));
for (let i = 0; i < 4; i++) { const c = box(0.6, 0.5, 0.6, [0xb5824a, 0xd9c79a][i % 2]); c.position.set(-1.1 + i * 0.7, 0.75, 0); boat.add(c); }
const sail = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2), M(0xf4f4f0, { side: THREE.DoubleSide })); sail.position.set(0.2, 2.0, 0); boat.add(sail);
const boardTex = canvasTex(512, 640, (c, w, h) => { c.fillStyle = '#fbf7ea'; c.fillRect(0, 0, w, h); c.fillStyle = '#14215B'; c.font = 'bold 50px PB'; c.textAlign = 'center'; c.fillText('CATATAN UANG', w / 2, 70); c.font = 'bold 36px PM'; c.textAlign = 'left'; const rows = [['Masuk', '+'], ['Keluar', '−'], ['Sisa', '=']]; rows.forEach((r, i) => { c.fillStyle = '#14215B'; c.fillText(r[0], 50, 180 + i * 130); c.fillStyle = '#12C2B0'; c.fillRect(260, 140 + i * 130, 200, 54); c.fillStyle = '#ffffff'; c.fillText(r[1] + ' Rp…', 280, 182 + i * 130); }); });
const board = new THREE.Group(); board.position.set(2.8, 0, 1.5); board.rotation.y = -0.35; scene.add(board);
board.add(at(new THREE.Mesh(new THREE.PlaneGeometry(1.6, 2.0), new THREE.MeshStandardMaterial({ map: boardTex })), 0, 2.0, 0.06));
board.add(at(box(1.8, 2.2, 0.1, 0x6e4321), 0, 2.0, 0));
for (const s of [-1, 1]) board.add(at(box(0.12, 1.2, 0.12, 0x6e4321), s * 0.7, 0.6, 0));
// plang usulan
const plangTex = canvasTex(1024, 300, (c, w, h) => { c.fillStyle = '#FFB800'; c.fillRect(0, 0, w, h); c.strokeStyle = '#14215B'; c.lineWidth = 16; c.strokeRect(8, 8, w - 16, h - 16); c.fillStyle = '#14215B'; c.textAlign = 'center'; c.font = 'bold 66px PB'; c.fillText('USULAN', w / 2, 110); c.font = 'bold 84px PB'; c.fillText('@idontknow_8211', w / 2, 215); });
const plang = new THREE.Group(); plang.position.set(0.5, 0, 3.4); scene.add(plang);
plang.add(at(new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.82), new THREE.MeshStandardMaterial({ map: plangTex })), 0, 1.75, 0.06));
plang.add(at(box(0.14, 1.8, 0.14, 0x6e4321), 0, 0.9, 0));
// konfeti
const confetti = new THREE.Group(); scene.add(confetti);
const cols = [0xFFB800, 0x12C2B0, 0xd7262e, 0xffffff, 0x5aa9d6];
for (let i = 0; i < 160; i++) { const c = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.26), new THREE.MeshBasicMaterial({ color: cols[i % 5], side: THREE.DoubleSide })); c.userData = { x: (Math.sin(i * 12.9898) * 43758.5 % 1) * 12 - 6, z: (Math.sin(i * 78.233) * 12345.6 % 1) * 6 - 1, v: 1.5 + (i % 7) * 0.3, r: i }; confetti.add(c); }

// ---------- kamera per adegan ----------
const SHOTS = [
  // [mulai, posisi kamera, target]
  [0, [0, 3.6, 13.5], [0, 3.2, 0]],                 // frame 0: Jarwo + spanduk
  [P[1], [1.8, 3.4, 6.2], [0, 3.0, 0]],             // close Jarwo
  [P[2], [0, 7, 15], [0, 2, -4.5]],                 // koperasi muncul
  [P[7], [-4, 5, 9], [0, 2.5, -3]],
  [P[8], [2.5, 3.2, 6.5], [0, 2.8, 0]],
  [P[9], [-6, 9, 16], [0, 1, -2]],
  [P[10], [0, 70, 55], [0, 0, 0]],                  // zoom out: pulau kecil di laut
  [P[11], [1.8, 3.4, 6.2], [0, 3.0, 0]],
  [P[12], [-5, 3.6, 7.5], [-2.6, 1.2, 1.6]],         // rak ikan
  [P[13], [13, 6, 15], [7.5, 1, 3]],                   // kapal
  [P[14], [5.5, 3.4, 7], [2.8, 2, 1.5]],            // papan catatan
  [P[15], [0, 6, 16], [0, 2.2, -2]],                // koperasi jadi
  [P[16], [1.8, 3.4, 6.2], [0, 3.0, 0]],
  [P[17], [-2, 5, 12], [0, 2.4, -2]],
];
function camAt(t) {
  let k = 0; for (let i = 0; i < SHOTS.length; i++) if (t >= SHOTS[i][0]) k = i;
  const [s0, p, q] = SHOTS[k]; const prev = SHOTS[Math.max(0, k - 1)];
  const u = k === 0 ? 1 : easeOut((t - s0) / 0.8);
  const pos = p.map((v, i) => lerp(prev[1][i], v, u)), tg = q.map((v, i) => lerp(prev[2][i], v, u));
  const drift = (t - s0) * 0.12;
  cam.position.set(pos[0] + Math.sin(t * 0.3) * 0.15 + drift * 0.3, pos[1], pos[2] - drift * 0.4);
  cam.lookAt(tg[0], tg[1], tg[2]);
}

// ---------- 2D overlay ----------
const NAVY = '#14215B', YEL = '#FFB800', TEAL = '#12C2B0';
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
function pill(x, y, text, bg, fg, size = 34, pad = 22) { ctx.font = `bold ${size}px PB`; const w = ctx.measureText(text).width + pad * 2, h = size * 1.6; rr(x, y, w, h, 14); ctx.fillStyle = bg; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = NAVY; ctx.stroke(); ctx.fillStyle = fg; ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; ctx.fillText(text, x + pad, y + h / 2 + 2); return w; }
function outlineText(text, x, y, size, fill = '#fff', align = 'center', stroke = 12) { ctx.font = `bold ${size}px PB`; ctx.textAlign = align; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round'; ctx.lineWidth = stroke; ctx.strokeStyle = 'rgba(10,20,50,.9)'; ctx.strokeText(text, x, y); ctx.fillStyle = fill; ctx.fillText(text, x, y); }
function wrapLines(text, size, maxW) { ctx.font = `bold ${size}px PB`; const ws = text.split(' '); const lines = []; let cur = ''; for (const w of ws) { const tst = cur ? cur + ' ' + w : w; if (ctx.measureText(tst).width > maxW && cur) { lines.push(cur); cur = w; } else cur = tst; } if (cur) lines.push(cur); return lines; }
function hud(t) {
  pill(40, 60, 'HARI 2', YEL, NAVY, 34);
  ctx.font = 'bold 34px PB'; const txt = `PENDUDUK: ${PEND}`; const w = ctx.measureText(txt).width + 44; pill(W - 40 - w, 60, txt, NAVY, '#fff', 34);
}
function bubble(x, y, user, text, likes, a, scale = 1) {
  if (a <= 0) return; ctx.save(); ctx.globalAlpha = clamp(a); ctx.translate(x, y); ctx.scale(scale, scale);
  const w = 760, h = 150; rr(-w / 2, 0, w, h, 26); ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = NAVY; ctx.stroke();
  ctx.beginPath(); ctx.arc(-w / 2 + 70, 75, 44, 0, Math.PI * 2); ctx.fillStyle = TEAL; ctx.fill();
  ctx.fillStyle = '#fff'; ctx.font = 'bold 40px PB'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(user.replace(/[^a-z]/i, '')[0].toUpperCase(), -w / 2 + 70, 77);
  ctx.textAlign = 'left'; ctx.fillStyle = '#555'; ctx.font = 'bold 30px PB'; ctx.fillText('@' + user, -w / 2 + 135, 48);
  ctx.fillStyle = '#111'; let fs = 40; ctx.font = `bold ${fs}px PB`; while (ctx.measureText(text).width > w - 260 && fs > 24) { fs -= 2; ctx.font = `bold ${fs}px PB`; } ctx.fillText(text, -w / 2 + 135, 100);
  ctx.fillStyle = '#e0245e'; ctx.font = 'bold 34px PB'; ctx.textAlign = 'right'; ctx.fillText('♥ ' + likes, w / 2 - 28, 75);
  ctx.restore();
}
function card(cx, y, w, h, a, fn) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = clamp(a); const s = lerp(0.85, 1, clamp(a)); ctx.translate(cx, y + h / 2); ctx.scale(s, s); ctx.translate(-cx, -(y + h / 2)); rr(cx - w / 2, y, w, h, 30); ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = NAVY; ctx.stroke(); fn(cx - w / 2, y, w, h); ctx.restore(); }
function numCard(n, emoji, title, sub, a, y = 230) {
  card(W / 2, y, 900, 210, a, (x, y0, w, h) => {
    ctx.beginPath(); ctx.arc(x + 95, y0 + h / 2, 62, 0, Math.PI * 2); ctx.fillStyle = YEL; ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = NAVY; ctx.stroke();
    ctx.fillStyle = NAVY; ctx.font = 'bold 64px PB'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(String(n), x + 95, y0 + h / 2 + 4);
    ctx.font = '84px "Noto Color Emoji"'; ctx.fillText(emoji, x + w - 95, y0 + h / 2 + 6);
    ctx.textAlign = 'left'; ctx.fillStyle = NAVY; ctx.font = 'bold 50px PB'; ctx.fillText(title, x + 185, y0 + 78);
    ctx.fillStyle = '#4a5578'; ctx.font = 'bold 32px PM'; ctx.fillText(sub, x + 185, y0 + 145);
  });
}
function source(text, a) { if (a <= 0) return; ctx.save(); ctx.globalAlpha = clamp(a) * 0.95; ctx.font = 'bold 26px PM'; const w = ctx.measureText(text).width + 36; rr(40, 1255, w, 50, 12); ctx.fillStyle = 'rgba(20,33,91,.85)'; ctx.fill(); ctx.fillStyle = '#fff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(text, 58, 1281); ctx.restore(); }
function subtitle(t) {
  const c = CH.find(c => t >= c.s && t < c.show_end); if (!c) return;
  const lines = wrapLines(c.text, 66, 900); const y0 = 1420 - (lines.length - 1) * 40;
  const u = pop(t, c.s, 0.18); ctx.save(); ctx.translate(W / 2, y0); ctx.scale(lerp(0.9, 1, u), lerp(0.9, 1, u));
  lines.forEach((l, i) => outlineText(l, 0, i * 80, 66)); ctx.restore();
}
const FN = [['🛒', 'Warung sembako', 'harga diusahakan lebih murah'], ['💰', 'Simpan pinjam', 'tanpa bank keliling'], ['🌾', 'Beli hasil panen', 'tidak dilepas murah ke tengkulak'], ['❄️', 'Gudang pendingin', 'panen tidak cepat busuk'], ['🏥', 'Klinik & apotek desa', 'tidak usah jauh ke kota']];
const SR = [['🐟', 'Jual produk kampung', 'ikan, kelapa, garam laut'], ['🚤', 'Kirim patungan', 'satu kapal, ongkos dibagi'], ['📋', 'Catatan uang terbuka', 'ditempel di depan koperasi']];
const USERS = [['_asthree_', 'SPPG atau KOPDES', 1], ['dwi_andika_16', 'Bangun kopdes', 1], ['idontknow_8211', 'KTP MAU BUKA KOPDES 🔥', 6], ['elbaraaa15', 'KTP, bikin kopdes, jadi coe kopdes', 1], ['queendahyunnnn', 'Bikin kopdes', 2]];
const NAMEKEY = ['asthree', 'dwi', 'idontknow', 'elbaraaa', 'queendahyun'];

function overlay(t) {
  hud(t);
  // P0: judul cover + komentar
  if (t < P[1]) {
    const tOut = ramp(t, wordT('Yang', 0) - 0.1, 0.25);
    if (tOut < 1) { ctx.save(); ctx.globalAlpha = 1 - tOut; outlineText('KOPDES', W / 2, 330, 150, YEL, 'center', 16); outlineText('ISINYA APA?', W / 2, 470, 112, '#fff', 'center', 14); ctx.restore(); }
    // bubble pemenang (setelah dtk 1)
    if (tOut < 1) bubble(W / 2, 600, USERS[2][0], USERS[2][1], USERS[2][2], ramp(t, 1.0, 0.3) * (1 - tOut));
    USERS.forEach((u, i) => { const ts = wordT(NAMEKEY[i], 1); bubble(W / 2, 200 + i * 175, u[0], u[1], u[2], ramp(t, ts - 0.15, 0.25), lerp(0.8, 1, pop(t, ts - 0.15, 0.3)) * 0.92); });
  }
  if (t >= P[1] && t < P[2]) { outlineText('KOPDES', W / 2, 330, 120, YEL); outlineText('ISINYA APA SAJA?', W / 2, 450, 84); }
  // follow kecil (sepertiga awal)
  if (t > 12 && t < 30) { ctx.save(); ctx.globalAlpha = ramp(t, 12, 0.4) * (1 - ramp(t, 29.5, 0.4)); pill(40, 140, 'Follow = jadi penduduk + KTP', TEAL, '#fff', 28); ctx.restore(); }
  // fungsi 1-5
  for (let i = 0; i < 5; i++) { const a = P[2 + i], b = P[3 + i]; if (t >= a - 0.1 && t < b) numCard(i + 1, FN[i][0], FN[i][1], FN[i][2], ramp(t, a, 0.3)); }
  if (t >= P[7] && t < P[8]) { FN.forEach((f, i) => { const a = pop(t, P[7] + i * 0.12, 0.3); ctx.save(); ctx.globalAlpha = clamp(a); const x = 150 + (i % 3) * 390, y = 260 + Math.floor(i / 3) * 210; rr(x - 170, y, 340, 180, 24); ctx.fillStyle = '#fff'; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = NAVY; ctx.stroke(); ctx.font = '70px "Noto Color Emoji"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(f[0], x, y + 65); ctx.fillStyle = NAVY; ctx.font = 'bold 28px PB'; ctx.fillText(f[1], x, y + 145); ctx.restore(); }); outlineText('LENGKAP, TOH?', W / 2, 760, 96, YEL); }
  // angka beroperasi
  if (t >= P[8] && t < P[9]) {
    card(W / 2, 220, 920, 520, ramp(t, P[8], 0.3), (x, y, w, h) => {
      const tA = wordT('sepuluh', P[8]), tB = wordT('delapan', P[8]);
      ctx.textAlign = 'left'; ctx.textBaseline = 'middle';
      ctx.fillStyle = NAVY; ctx.font = 'bold 40px PB'; ctx.fillText('Buka & jualan (Okt 2026)', x + 50, y + 80);
      const bw = (w - 100);
      const u1 = easeOut((t - tA) / 0.8); rr(x + 50, y + 120, Math.max(1, bw * 10070 / 83383 * u1), 80, 14); ctx.fillStyle = TEAL; ctx.fill();
      ctx.fillStyle = NAVY; ctx.font = 'bold 54px PB'; if (t > tA) ctx.fillText('±10.070', x + 70 + bw * 10070 / 83383, y + 162);
      ctx.font = 'bold 40px PB'; ctx.fillText('Terdaftar (Jun 2026)', x + 50, y + 290);
      const u2 = easeOut((t - tB) / 0.8); rr(x + 50, y + 330, Math.max(1, bw * u2), 80, 14); ctx.fillStyle = YEL; ctx.fill();
      ctx.fillStyle = NAVY; ctx.font = 'bold 54px PB'; if (t > tB + 0.5) { ctx.textAlign = 'right'; ctx.fillText('83.383', x + w - 70, y + 372); }
      if (t > tB + 0.8) { ctx.textAlign = 'center'; ctx.fillStyle = '#d7262e'; ctx.font = 'bold 44px PB'; ctx.fillText('baru ±1 dari 8', x + w / 2, y + 470); }
    });
    source('Sumber: Bakom RI (15 Okt 2026) · IDN Research Institute (Jun 2026)', ramp(t, P[8] + 0.5));
  }
  if (t >= P[9] && t < P[10]) {
    const items = [['🚚', 'Kirim barang mahal', 'mahal'], ['👥', 'Pengurus cuma 3–5 orang', 'Pengurusnya'], ['🤔', 'Mau jual apa?', 'bingung']];
    outlineText('PALING SUSAH:', W / 2, 270, 70, YEL); outlineText('KAMPUNG YANG JAUH', W / 2, 360, 70);
    items.forEach((it, i) => { const ts = wordT(it[2], P[9]); card(W / 2, 440 + i * 190, 860, 160, ramp(t, ts - 0.2, 0.3), (x, y, w, h) => { ctx.font = '76px "Noto Color Emoji"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(it[0], x + 90, y + h / 2 + 4); ctx.fillStyle = NAVY; ctx.font = 'bold 46px PB'; ctx.textAlign = 'left'; ctx.fillText(it[1], x + 175, y + h / 2 + 2); }); });
    source('Sumber: IDN Research Institute (31 Agu 2026)', ramp(t, P[9] + 0.5));
  }
  if (t >= P[10] && t < P[11]) { const te = wordT('Itu', P[10]); if (t > te - 0.1) { const u = pop(t, te - 0.1, 0.35); ctx.save(); ctx.translate(W / 2, 560); ctx.scale(u, u); outlineText('ITU PULAU KITA!', 0, 0, 104, YEL, 'center', 16); ctx.restore(); } }
  if (t >= P[11] && t < P[12]) { outlineText('3 SARAN JARWO', W / 2, 330, 104, YEL); outlineText('BUAT KOPDES', W / 2, 450, 84); }
  for (let i = 0; i < 3; i++) { const a = P[12 + i], b = P[13 + i]; if (t >= a - 0.1 && t < b) numCard(i + 1, SR[i][0], SR[i][1], SR[i][2], ramp(t, a, 0.3)); }
  if (t >= P[15] && t < P[16]) { const u = pop(t, P[15], 0.4); ctx.save(); ctx.translate(W / 2, 330); ctx.scale(u, u); outlineText('RESMI BUKA!', 0, 0, 120, YEL, 'center', 16); ctx.restore(); const tb = wordT('idontknow', P[15]); card(W / 2, 440, 760, 130, ramp(t, tb - 0.2, 0.3), (x, y, w, h) => { ctx.font = '60px "Noto Color Emoji"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('🔨', x + 70, y + h / 2 + 4); ctx.fillStyle = NAVY; ctx.font = 'bold 34px PB'; ctx.textAlign = 'left'; ctx.fillText('Arsitek Pulau', x + 130, y + 45); ctx.font = 'bold 40px PB'; ctx.fillText('@idontknow_8211', x + 130, y + 92); }); }
  if (t >= P[16] && t < P[17]) {
    outlineText('DI KAMPUNGMU,', W / 2, 260, 76, '#fff'); outlineText('KOPDES SUDAH JALAN?', W / 2, 350, 76, YEL);
    const tk = wordT('sudah,', P[16] + 2);
    [['SUDAH', '#23a455'], ['BELUM', '#e08a00'], ['BELUM ADA', '#d7262e']].forEach((b, i) => { const a = pop(t, tk + i * 0.35, 0.3); if (a <= 0) return; ctx.save(); ctx.globalAlpha = clamp(a); const y = 450 + i * 150; rr(W / 2 - 330, y, 660, 120, 60); ctx.fillStyle = b[1]; ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = NAVY; ctx.stroke(); ctx.fillStyle = '#fff'; ctx.font = 'bold 58px PB'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(b[0], W / 2, y + 63); ctx.restore(); });
    const ts = wordT('saran', P[16] + 4); if (t > ts - 0.2) { ctx.save(); ctx.globalAlpha = ramp(t, ts - 0.2); pill(W / 2 - 300, 920, '💬 Punya saran lain? Tulis juga!', '#fff', NAVY, 36); ctx.restore(); }
    const tp = wordT('peta', P[16]); if (t > tp - 0.2) { ctx.save(); ctx.globalAlpha = ramp(t, tp - 0.2); pill(W / 2 - 290, 1030, '🗺️ jadi PETA KOPDES episode depan', YEL, NAVY, 34); ctx.restore(); }
  }
  if (t >= P[17]) {
    const u = ramp(t, P[17], 0.3); ctx.save(); ctx.globalAlpha = u; card(W / 2, 250, 900, 230, u, (x, y, w, h) => { ctx.font = '86px "Noto Color Emoji"'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('📍', x + 100, y + h / 2); ctx.fillStyle = NAVY; ctx.font = 'bold 46px PB'; ctx.textAlign = 'left'; ctx.fillText('Kirim ke teman', x + 190, y + 85); ctx.fillText('sekampungmu!', x + 190, y + 150); }); ctx.restore();
    const tl = wordT('Koperasinya', P[17]); if (t > tl - 0.1) { outlineText('YANG BIKIN JALAN,', W / 2, 600, 72); outlineText('KITA-KITA JUGA.', W / 2, 690, 86, YEL); }
    const tz = T.vo_end - 1.2; if (t > tz) { ctx.save(); ctx.globalAlpha = ramp(t, tz, 0.4); const lw = 360, lh = lw * logo.height / logo.width; ctx.drawImage(logo, W / 2 - lw / 2, 830, lw, lh); ctx.restore(); }
  }
  subtitle(t);
  // progress bar
  ctx.fillStyle = YEL; ctx.fillRect(0, H - 14, W * clamp(t / TOTAL), 14);
}

// ---------- animasi 3D ----------
function animate(t) {
  // Jarwo: posisi & pose
  let jp = [0, 0, 0.6], jr = 0;
  if (t >= P[2] && t < P[7]) { jp = [2.2, 0, 2.2]; jr = -0.5; }
  if (t >= P[7] && t < P[8]) { jp = [1.8, 0, 1.5]; jr = -0.3; }
  if (t >= P[12] && t < P[13]) { jp = [0.6, 0, 2.6]; jr = -0.6; }
  if (t >= P[14] && t < P[15]) { jp = [0.9, 0, 2.2]; jr = 0.5; }
  if (t >= P[15] && t < P[16]) { jp = [-1.6, 0, 3.2]; jr = 0.2; }
  if (t >= P[17]) { jp = [-1.2, 0, 2.8]; jr = 0.15; }
  jarwo.position.set(...jp); jarwo.rotation.y = jr + Math.sin(t * 0.9) * 0.06;
  const m = mouthAt(t); jarwo.userData.mouth.scale.y = 1 + m * 3.2; jarwo.userData.mouth.position.y = -0.42 - m * 0.08;
  jarwo.userData.head.rotation.z = Math.sin(t * 1.7) * 0.04; jarwo.userData.head.rotation.x = -m * 0.08;
  const shock = (t >= P[10] && t < P[11]) ? 1 : 0;
  jarwo.userData.brows.forEach((b, i) => { b.position.y = 0.47 + shock * 0.14 + m * 0.03; });
  const [aL, aR] = jarwo.userData.arms;
  const holdBanner = t < P[1];
  aL.rotation.x = holdBanner ? -2.6 : -0.15 + Math.sin(t * 2.2) * 0.12 * (m > 0.2 ? 1 : 0.2);
  aR.rotation.x = holdBanner ? -2.6 : -0.15 - Math.sin(t * 2.4 + 1) * 0.35 * (m > 0.2 ? 1 : 0.3);
  aL.rotation.z = holdBanner ? 0.25 : 0.12 + shock * 0.8; aR.rotation.z = holdBanner ? -0.25 : -0.12 - shock * 0.8;
  jarwo.position.y = Math.abs(Math.sin(t * 3)) * 0.04 + shock * Math.abs(Math.sin(t * 9)) * 0.15;
  // spanduk: dipegang di P0, lalu pindah ke depan koperasi
  if (t < P[2]) { banner.position.set(0, -0.6, -0.4); banner.visible = t < P[1]; cloth.rotation.y = Math.sin(t * 2) * 0.05; }
  else { banner.visible = false; }
  // koperasi muncul di P2, props per fungsi
  const cb = easeOut((t - P[2] + 0.4) / 0.8); coop.visible = t >= P[2] - 0.4;
  coopBase.scale.set(1, Math.max(0.001, cb), 1);
  props.forEach((g, i) => { const s = back((t - P[2 + i]) / 0.45); g.scale.setScalar(Math.max(0.001, s)); g.visible = t >= P[2 + i]; });
  fishStand.visible = t >= P[12]; fishStand.scale.setScalar(Math.max(0.001, back((t - P[12]) / 0.45)));
  boat.visible = t >= P[13]; const bu = easeOut((t - P[13]) / 3.5); boat.position.set(lerp(18, 8.5, bu), 0.1 + Math.sin(t * 2) * 0.08, 3.5); boat.rotation.z = Math.sin(t * 1.6) * 0.04; boat.rotation.y = -0.2;
  board.visible = t >= P[14]; board.scale.setScalar(Math.max(0.001, back((t - P[14]) / 0.45)));
  plang.visible = t >= wordT('Plangnya', P[15]) - 0.2; plang.scale.setScalar(Math.max(0.001, back((t - wordT('Plangnya', P[15]) + 0.2) / 0.45)));
  confetti.visible = t >= P[15] && t < P[16] + 1.5;
  confetti.children.forEach(c => { const d = c.userData; const tt = t - P[15]; c.position.set(d.x + Math.sin(tt * 2 + d.r) * 0.4, 9 - ((tt * d.v + (d.r % 13) * 0.5) % 10), d.z); c.rotation.set(tt * 3 + d.r, tt * 2 + d.r * 0.3, 0); });
  // laut beriak (warna)
  shallow.material.opacity = 0.8 + Math.sin(t * 1.3) * 0.05;
}

window.renderFrame = (t) => {
  animate(t); camAt(t);
  renderer.render(scene, cam);
  ctx.clearRect(0, 0, W, H); ctx.drawImage(glc, 0, 0);
  // gradasi lembut atas/bawah agar teks terbaca
  let g = ctx.createLinearGradient(0, 0, 0, 520); g.addColorStop(0, 'rgba(10,20,50,.35)'); g.addColorStop(1, 'rgba(10,20,50,0)'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, 520);
  g = ctx.createLinearGradient(0, 1250, 0, H); g.addColorStop(0, 'rgba(10,20,50,0)'); g.addColorStop(1, 'rgba(10,20,50,.45)'); ctx.fillStyle = g; ctx.fillRect(0, 1250, W, H - 1250);
  overlay(t);
};
window.READY = true;
