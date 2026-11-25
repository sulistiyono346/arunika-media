// ARN-61 "Bayangkan kamu di Anyer, 1883" — 3D sinematik gelap (three.js r160, lokal). Pangkalan: tools/r3d_kamu_pilih (ARN-40).
// Deterministik: window.renderFrame(t) menggambar frame waktu t (detik) ke <canvas id="out"> 1080x1920.
// Semua visual adalah ILUSTRASI. Korban tidak digambarkan: manusia hanya siluet, dampak lewat benda.
import * as THREE from './three.module.js';

const W = 1080, H = 1920;
const NAVY = 0x14215B, TEAL = 0x12C2B0, YEL = 0xFFB800;
const CNAVY = '#14215B', CTEAL = '#12C2B0', CYEL = '#FFB800';
const T = await (await fetch('timing.json')).json();
const CH = T.chunks, SC = T.scenes, TOTAL = T.total;
const cs = i => CH[i].s;
const CLOSE = SC[13];
const EMO = '"Noto Color Emoji"';

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
try { await document.fonts.load('40px "Noto Color Emoji"', '📤📌'); } catch (e) { }
const logo = new Image(); logo.src = 'arunika-logo-putih.png'; await logo.decode();

// ---------- tekstur & material ----------
function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const softTex = canvasTex(128, 128, (g, w, h) => { const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.35, 'rgba(255,255,255,.55)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); });
const smokeTex = canvasTex(128, 128, (g, w, h) => { const R = mulberry(7); for (let i = 0; i < 14; i++) { const x = 30 + R() * 68, y = 30 + R() * 68, rr = 18 + R() * 26; const r = g.createRadialGradient(x, y, 0, x, y, rr); r.addColorStop(0, 'rgba(255,255,255,.35)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); } });
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.0, ...o });
const emis = (color, k = 1) => new THREE.MeshStandardMaterial({ color: 0x000000, emissive: color, emissiveIntensity: k, roughness: 1 });
function sprite(color, s, op = 1, additive = true, tex = softTex) { const m = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, color, transparent: true, opacity: op, blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending, depthWrite: false })); m.scale.set(s, s, 1); return m; }

// ---------- Aru 3D (Syal Bendera), berdiri ----------
function makeAru() {
  const root = new THREE.Group(); const g = new THREE.Group(); g.position.y = 2.35; root.add(g); root.userData.body = g;
  const skin = std(0xFFD5B5, { roughness: 0.5 }), navyM = std(NAVY, { roughness: 0.7 }), tealM = std(TEAL, { roughness: 0.55 }), yelM = std(YEL, { roughness: 0.55 }), greyM = std(0x4d4a5a);
  const head = new THREE.Group(); head.position.y = 1.0; g.add(head); root.userData.head = head;
  head.add(new THREE.Mesh(new THREE.IcosahedronGeometry(1, 4), skin));
  for (const s of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.22, 16, 12), skin); e.position.set(s * 0.98, -0.05, 0); head.add(e); }
  const eyeM = std(0x0d1433, { roughness: 0.25 }), hiM = emis(0xffffff, 1.6), blushM = std(0xFFA48C, { roughness: 0.8 });
  root.userData.brows = [];
  for (const s of [-1, 1]) {
    const eye = new THREE.Group(); eye.position.set(s * 0.34, 0.05, 0.9); eye.rotation.y = s * 0.33; head.add(eye);
    const ball = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), eyeM); ball.scale.set(0.13, 0.17, 0.08); eye.add(ball);
    const hi = new THREE.Mesh(new THREE.SphereGeometry(0.04, 8, 6), hiM); hi.position.set(0.035, 0.06, 0.07); eye.add(hi);
    const bl = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8), blushM); bl.scale.set(0.15, 0.08, 0.04); bl.position.set(s * 0.56, -0.3, 0.8); bl.rotation.y = s * 0.6; head.add(bl);
    const brow = new THREE.Mesh(new THREE.CapsuleGeometry(0.035, 0.2, 4, 8), navyM); brow.rotation.order = 'YXZ'; brow.rotation.y = s * 0.3; brow.rotation.z = Math.PI / 2 - s * 0.28; brow.position.set(s * 0.33, 0.37, 0.93); head.add(brow); root.userData.brows.push(brow);
  }
  const mouth = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.028, 8, 20, Math.PI), std(0x5a2030)); mouth.position.set(0, -0.4, 0.93); head.add(mouth); root.userData.mouth = mouth;
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.7, 0.7, 6, 16), navyM); body.position.y = -0.55; body.scale.set(1, 1, 0.85); g.add(body);
  const scarf = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.2, 12, 32), tealM); scarf.rotation.x = Math.PI / 2; scarf.position.y = 0.02; g.add(scarf);
  const flag = new THREE.Group(); flag.position.set(0.42, -0.2, 0.62); flag.rotation.set(0.15, -0.2, -0.25); g.add(flag); root.userData.flag = flag;
  const f1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.06), tealM); f1.position.set(0.2, 0, 0); flag.add(f1);
  const f2 = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.2, 0.06), yelM); f2.position.set(0.17, -0.22, 0); flag.add(f2);
  root.userData.arms = []; root.userData.legs = [];
  for (const s of [-1, 1]) {
    const arm = new THREE.Group(); arm.position.set(s * 0.72, -0.25, 0); g.add(arm); root.userData.arms.push(arm);
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.5, 4, 10), navyM); up.position.y = -0.3; arm.add(up);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.19, 14, 10), skin); hand.position.y = -0.72; arm.add(hand);
    const leg = new THREE.Group(); leg.position.set(s * 0.32, -1.35, 0); g.add(leg); root.userData.legs.push(leg);
    const lm = new THREE.Mesh(new THREE.CapsuleGeometry(0.2, 0.55, 4, 10), greyM); lm.position.y = -0.4; leg.add(lm);
    const shoe = new THREE.Mesh(new THREE.SphereGeometry(0.24, 14, 10), yelM); shoe.scale.set(1, 0.6, 1.4); shoe.position.set(0, -0.85, 0.08); leg.add(shoe);
  }
  return root;
}
function aruPose(a, o = {}) {
  const u = a.userData; const g = u.body;
  g.rotation.set(o.lean || 0, 0, 0); g.position.y = 2.35 + (o.bob || 0);
  u.head.rotation.set(o.hx || 0, o.hy || 0, 0);
  const sw = o.swing || 0;
  u.arms.forEach((arm, i) => { const s = i ? 1 : -1; arm.rotation.set(o.armX !== undefined ? o.armX : -0.1 + s * sw, 0, s * (o.armZ !== undefined ? o.armZ : 0.15)); });
  if (o.point) { u.arms[0].rotation.set(-1.75, 0, -0.1); }
  u.legs.forEach((leg, i) => { const s = i ? 1 : -1; leg.rotation.set(-s * sw * 1.1, 0, 0); });
  const happy = o.mood === 1;
  u.mouth.rotation.z = happy ? Math.PI : 0; u.mouth.position.y = happy ? -0.3 : -0.42;
  u.flag.rotation.z = -0.25 + 0.08 * Math.sin((o.t || 0) * 3);
}

// ---------- PANTAI ANYER ----------
const bs = new THREE.Scene();
const skyU = { a: { value: new THREE.Color(0x070b1c) }, b: { value: new THREE.Color(0x26314d) }, c: { value: new THREE.Color(0x4b5168) } };
{
  const m = new THREE.ShaderMaterial({ side: THREE.BackSide, depthWrite: false, fog: false, uniforms: skyU,
    vertexShader: 'varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
    fragmentShader: 'uniform vec3 a,b,c; varying vec3 vp; void main(){ float h=vp.y; vec3 col = h>0.02? mix(b,a,clamp((h-0.02)/0.45,0.,1.)) : mix(c,b,clamp((h+0.1)/0.12,0.,1.)); gl_FragColor=vec4(col,1.); }' });
  const s = new THREE.Mesh(new THREE.SphereGeometry(1800, 32, 16), m); s.frustumCulled = false; bs.add(s);
}
bs.fog = new THREE.FogExp2(0x2e3650, 0.0016);
// awan gelap
const clouds = new THREE.Group(); bs.add(clouds);
{ const R = mulberry(19); for (let i = 0; i < 46; i++) { const sp = sprite(0x1a2034, 260 + R() * 320, 0.55 + R() * 0.3, false, smokeTex); sp.material.fog = false; const th = (R() - 0.5) * 2.4; sp.position.set(Math.sin(th) * 1300, 160 + R() * 380, -Math.cos(th) * 1300); clouds.add(sp); } }
// bintang (malam 2018)
const starPts = (() => { const R = mulberry(9), n = 500, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const th = R() * Math.PI * 2, ph = 0.1 + R() * 1.2; p[i * 3] = Math.cos(th) * Math.cos(ph) * 1500; p[i * 3 + 1] = Math.sin(ph) * 1500; p[i * 3 + 2] = Math.sin(th) * Math.cos(ph) * 1500; } const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); return new THREE.Points(g, new THREE.PointsMaterial({ color: 0xcfdcff, size: 2.2, sizeAttenuation: false, transparent: true, opacity: 0, fog: false })); })();
bs.add(starPts);
// pasir + dasar laut terbuka (warna per verteks)
{
  const g = new THREE.PlaneGeometry(1400, 1400, 220, 220); g.rotateX(-Math.PI / 2);
  const p = g.attributes.position, col = new Float32Array(p.count * 3); const c = new THREE.Color();
  const dry = new THREE.Color(0x9a8664), wet = new THREE.Color(0x5e5341), bed = new THREE.Color(0x3f3d31), moss = new THREE.Color(0x33402f);
  for (let i = 0; i < p.count; i++) { const x = p.getX(i), z = p.getZ(i);
    const rip = 0.025 * Math.sin(z * 3.1 + Math.sin(x * 0.7) * 2) + 0.05 * (noise1(x * 0.08 + 5) - 0.5) * (z < -5 ? 3 : 1);
    p.setY(i, rip + (z < -5 ? -0.08 : 0));
    if (z > -2.5) c.copy(dry); else if (z > -6) c.copy(dry).lerp(wet, (-2.5 - z) / 3.5); else { c.copy(wet).lerp(bed, clamp((-6 - z) / 12)); c.lerp(moss, 0.6 * noise1(x * 0.15 + z * 0.11 + 9) * clamp((-8 - z) / 10)); }
    if (z > 6) c.lerp(new THREE.Color(0x4d5236), clamp((z - 6) / 10)); // daratan berumput di belakang
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b; }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3)); g.computeVertexNormals();
  bs.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.88, metalness: 0.0 })));
}
// karang & batu di dasar laut yang terbuka
{ const R = mulberry(23); const rm = [std(0x3a3631, { flatShading: true, roughness: 0.9 }), std(0x5b4a44, { flatShading: true }), std(0x7a6a5a, { flatShading: true })];
  for (let i = 0; i < 260; i++) { const z = -7 - R() * 55, x = (R() - 0.5) * 90; const m = new THREE.Mesh(new THREE.IcosahedronGeometry(0.15 + R() * 0.55, 0), rm[Math.floor(R() * 3)]); m.position.set(x, -0.05, z); m.scale.y = 0.45 + R() * 0.4; m.rotation.set(R() * 3, R() * 3, 0); bs.add(m); } }
// laut (tepi bergerak = laut surut)
const seaMat = new THREE.MeshStandardMaterial({ color: 0x1b2a40, roughness: 0.22, metalness: 0.35 });
const sea = new THREE.Mesh(new THREE.PlaneGeometry(4000, 3000), seaMat); sea.rotation.x = -Math.PI / 2; bs.add(sea);
const foamLine = new THREE.Mesh(new THREE.PlaneGeometry(4000, 0.6), new THREE.MeshBasicMaterial({ color: 0x8fa0b8, transparent: true, opacity: 0.45 })); foamLine.rotation.x = -Math.PI / 2; bs.add(foamLine);
function setShore(z) { sea.position.set(0, 0.02, z - 1500); foamLine.position.set(0, 0.04, z); }
// ikan menggelepar
const fishes = [];
{ const R = mulberry(31); const fm = std(0xa9b8c8, { metalness: 0.65, roughness: 0.28 }), fin = std(0x6f7f94, { metalness: 0.4, roughness: 0.4 }), eyeM = std(0x0a0a10, { roughness: 0.2 });
  const spots = [[-0.35, 1.3], [0.15, 1.15], [0.55, 1.55], [-0.75, 0.75], [0.05, 0.55], [0.45, 0.25], [-0.3, -0.2], [0.9, 0.95], [-1.1, 1.6], [0.25, -0.9], [-0.7, -1.4], [1.0, -0.3]];
  for (const [x, z] of spots) { const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.SphereGeometry(1, 18, 12), fm); b.scale.set(0.2, 0.07, 0.055); g.add(b);
    const tail = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.12, 4), fin); tail.rotation.z = Math.PI / 2; tail.scale.z = 0.25; tail.position.x = -0.24; g.add(tail);
    const df = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.08, 3), fin); df.position.set(0, 0.07, 0); df.scale.z = 0.2; g.add(df);
    for (const s of [-1, 1]) { const e = new THREE.Mesh(new THREE.SphereGeometry(0.014, 8, 6), eyeM); e.position.set(0.14, 0.015, s * 0.045); g.add(e); }
    g.rotation.order = 'YXZ'; g.position.set(x, 0.06, z); g.userData = { x, z, ph: R() * 10, ry: R() * 6.28, sc: 0.85 + R() * 0.5 }; g.scale.setScalar(g.userData.sc); bs.add(g); fishes.push(g); } }
function flop(t, k = 1) { fishes.forEach((f, i) => { const d = f.userData; const n = noise1(t * 2.2 + d.ph); const jump = Math.max(0, Math.sin(t * (5 + i % 3) + d.ph)) ** 6 * k;
  f.position.set(d.x, 0.06 + 0.12 * jump, d.z); f.rotation.set(Math.PI / 2 * 0.92 + 0.35 * Math.sin(t * 9 + d.ph) * k, d.ry + 0.3 * n, 0.3 * Math.sin(t * 13 + d.ph) * k); }); }
// desa pesisir (rumah panggung), pohon kelapa, mercusuar, bukit
const palms = [];
function makePalm(R, h) { const g = new THREE.Group(); const trunkM = std(0x4a3a2a, { roughness: 0.9 }), leafM = std(0x24402a, { roughness: 0.8, side: THREE.DoubleSide });
  const lean = (R() - 0.5) * 0.3; let px = 0, py = 0; for (let k = 0; k < 6; k++) { const seg = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.2, h / 6, 8), trunkM); px += Math.sin(lean * k) * h / 6 * 0.3; seg.position.set(px, py + h / 12, 0); seg.rotation.z = -lean * k * 0.3; g.add(seg); py += h / 6; }
  for (let k = 0; k < 8; k++) { const an = k / 8 * Math.PI * 2; const piv = new THREE.Group(); piv.position.set(px, py, 0); piv.rotation.y = an; g.add(piv); const lf = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.05, 0.8), leafM); lf.position.set(1.6, -0.55, 0); lf.rotation.z = -0.35; piv.add(lf); }
  return g; }
const houses = [];
{ const R = mulberry(41); const wallM = std(0x6b5440, { roughness: 0.9 }), roofM = std(0x3a2a22, { roughness: 0.9, flatShading: true }), postM = std(0x3a2e24);
  for (let i = 0; i < 11; i++) { const g = new THREE.Group(); const w = 4 + R() * 2;
    const box = new THREE.Mesh(new THREE.BoxGeometry(w, 2.6, 3.5), wallM); box.position.y = 2.6; g.add(box);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(w * 0.8, 2.2, 4), roofM); roof.rotation.y = Math.PI / 4; roof.scale.z = 0.7; roof.position.y = 5.0; g.add(roof);
    for (const sx of [-1, 1]) for (const sz of [-1, 1]) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 1.4, 6), postM); p.position.set(sx * (w / 2 - 0.3), 0.7, sz * 1.4); g.add(p); }
    const win = new THREE.Mesh(new THREE.PlaneGeometry(0.7, 0.6), emis(0x2a2418, 0.2)); win.position.set(0, 2.7, 1.76); g.add(win);
    g.position.set(-22 - i * 8 - R() * 3, 0, 4 + R() * 10); g.rotation.y = (R() - 0.5) * 0.5; bs.add(g); houses.push(g); }
  for (let i = 0; i < 22; i++) { const p = makePalm(R, 7 + R() * 4); const side = i < 15; p.position.set(side ? -14 - i * 5.5 - R() * 3 : 14 + (i - 15) * 7, 0, side ? -1 + R() * 3 : 1 + R() * 6); p.rotation.y = R() * 6; bs.add(p); palms.push(p); } }
const lighthouse = new THREE.Group();
{ const wM = std(0xd8d8d0, { roughness: 0.6 }), rM = std(0x9a2a24, { roughness: 0.6 }); const inner = new THREE.Group(); lighthouse.add(inner); lighthouse.userData.inner = inner;
  for (let k = 0; k < 6; k++) { const seg = new THREE.Mesh(new THREE.CylinderGeometry(1.6 - k * 0.16, 1.76 - k * 0.16, 3.2, 16), k % 2 ? rM : wM); seg.position.y = 1.6 + k * 3.2; inner.add(seg); }
  const cab = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, 1.4, 12), emis(0xffe0a0, 1.4)); cab.position.y = 20.0; inner.add(cab);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(1.2, 1.4, 12), rM); cap.position.y = 21.4; inner.add(cap);
  const glow = sprite(0xffd890, 9, 0.6); glow.position.y = 20; inner.add(glow); lighthouse.userData.glow = glow;
  lighthouse.position.set(-58, 0, -14); bs.add(lighthouse); }
const hill = new THREE.Mesh(new THREE.IcosahedronGeometry(45, 3), std(0x2c3a28, { flatShading: true, roughness: 1 })); hill.position.set(45, -30, 30); bs.add(hill);
const hillY = (x, z) => Math.sqrt(Math.max(0, 2025 - (x - 45) ** 2 - (z - 30) ** 2)) - 30;
// Krakatau di seberang selat + letusan
const KX = 70, KZ = -760;
const krak = new THREE.Mesh(new THREE.ConeGeometry(70, 46, 9), std(0x161a24, { flatShading: true, roughness: 1 })); krak.position.set(KX, 18, KZ); bs.add(krak);
const lava = sprite(0xff6a20, 60, 0); lava.position.set(KX, 44, KZ); lava.material.fog = false; bs.add(lava);
const flash = sprite(0xffb060, 700, 0); flash.position.set(KX, 70, KZ); flash.material.fog = false; bs.add(flash);
const ashCol = (() => { const N = 420, pos = new Float32Array(N * 3), seeds = []; const R = mulberry(61); for (let i = 0; i < N; i++) seeds.push([R(), R(), R(), R()]);
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(g, new THREE.PointsMaterial({ map: smokeTex, color: 0x3d3a40, size: 130, transparent: true, opacity: 0, depthWrite: false, fog: false })); pts.frustumCulled = false; bs.add(pts); return { pos, seeds, pts }; })();
function setAsh(t, k) { ashCol.pts.material.opacity = 0.9 * k; ashCol.pts.visible = k > 0; if (k <= 0) return; const t0 = cs(9) + 0.1; const age0 = Math.max(0, t - t0);
  ashCol.seeds.forEach((s, i) => { const grow = clamp(age0 / 3); const h = 40 + s[0] * 380 * grow + 15 * Math.sin(t * 0.3 + i); const spread = 10 + s[0] * 160 * grow;
    ashCol.pos[i * 3] = KX + Math.cos(s[1] * 6.28) * spread * s[2] + s[0] * 120 * grow; ashCol.pos[i * 3 + 1] = h; ashCol.pos[i * 3 + 2] = KZ + Math.sin(s[1] * 6.28) * spread * s[2]; });
  ashCol.pts.geometry.attributes.position.needsUpdate = true; }
const ring = new THREE.Mesh(new THREE.RingGeometry(0.93, 1, 160), new THREE.MeshBasicMaterial({ color: 0xdfe8ff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false, fog: false }));
ring.rotation.x = -Math.PI / 2; ring.position.set(KX, 3, KZ); bs.add(ring);
const ring2 = ring.clone(); ring2.material = ring.material.clone(); bs.add(ring2);
// gelombang tsunami (dinding air)
const wave = (() => {
  const prof = new THREE.CatmullRomCurve3([[-46, 0], [-28, 0.3], [-14, 0.68], [-5, 0.93], [1, 1.0], [5.5, 0.93], [8.5, 0.76], [9, 0.62], [7.8, 0.52]].map(([z, y]) => new THREE.Vector3(0, y, z)));
  const NV = 44, NU = 140, Wd = 2400; const pp = prof.getPoints(NV - 1);
  const pos = new Float32Array(NU * NV * 3); const idx = [];
  for (let iu = 0; iu < NU; iu++) { const x = (iu / (NU - 1) - 0.5) * Wd; const hn = 0.85 + 0.3 * noise1(x * 0.012 + 3); const zn = 14 * (noise1(x * 0.006 + 11) - 0.5);
    for (let iv = 0; iv < NV; iv++) { const k = (iu * NV + iv) * 3; pos[k] = x; pos[k + 1] = pp[iv].y * hn; pos[k + 2] = pp[iv].z + zn; } }
  for (let iu = 0; iu < NU - 1; iu++) for (let iv = 0; iv < NV - 1; iv++) { const a = iu * NV + iv, b = a + NV; idx.push(a, b, a + 1, b, b + 1, a + 1); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3)); g.setIndex(idx); g.computeVertexNormals();
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0x34506e, emissive: 0x0b1828, roughness: 0.18, metalness: 0.3, side: THREE.DoubleSide })); m.frustumCulled = false;
  // buih di puncak
  const R = mulberry(71), N = 700, fp = new Float32Array(N * 3); for (let i = 0; i < N; i++) { const iu = Math.floor(R() * NU), iv = 30 + Math.floor(R() * 12); const k = (iu * NV + iv) * 3; fp[i * 3] = pos[k] + (R() - 0.5) * 18; fp[i * 3 + 1] = pos[k + 1] + (R() - 0.3) * 0.06; fp[i * 3 + 2] = pos[k + 2] + (R() - 0.5) * 3; }
  const fg = new THREE.BufferGeometry(); fg.setAttribute('position', new THREE.BufferAttribute(fp, 3));
  const foam = new THREE.Points(fg, new THREE.PointsMaterial({ map: smokeTex, color: 0xb8c6d8, size: 9, transparent: true, opacity: 0.55, depthWrite: false })); foam.frustumCulled = false; m.add(foam);
  m.visible = false; bs.add(m); return m; })();
function setWave(z, h) { wave.visible = h > 0.3; wave.position.set(0, -0.2, z); wave.scale.set(1, Math.max(h, 0.01), Math.max(h, 2) / 40); }
// siluet rombongan (tanpa wajah, jauh)
const crowd = new THREE.Group(); bs.add(crowd); const silM = std(0x0a0d18, { roughness: 1 });
function silhouette(seated) { const g = new THREE.Group(); const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.26, seated ? 0.35 : 0.85, 4, 10), silM); b.position.y = seated ? 0.45 : 0.85; g.add(b); const hd = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), silM); hd.position.y = seated ? 1.05 : 1.72; g.add(hd); g.userData.headY = hd.position.y; return g; }
{ const R = mulberry(81); [[-2.2, -2.0], [-1.4, -3.2], [-0.4, -2.6], [2.4, -3.4], [3.1, -2.2], [-3.2, -4.4]].forEach(([x, z]) => { const s = silhouette(false); s.position.set(x, 0, z); s.rotation.y = (R() - 0.5) * 1; s.scale.setScalar(0.9 + R() * 0.2); crowd.add(s); }); }
const lazy = silhouette(true); lazy.position.set(1.0, 0, -0.6); crowd.add(lazy);
const phone = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.2, 0.02), emis(0x9fd0ff, 2.2)); phone.position.set(0.05, 0.85, 0.3); phone.rotation.x = -0.6; lazy.add(phone);
const phoneGlow = sprite(0x7fb8ff, 0.9, 0.5); phoneGlow.position.copy(phone.position); lazy.add(phoneGlow);
crowd.visible = false;
// menara sirene (malam 2018)
const siren = new THREE.Group();
{ const mM = std(0x8a93a6, { metalness: 0.6, roughness: 0.4 }); const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.25, 12, 10), mM); pole.position.y = 6; siren.add(pole);
  const box = new THREE.Mesh(new THREE.BoxGeometry(1.2, 1.4, 0.8), std(0xcfd3dc)); box.position.set(0, 3.2, 0.4); siren.add(box);
  for (let k = 0; k < 4; k++) { const horn = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.15, 1.4, 14, 1, true), std(0xd9dde6, { side: THREE.DoubleSide, metalness: 0.4 })); const an = k * Math.PI / 2; horn.rotation.set(Math.PI / 2, 0, 0); horn.rotation.y = an; const hg = new THREE.Group(); hg.add(horn); horn.position.z = 0.8; hg.rotation.y = an; hg.position.y = 11.6; siren.add(hg); }
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 6), emis(0x30ff60, 1.5)); led.position.set(0, 3.5, 0.82); siren.add(led);
  siren.position.set(3, 0, -2); siren.visible = false; bs.add(siren); }
// Aru
const aru = makeAru(); aru.scale.setScalar(0.36); bs.add(aru);
// lampu
const hemi = new THREE.HemisphereLight(0x8a97b8, 0x2a2418, 1.0); bs.add(hemi);
const sun = new THREE.DirectionalLight(0xd6dcea, 1.3); sun.position.set(-40, 60, -80); bs.add(sun);
const key = new THREE.PointLight(0xffe2c4, 3.5, 8, 1.5); bs.add(key);
const boomL = new THREE.PointLight(0xff8a40, 0, 3000, 0.6); boomL.position.set(KX, 80, KZ + 100); bs.add(boomL);
function setMood(m) { // 'storm' (1883) atau 'night' (2018)
  if (m === 'night') { skyU.a.value.setHex(0x02040c); skyU.b.value.setHex(0x0a1430); skyU.c.value.setHex(0x16224a); bs.fog.color.setHex(0x0a1430); hemi.intensity = 0.45; hemi.color.setHex(0x4a5a90); sun.intensity = 0.5; sun.color.setHex(0x9fb4ff); starPts.material.opacity = 0.8; clouds.visible = false; krak.visible = false; }
  else { skyU.a.value.setHex(0x070b1c); skyU.b.value.setHex(0x26314d); skyU.c.value.setHex(0x4b5168); bs.fog.color.setHex(0x2e3650); hemi.intensity = 1.0; hemi.color.setHex(0x8a97b8); sun.intensity = 1.3; sun.color.setHex(0xd6dcea); starPts.material.opacity = 0; clouds.visible = true; krak.visible = true; }
}

// ---------- kamera ----------
const cam = new THREE.PerspectiveCamera(42, W / H, 0.05, 4000);
function look(p, tg, fov = 42, roll = 0) { cam.position.set(...p); cam.up.set(Math.sin(roll), Math.cos(roll), 0); cam.lookAt(...tg); cam.fov = fov; cam.updateProjectionMatrix(); }
const V = (a, b, u) => a.map((x, i) => lerp(x, b[i], u));
const proj = v => { const p = v.clone(); p.project(cam); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; };
const shake = (t, k) => [k * (noise1(t * 9) - 0.5), k * (noise1(t * 8 + 30) - 0.5), k * 0.5 * (noise1(t * 7 + 60) - 0.5)];
const add3 = (a, b) => a.map((x, i) => x + b[i]);

// ---------- 2D overlay ----------
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function subtitle(t) {
  if (t >= CLOSE) return;
  let c = null; for (const k of CH) if (t >= k.s && t < Math.min(k.show_end, CLOSE)) c = k; if (!c) return;
  const a = (c.s === 0 ? 1 : ramp(t, c.s, 0.08)) * (1 - ramp(t, Math.min(c.show_end, CLOSE) - 0.06, 0.06));
  let fs = 56; const txt = c.text, kw = c.kw; const i = kw ? txt.indexOf(kw) : -1;
  const parts = i < 0 ? [[txt, 0]] : [[txt.slice(0, i), 0], [kw, 1], [txt.slice(i + kw.length), 0]];
  let tw; do { ctx.font = `${fs}px PB`; tw = parts.reduce((s, [p, k]) => s + ctx.measureText(p).width + (k ? 28 : 0), 0); if (tw > 780) fs -= 2; } while (tw > 780 && fs > 36);
  let x = W / 2 - tw / 2; const y = 1475; const pop = c.s === 0 ? 1 : 1 + 0.06 * (1 - easeOut((t - c.s) / 0.15));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, y); ctx.scale(pop, pop); ctx.translate(-W / 2, -y); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  for (const [p, k] of parts) { const w = ctx.measureText(p).width;
    if (k) { ctx.fillStyle = CYEL; rr(x, y - fs * 0.68, w + 28, fs * 1.32, 12); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(p, x + 14, y + 2); x += w + 28; }
    else { ctx.shadowColor = 'rgba(0,0,0,.9)'; ctx.shadowBlur = 14; ctx.fillStyle = '#fff'; ctx.fillText(p, x, y + 2); ctx.shadowBlur = 0; x += w; } }
  ctx.restore();
}
function source(t, a, b, s) { if (t < a || t >= b) return; const al = ramp(t, a, 0.25) * (1 - ramp(t, b - 0.2, 0.2)); ctx.save(); ctx.globalAlpha = al * 0.88; let fs = 27; const str = 'Sumber: ' + s; do { ctx.font = `${fs}px PM`; if (ctx.measureText(str).width > 800) fs -= 1; else break; } while (fs > 20); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillStyle = '#dfe6f5'; ctx.fillText(str, W / 2, 1640); ctx.restore(); }
function smallText(t, a, b, s, y, f = '30px PM', col = '#e8eefc') { if (t < a || t >= b) return; const al = ramp(t, a, 0.3) * (1 - ramp(t, b - 0.25, 0.25)); ctx.save(); ctx.globalAlpha = al; ctx.font = f; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 12; ctx.fillStyle = col; ctx.fillText(s, W / 2, y); ctx.restore(); }
function tagIlustrasi(a = 1) { ctx.save(); ctx.globalAlpha = 0.8 * a; ctx.font = '24px PM'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; const w = ctx.measureText('ilustrasi').width + 28; ctx.fillStyle = 'rgba(6,10,28,.55)'; rr(140, 196, w, 40, 20); ctx.fill(); ctx.fillStyle = '#e6ecf8'; ctx.fillText('ilustrasi', 154, 217); ctx.restore(); }
function titlePill(t) { // judul layar frame 0: "Pungut ikan, atau LARI?"
  if (t > 3.6) return; const a = 1 - ramp(t, 3.25, 0.35);
  ctx.save(); ctx.globalAlpha = a; ctx.font = '54px PB'; const s1 = 'Pungut ikan, atau ', s2 = 'LARI?';
  const w1 = ctx.measureText(s1).width, w2 = ctx.measureText(s2).width; const w = w1 + w2 + 24; const x0 = W / 2 - w / 2 - 34, y0 = 292, h = 108;
  ctx.fillStyle = 'rgba(10,18,52,.84)'; rr(x0, y0, w + 68, h, 54); ctx.fill(); ctx.strokeStyle = 'rgba(18,194,176,.9)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; let x = x0 + 34; const y = y0 + h / 2 + 4;
  ctx.fillStyle = '#fff'; ctx.fillText(s1, x, y); x += w1; ctx.fillStyle = CYEL; rr(x, y0 + 16, w2 + 24, h - 32, 14); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(s2, x + 12, y);
  ctx.restore();
}
function label(x, y, num, text, col, a = 1, scale = 1, glow = 0) {
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(scale, scale); ctx.font = '34px PB'; const tw = ctx.measureText(text).width; const w = tw + 100, h = 68;
  if (glow) { ctx.shadowColor = col; ctx.shadowBlur = 40 * glow; }
  ctx.fillStyle = glow ? col : 'rgba(8,12,30,.92)'; rr(-w / 2, -h / 2, w, h, 14); ctx.fill(); ctx.shadowBlur = 0; ctx.strokeStyle = glow ? '#fff' : 'rgba(255,255,255,.55)'; ctx.lineWidth = 2.5; ctx.stroke();
  ctx.fillStyle = glow ? CNAVY : col; ctx.beginPath(); ctx.arc(-w / 2 + 38, 0, 21, 0, 7); ctx.fill(); ctx.fillStyle = glow ? col : CNAVY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '28px PB'; ctx.fillText(num, -w / 2 + 38, 2);
  ctx.fillStyle = glow ? CNAVY : '#fff'; ctx.font = '34px PB'; ctx.textAlign = 'left'; ctx.fillText(text, -w / 2 + 72, 2); ctx.restore();
}
function badge(x, y, text, bg, fg, a, f = '32px PB') { ctx.save(); ctx.globalAlpha = a; ctx.font = f; const w = ctx.measureText(text).width + 48; ctx.fillStyle = bg; rr(x - w / 2, y - 32, w, 64, 32); ctx.fill(); ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, x, y + 2); ctx.restore(); }
function wrapPill(t, a, b, lines, y, f = '32px PB') { if (t < a || t >= b) return; const al = ramp(t, a, 0.25) * (1 - ramp(t, b - 0.25, 0.25)); const pop = 1 + 0.06 * (1 - easeOut((t - a) / 0.2));
  ctx.save(); ctx.globalAlpha = al; ctx.font = `${f}, ${EMO}`; const lh = 46; const w = Math.min(800, Math.max(...lines.map(s => ctx.measureText(s).width)) + 64); const h = lines.length * lh + 34;
  ctx.translate(W / 2, y); ctx.scale(pop, pop); ctx.fillStyle = 'rgba(255,184,0,.96)'; rr(-w / 2, -h / 2, w, h, 26); ctx.fill(); ctx.fillStyle = CNAVY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  lines.forEach((s, i) => ctx.fillText(s, 0, -h / 2 + 17 + lh / 2 + i * lh + 2)); ctx.restore(); }
function follow(t) { if (t < 10 || t >= 15) return; const a = ramp(t, 10, 0.3) * (1 - ramp(t, 14.7, 0.3)); ctx.save(); ctx.globalAlpha = a * 0.92; ctx.font = '25px PM'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillStyle = '#e8eefc'; ctx.fillText('Follow, besok: trik bikin minuman kaleng dingin tanpa nunggu kulkas', W / 2, 1725); ctx.restore(); }
function bigNum(text, unit, y, a, col = CYEL, fs = 150) { ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = `${fs}px PB`; ctx.fillStyle = col; ctx.shadowColor = 'rgba(0,0,0,.8)'; ctx.shadowBlur = 30; ctx.fillText(text, W / 2, y); ctx.shadowBlur = 0; if (unit) { ctx.font = '44px PB'; ctx.fillStyle = '#fff'; ctx.shadowColor = '#000'; ctx.shadowBlur = 12; ctx.fillText(unit, W / 2, y + fs * 0.62); } ctx.restore(); }
function bubble(x, y, text, a) { ctx.save(); ctx.globalAlpha = a; ctx.font = 'italic 34px PB'; const w = ctx.measureText(text).width + 56, h = 76; const bx = clamp(x - w / 2, 140, W - 140 - w), by = y - h - 40;
  ctx.fillStyle = '#f4f6fb'; rr(bx, by, w, h, 30); ctx.fill(); ctx.beginPath(); ctx.moveTo(clamp(x, bx + 40, bx + w - 40) - 16, by + h - 2); ctx.lineTo(x, y - 8); ctx.lineTo(clamp(x, bx + 40, bx + w - 40) + 16, by + h - 2); ctx.fill();
  ctx.fillStyle = CNAVY; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, bx + w / 2, by + h / 2 + 2); ctx.restore(); }
function ruler(t, a, hFrac, label40) { // penggaris vertikal kanan
  ctx.save(); ctx.globalAlpha = a; const x = 900, yb = 1180, yt = 520; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(x, yb); ctx.lineTo(x, yt); ctx.stroke();
  ctx.font = '22px PM'; ctx.fillStyle = '#e6ecf8'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
  for (let m = 0; m <= 40; m += 5) { const y = lerp(yb, yt, m / 40); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - (m % 10 ? 14 : 26), y); ctx.stroke(); if (m % 10 === 0) ctx.fillText(m + ' m', x - 34, y); }
  const yh = lerp(yb, yt, hFrac); ctx.fillStyle = CYEL; ctx.beginPath(); ctx.moveTo(x + 6, yh); ctx.lineTo(x + 30, yh - 14); ctx.lineTo(x + 30, yh + 14); ctx.fill();
  ctx.restore(); }
function seismo(t, a) { ctx.save(); ctx.globalAlpha = a; const x = 140, y = 1110, w = 800, h = 220; ctx.fillStyle = 'rgba(4,8,22,.86)'; rr(x, y, w, h, 22); ctx.fill(); ctx.strokeStyle = 'rgba(120,170,255,.55)'; ctx.lineWidth = 2.5; ctx.stroke();
  ctx.font = '24px PB'; ctx.fillStyle = '#cfe0ff'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText('SEISMOGRAF', x + 26, y + 34); ctx.font = '22px PM'; ctx.fillStyle = 'rgba(200,215,255,.7)'; ctx.textAlign = 'right'; ctx.fillText('ilustrasi', x + w - 26, y + 34);
  ctx.strokeStyle = 'rgba(120,170,255,.15)'; ctx.lineWidth = 1.5; for (let k = 1; k < 4; k++) { ctx.beginPath(); ctx.moveTo(x + 20, y + 60 + k * 36); ctx.lineTo(x + w - 20, y + 60 + k * 36); ctx.stroke(); }
  ctx.strokeStyle = '#2ee88a'; ctx.lineWidth = 4; ctx.shadowColor = '#2ee88a'; ctx.shadowBlur = 10; ctx.beginPath(); const yc = y + 150;
  for (let px = 0; px <= w - 60; px += 4) { const tt = t * 60 - px * 0.3; const v = 2.5 * (noise1(tt * 0.3) - 0.5); px ? ctx.lineTo(x + 30 + px, yc + v) : ctx.moveTo(x + 30, yc + v); } ctx.stroke(); ctx.shadowBlur = 0;
  ctx.fillStyle = '#2ee88a'; ctx.beginPath(); ctx.arc(x + w - 30, yc, 7, 0, 7); ctx.fill(); ctx.restore(); }
function stopwatch(t, a, t0) { ctx.save(); ctx.globalAlpha = a; const cx = W / 2, cy = 820, R = 240; const el = Math.max(0, t - t0);
  ctx.fillStyle = 'rgba(4,8,22,.88)'; ctx.beginPath(); ctx.arc(cx, cy, R + 24, 0, 7); ctx.fill(); ctx.fillStyle = '#cfd6e6'; rr(cx - 34, cy - R - 74, 68, 46, 10); ctx.fill(); rr(cx - 14, cy - R - 34, 28, 22, 4); ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,.18)'; ctx.lineWidth = 18; ctx.beginPath(); ctx.arc(cx, cy, R, 0, 7); ctx.stroke();
  const frac = clamp(1 - el / 4.2); ctx.strokeStyle = CYEL; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(cx, cy, R, -Math.PI / 2, -Math.PI / 2 + frac * Math.PI * 2); ctx.stroke(); ctx.lineCap = 'butt';
  ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 4; for (let k = 0; k < 60; k += 5) { const an = k / 60 * Math.PI * 2; ctx.beginPath(); ctx.moveTo(cx + Math.sin(an) * (R - 34), cy - Math.cos(an) * (R - 34)); ctx.lineTo(cx + Math.sin(an) * (R - 52), cy - Math.cos(an) * (R - 52)); ctx.stroke(); }
  const an = el * 2.4; ctx.strokeStyle = '#ff5a48'; ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.sin(an) * (R - 60), cy - Math.cos(an) * (R - 60)); ctx.stroke(); ctx.fillStyle = '#ff5a48'; ctx.beginPath(); ctx.arc(cx, cy, 12, 0, 7); ctx.fill();
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; const s = Math.max(0, 300 - Math.floor(el * 24)); ctx.font = '40px PB'; ctx.fillStyle = 'rgba(255,255,255,.85)'; ctx.fillText(`0${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`, cx, cy + 110);
  ctx.restore(); }
function saveCard(t, a) { // KARTU LAYAK SIMPAN (PRB-62)
  ctx.save(); ctx.globalAlpha = a; const x = 140, y = 360, w = 800, h = 930; const pop = 1 + 0.04 * (1 - easeOut((t - cs(37)) / 0.25)); ctx.translate(W / 2, y + h / 2); ctx.scale(pop, pop); ctx.translate(-W / 2, -(y + h / 2));
  ctx.fillStyle = 'rgba(244,246,251,.97)'; rr(x, y, w, h, 34); ctx.fill(); ctx.fillStyle = CNAVY; rr(x, y, w, 128, [34, 34, 0, 0]); ctx.fill();
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.font = '46px PB'; ctx.fillStyle = '#fff'; ctx.fillText('TANDA TSUNAMI', x + 44, y + 66); ctx.font = '30px PB'; ctx.fillStyle = CYEL; ctx.fillText('(BMKG)', x + 44 + ctx.measureText('TANDA TSUNAMI').width * 46 / 30 + 18, y + 68);
  const items = [['Gempa sangat kuat', 'atau lama (±1 menit)'], ['Laut surut tiba-tiba,', 'ikan/karang terlihat'], ['Dentuman keras', 'dari laut']];
  items.forEach(([l1, l2], i) => { const yy = y + 200 + i * 168; const ai = ramp(t, cs(37) + 0.25 + i * 0.35, 0.25); ctx.globalAlpha = a * ai;
    ctx.fillStyle = CTEAL; ctx.beginPath(); ctx.arc(x + 80, yy + 30, 38, 0, 7); ctx.fill(); ctx.fillStyle = CNAVY; ctx.textAlign = 'center'; ctx.font = '40px PB'; ctx.fillText(String(i + 1), x + 80, yy + 33);
    ctx.textAlign = 'left'; ctx.font = '40px PB'; ctx.fillStyle = CNAVY; ctx.fillText(l1, x + 146, yy + 8); ctx.font = '34px PM'; ctx.fillStyle = '#3b4670'; ctx.fillText(l2, x + 146, yy + 56); });
  const ab = ramp(t, cs(38), 0.3); ctx.globalAlpha = a * ab; ctx.fillStyle = CYEL; rr(x + 40, y + 700, w - 80, 128, 24); ctx.fill(); ctx.fillStyle = CNAVY; ctx.textAlign = 'center'; ctx.font = '38px PB'; ctx.fillText('→ Langsung ke tempat tinggi.', W / 2, y + 742); ctx.font = '32px PM'; ctx.fillText('Jangan tunggu sirene.', W / 2, y + 790);
  ctx.globalAlpha = a * ramp(t, cs(39), 0.3); ctx.font = `30px PB, ${EMO}`; ctx.fillStyle = '#3b4670'; ctx.fillText('simpan sebelum liburan 📌', W / 2, y + 885);
  ctx.restore(); }

// ---------- frame ----------
function sceneOf(t) { let k = 0; for (let i = 0; i < SC.length; i++) if (t >= SC[i]) k = i; return k; }
const AR0 = [1.6, 0, -2.4]; // posisi Aru di pantai (frame 0)

window.renderFrame = function (t) {
  const k = sceneOf(t); const t0 = SC[k], t1 = k + 1 < SC.length ? SC[k + 1] : TOTAL; const lt = t - t0, u = clamp(lt / (t1 - t0));
  let render3d = true; const post = { dark: 0, flash: 0 };
  // default dunia
  setMood('storm'); setShore(-52); setWave(0, 0); crowd.visible = false; siren.visible = false; aru.visible = true;
  lava.material.opacity = 0; flash.material.opacity = 0; boomL.intensity = 0; ring.material.opacity = 0; ring2.material.opacity = 0; setAsh(t, t > cs(9) ? 1 : 0);
  if (t > cs(9)) lava.material.opacity = 0.75 + 0.25 * noise1(t * 4);
  lighthouse.userData.inner.rotation.set(0, 0, 0); palms.forEach(p => { p.rotation.x = 0; p.rotation.z = 0; }); houses.forEach(h => h.visible = true);
  aru.position.set(...AR0); aru.rotation.set(0, -1.15, 0); aruPose(aru, { lean: 0.85, armX: 0.5, armZ: 0.1, hx: 0.2, t });
  key.position.set(0.3, 1.6, 2.2); key.intensity = 3.5;
  flop(t, 1);

  if (k === 0) { // HOOK POV: pasir basah, ikan di depan kamera, Aru mau memungut ikan; dtk ~1,5 kamera naik
    setShore(lerp(-40, -52, ease(t / 3.7)));
    const e = ease((t - 1.35) / 1.6);
    const p0 = [-0.05, 0.95, 2.9], p1 = [-0.15, 1.75, 3.35]; const g0 = [0.35, 0.3, -0.6], g1 = [0.1, 0.35, -18];
    look(add3(V(p0, p1, e), shake(t, 0.008)), V(g0, g1, e), lerp(52, 46, e));
  } else if (k === 1) { // kartu pilihan
    const e = ease(u); look([lerp(-0.9, -1.1, e), lerp(1.15, 1.05, e), lerp(2.6, 2.3, e)], [0.1, 0.35, -0.6], 48);
    aruPose(aru, { lean: 0.35, armX: 0.2, hx: 0.1, hy: lerp(0.0, 0.7, ease((t - cs(4)) / 0.6)), t });
  } else if (k === 2) { // Anyer 1883: desa & mercusuar di kejauhan
    const e = ease(u); look([lerp(10, 7, e), lerp(7, 7.8, e), lerp(26, 23, e)], [-48, lerp(2, 3, e), -4], 44);
    aruPose(aru, { lean: 0.1, hy: 0.6, t }); aru.rotation.y = -0.4;
  } else if (k === 3) { // Krakatau meledak di seberang selat
    const tb = cs(9) + 0.05; const fl = t > tb ? Math.exp(-(t - tb) * 2.2) : 0;
    flash.material.opacity = fl; boomL.intensity = 6 * fl; post.flash = 0.35 * fl * (t - tb < 0.25 ? 1 : 0.4);
    if (t < cs(10) - 0.1) { const e = ease((t - SC[3]) / (cs(10) - SC[3])); const sk = t > tb + 0.25 ? shake(t, 0.18 * Math.exp(-(t - tb - 0.25) * 0.8)) : [0, 0, 0];
      look(add3([lerp(-1.2, -1.0, e), 1.6, lerp(3.6, 3.1, e)], sk), [KX * 0.9, lerp(25, 45, e), KZ], 34);
      aruPose(aru, { lean: -0.05, hy: 0.25, armX: -0.3, t }); aru.rotation.y = -2.7; }
    else { // gelombang kejut melintasi selat
      const e = ease((t - cs(10)) / (SC[4] - cs(10))); const age = t - tb;
      const r1 = 40 + age * 180, r2 = Math.max(1, 20 + (age - 0.8) * 180); ring.scale.setScalar(r1); ring2.scale.setScalar(r2); ring.material.opacity = 0.75 * clamp(1 - age / 7); ring2.material.opacity = age > 0.8 ? 0.45 * clamp(1 - age / 7) : 0;
      look(add3([lerp(-30, -24, e), lerp(26, 30, e), lerp(40, 34, e)], shake(t, 0.25)), [KX * 0.55, 0, KZ * 0.55], 44);
      aruPose(aru, { lean: -0.05, hy: 0.25, t }); aru.rotation.y = -2.7; }
  } else if (k === 4) { // menoleh dari letusan ke laut
    const e = ease((t - SC[4] - 0.3) / 2.2); const tg = V([KX * 0.9, 45, KZ], [0, 6, -400], e);
    look([-1.0, 1.6, 3.1], tg, lerp(34, 44, e)); aruPose(aru, { lean: -0.05, hy: lerp(0.25, 0, e), t }); aru.rotation.y = lerp(-2.7, -3.14, e);
  } else if (k === 5) { // dinding air di cakrawala
    const hh = lerp(4, 40, ease((t - cs(15) - 0.2) / 3.2)); const wz = lerp(-260, -160, u); setWave(wz, hh); setShore(-52);
    const e = ease(u); look(add3([0, lerp(1.6, 1.4, e), lerp(3.2, 3.6, e)], shake(t, 0.02 + 0.05 * e)), [0, lerp(8, 16, e), -160], lerp(48, 52, e));
    aru.visible = false;
  } else if (k === 6) { // mercusuar & kelapa tersapu (benda, tanpa orang)
    const wz = lerp(-120, 2, ease(u * 1.05)); setWave(wz, 26); setShore(-52);
    const hitZ = lighthouse.position.z; const front = wz + 8 * 26 / 40; const hit = clamp((front - hitZ) / 14);
    lighthouse.userData.inner.rotation.set(-0.0, 0, 1.35 * ease(hit)); lighthouse.userData.inner.position.z = 4 * ease(hit);
    palms.forEach(p => { const ph = clamp((front - p.position.z) / 6); p.rotation.x = 1.3 * ease(ph); });
    houses.forEach(h => { h.visible = front < h.position.z - 2; });
    const e = ease(u); look(add3([lerp(-18, -20, e), lerp(9, 10, e), lerp(34, 38, e)], shake(t, 0.12)), [-52, 8, -16], 50);
    aru.visible = false;
  } else if (k === 7) { // PUNCAK: LARI. Aru berbalik dan lari ke bukit; lalu ikan di dasar laut = tanda tsunami
    setShore(-52);
    if (t < cs(21)) { const tr = cs(20) + 0.15; const turn = ease((t - tr) / 0.35); const run = Math.max(0, t - tr - 0.3);
      aru.rotation.y = lerp(-1.15, 0.75, turn); const dir = [Math.sin(0.75), 0, Math.cos(0.75)];
      aru.position.set(AR0[0] + dir[0] * run * 2.6, 0, AR0[2] + dir[2] * run * 2.6);
      aruPose(aru, { lean: lerp(0.55, 0.25, turn), swing: run > 0 ? 0.9 * Math.sin(run * 14) : 0, bob: run > 0 ? 0.12 * Math.abs(Math.sin(run * 14)) : 0, hy: 0, t });
      const e = ease(u * 1.2); look([lerp(-0.6, -0.9, e), lerp(1.5, 1.7, e), lerp(3.6, 4.4, e)], [lerp(0.9, 2.2, e), 0.5, 0], 50);
    } else { const e = ease((t - cs(21)) / (SC[8] - cs(21))); aru.visible = false;
      look([lerp(0.35, 0.1, e), lerp(0.32, 0.5, e), lerp(2.3, 1.7, e)], [lerp(-0.2, 0, e), 0.15, -30], 50); }
  } else if (k === 8) { // rombongan siluet; satu orang santai pegang HP
    crowd.visible = true; aru.visible = false; setShore(-52);
    key.intensity = 0.6; const e = ease(u); look([lerp(7.5, 7.0, e), lerp(2.3, 2.1, e), lerp(12, 11, e)], [0.2, 0.9, -2.2], 40);
    lazy.rotation.y = 0.5; phoneGlow.material.opacity = 0.4 + 0.15 * noise1(t * 3);
  } else if (k === 9) { // malam Selat Sunda 2018: sirene diam, tanpa gempa
    setMood('night'); setShore(-7); siren.visible = true; aru.visible = false; fishes.forEach(f => f.visible = false); houses.forEach(h => h.visible = false); lighthouse.visible = false;
    key.intensity = 0;
    const e = ease(u); look([lerp(-4.5, -4.0, e), lerp(1.4, 1.6, e), lerp(9, 8, e)], [2.5, lerp(5, 6.5, e), -3], 46);
  } else if (k === 10) { // waktu emas < 5 menit
    setMood('night'); setShore(-7); siren.visible = true; aru.visible = false; fishes.forEach(f => f.visible = false); houses.forEach(h => h.visible = false); lighthouse.visible = false; key.intensity = 0;
    look([-6, 2.2, 12], [0, 3, -60], 46); post.dark = 0.45;
  } else if (k === 11 || k === 12) { // Aru di bukit menunjuk ke laut; kartu layak simpan; penutup
    setShore(lerp(-52, -56, u)); const ax = 38, az = 25; aru.position.set(ax, hillY(ax, az) - 0.05, az); aru.rotation.y = Math.PI + 0.45;
    aruPose(aru, { point: true, hx: 0.1, hy: 0, t });
    const hy = hillY(ax, az); key.position.set(40, hy + 2.5, 29); key.intensity = 4;
    if (k === 11 && t < cs(37)) { const e = ease((t - SC[11]) / (cs(37) - SC[11])); look([lerp(41, 40.6, e), hy + 1.2, lerp(30, 29.2, e)], [35.5, hy - 0.8, 18], 46); }
    else if (k === 11) { const e = ease((t - cs(37)) / (SC[12] - cs(37))); look([lerp(42, 43, e), hy + 2, lerp(32, 34, e)], [34, hy - 2, 12], 46); post.dark = 0.35 * ramp(t, cs(37), 0.3); }
    else { const e = ease(u); look([lerp(43, 44.5, e), hy + lerp(2.4, 3, e), lerp(33, 35.5, e)], [34, hy - 1.5, 13], 44); post.dark = 0.15; }
  } else { render3d = false; }
  if (k !== 9 && k !== 10) { fishes.forEach(f => f.visible = true); lighthouse.visible = true; }

  // ---- render 3D ----
  if (render3d) {
    renderer.render(bs, cam); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over'; ctx.drawImage(glc, 0, 0);
    sctx.filter = 'brightness(0.7) contrast(2.2) blur(5px)'; sctx.clearRect(0, 0, 180, 320); sctx.drawImage(glc, 0, 0, 180, 320); sctx.filter = 'none';
    ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.45; ctx.drawImage(small, 0, 0, W, H); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  } else { ctx.fillStyle = '#050a1c'; ctx.fillRect(0, 0, W, H); }
  if (post.dark) { ctx.fillStyle = `rgba(2,4,14,${post.dark})`; ctx.fillRect(0, 0, W, H); }
  const vg = ctx.createRadialGradient(W / 2, H * 0.48, H * 0.25, W / 2, H * 0.5, H * 0.75); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,8,.7)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  const bg = ctx.createLinearGradient(0, 1250, 0, 1920); bg.addColorStop(0, 'rgba(0,0,10,0)'); bg.addColorStop(1, 'rgba(0,0,10,.62)'); ctx.fillStyle = bg; ctx.fillRect(0, 1250, W, 670);

  // ---- grafik per adegan ----
  if (render3d) tagIlustrasi();
  if (k === 0) { titlePill(t); if (t >= 1.9) { const a = ramp(t, 1.9, 0.2); const y = Math.round(lerp(2026, 1883, easeOut((t - 2.0) / 1.2))); ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '40px PB'; ctx.fillStyle = 'rgba(255,255,255,.8)'; ctx.shadowColor = '#000'; ctx.shadowBlur = 12; ctx.fillText('2026  →', W / 2 - 120, 500); ctx.font = '92px PB'; ctx.fillStyle = CYEL; ctx.fillText(String(y), W / 2 + 90, 494); ctx.restore(); } }
  if (k === 1) { const blink = Math.floor((t - SC[1]) / 0.55) % 2; const a = ramp(t, SC[1], 0.25); const bob = Math.sin(t * 2) * 8;
    label(W / 2, 520 + bob, '1', 'PUNGUT IKAN', CTEAL, a * (blink === 0 ? 1 : 0.45), blink === 0 ? 1.12 : 1);
    label(W / 2, 640 - bob, '2', 'LARI', CYEL, a * (blink === 1 ? 1 : 0.45), blink === 1 ? 1.12 : 1);
    ctx.save(); ctx.globalAlpha = ramp(t, SC[1], 0.25) * 0.85; ctx.font = '26px PM'; ctx.textAlign = 'center'; ctx.fillStyle = '#e8eefc'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillText('kamu pilih apa?', W / 2, 430); ctx.restore(); }
  if (k === 2) { const a = ramp(t, cs(6), 0.3); ctx.save(); ctx.globalAlpha = a; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 16; ctx.font = '60px PB'; ctx.fillStyle = '#fff'; ctx.fillText('Anyer', W / 2, 420); ctx.font = '46px PB'; ctx.fillStyle = CYEL; ctx.fillText('27 Agustus 1883', W / 2, 492); ctx.restore(); }
  if (k === 3) { if (t >= cs(11)) { const p = easeOut((t - cs(11)) / 1.3); bigNum(fmt(Math.round(4800 * p / 10) * 10), 'km, dentuman terdengar', 470, ramp(t, cs(11), 0.15)); }
    source(t, cs(11), SC[4], 'Metro TV News, 26 Agu 2025'); }
  if (k === 4) { if (t >= cs(14)) { const p = easeOut((t - cs(14)) / 0.3); ctx.save(); ctx.globalAlpha = ramp(t, cs(14), 0.1); ctx.translate(W / 2, 760); ctx.scale(0.6 + 0.4 * p, 0.6 + 0.4 * p); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.font = '380px PB'; ctx.fillStyle = CYEL; ctx.shadowColor = 'rgba(255,184,0,.6)'; ctx.shadowBlur = 50; ctx.fillText('?', 0, 0); ctx.restore(); } }
  if (k === 5) { const a = ramp(t, cs(16), 0.3); if (a > 0) { const hf = clamp(lerp(0, 1, easeOut((t - cs(16)) / 2.0))); ruler(t, a, hf); }
    if (t >= cs(17)) bigNum('± ' + Math.round(40 * easeOut((t - cs(17)) / 0.9)) + ' m', 'tinggi gelombang', 440, ramp(t, cs(17), 0.15), CYEL, 130);
    source(t, cs(17), SC[6], 'NOAA NCEI, 26 Agu 2017 (±41 m di Banten)'); }
  if (k === 6) { if (t >= cs(19)) { ctx.save(); ctx.globalAlpha = ramp(t, cs(19), 0.4); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 14; ctx.font = '72px PB'; ctx.fillStyle = '#fff'; ctx.fillText('> 34.000 jiwa', W / 2, 450); ctx.restore(); }
    source(t, cs(19), SC[7], 'NOAA NCEI, 26 Agu 2017'); }
  if (k === 7) {
    if (t < cs(21)) { const g = ramp(t, cs(20), 0.15); label(W / 2, 900, "2", "LARI", CYEL, g, 1.6 + 0.12 * (1 - easeOut((t - cs(20)) / 0.3)), 1); }
    else { badge(W / 2, 640, 'tanda tsunami', CYEL, CNAVY, ramp(t, cs(23) - 0.2, 0.2), '40px PB'); source(t, cs(23) - 0.2, SC[8], 'Petunjuk Keselamatan Gempabumi & Tsunami, BMKG'); }
    wrapPill(t, cs(20), SC[8] - 0.05, ['Kirim ke keluarga yang liburan', 'akhir tahun ke pantai 📤'], 400, '32px PB'); }
  if (k === 8) { if (t >= cs(27) - 0.1) { const hp = new THREE.Vector3(); lazy.localToWorld(hp.set(0, lazy.userData.headY + 0.3, 0)); const [x, y] = proj(hp); bubble(x, y, 'santai, nanti ada sirene', ramp(t, cs(27) - 0.1, 0.2)); } }
  if (k === 9) { seismo(t, ramp(t, SC[9], 0.3)); smallText(t, cs(30) - 0.1, SC[10], '22 Des 2018 · tanpa gempa', 420, '52px PB', '#fff');
    if (t < cs(32) + 0.3) source(t, cs(30) - 0.1, cs(32) + 0.3, 'siaran pers BMKG, 22 Des 2018');
    else { smallText(t, cs(32) + 0.3, SC[10], '437 meninggal', 510, '44px PB', '#e6ecf8'); source(t, cs(32) + 0.3, SC[10], 'BNPB via Tempo, 31 Des 2018'); } }
  if (k === 10) { stopwatch(t, ramp(t, SC[10], 0.25), SC[10]); if (t >= cs(35) - 0.1) bigNum('< 5 menit', 'waktu emas evakuasi', 1150, ramp(t, cs(35) - 0.1, 0.15), CYEL, 96); source(t, SC[10] + 0.2, SC[11], 'BMKG, 26 Mar 2019'); }
  if (k === 11) { if (t >= cs(37)) { saveCard(t, ramp(t, cs(37), 0.2)); source(t, cs(37), SC[12], 'Petunjuk Keselamatan Gempabumi & Tsunami BMKG; BMKG 26 Mar 2019'); } }
  if (k === 12) { wrapPill(t, SC[12] + 0.1, CLOSE + 0.01, ['Tim LARI atau tim TUNGGU?', 'Komen satu kata!'], 560, '38px PB'); }
  if (k === 13) { const a = ramp(t, CLOSE, 0.2); ctx.save(); ctx.globalAlpha = a; const lw = 280, lh = lw * logo.height / logo.width; ctx.drawImage(logo, W / 2 - lw / 2, 800, lw, lh); ctx.restore();
    ctx.save(); ctx.globalAlpha = a * 0.9; ctx.font = '34px PB'; ctx.textAlign = 'center'; ctx.fillStyle = '#fff'; ctx.fillText('Tim LARI atau tim TUNGGU?', W / 2, 800 + lh + 90); ctx.restore(); }
  follow(t);
  subtitle(t);
  if (k > 0 && lt < 0.12) { ctx.fillStyle = `rgba(2,4,12,${0.6 * (1 - lt / 0.12)})`; ctx.fillRect(0, 0, W, H); }
  for (const cut of [cs(10), cs(21), cs(37)]) if (t >= cut && t - cut < 0.1) { ctx.fillStyle = `rgba(2,4,12,${0.5 * (1 - (t - cut) / 0.1)})`; ctx.fillRect(0, 0, W, H); }
  if (post.flash) { ctx.fillStyle = `rgba(255,220,180,${post.flash})`; ctx.fillRect(0, 0, W, H); }
};
window.READY = true;
