// ARN-58 "Anak kunci, kok PILIH-PILIH?" — format 3D bongkar (exploded view silinder kunci pin tumbler).
// three.js r160 lokal. Deterministik: window.renderFrame(t) menggambar frame waktu t (detik) ke <canvas id="out"> 1080x1920.
// Catatan konten: hanya cara kerja kunci benar vs kunci salah (macet). Tidak ada cara membobol/mencungkil kunci.
import * as THREE from './three.module.js';

const W = 1080, H = 1920;
const NAVY = 0x14215B, TEAL = 0x12C2B0, YEL = 0xFFB800, ORG = 0xFF7A1A;
const CNAVY = '#14215B', CTEAL = '#12C2B0', CYEL = '#FFB800', CRED = '#FF4B3E';
const T = await (await fetch('timing.json')).json();
const CH = T.chunks, SC = T.scenes, TOTAL = T.total;
const cs = i => CH[i].s;
const CLOSE = SC[10];
const CUT_B = cs(18) - 0.15;            // potongan kamera di adegan 5 (kunci salah)

// ---------- util ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, u) => a + (b - a) * u;
const ease = u => { u = clamp(u); return u * u * (3 - 2 * u); };
const easeOut = u => { u = clamp(u); return 1 - Math.pow(1 - u, 3); };
const easeBack = u => { u = clamp(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
const ramp = (t, a, d = 0.3) => ease((t - a) / d);
const hash = n => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
function mulberry(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }

// ---------- renderer ----------
const glc = document.createElement('canvas'); glc.width = W; glc.height = H;
const renderer = new THREE.WebGLRenderer({ canvas: glc, antialias: true, alpha: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1); renderer.setSize(W, H, false); renderer.setClearColor(0x000000, 0);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.1;
const out = document.getElementById('out'); const ctx = out.getContext('2d');
const small = document.createElement('canvas'); small.width = 180; small.height = 320; const sctx = small.getContext('2d');

await Promise.all([
  new FontFace('PB', 'url(Poppins-Bold.ttf)').load().then(f => document.fonts.add(f)),
  new FontFace('PM', 'url(Poppins-Medium.ttf)').load().then(f => document.fonts.add(f)),
]);
const logo = new Image(); logo.src = 'arunika-logo-putih.png'; await logo.decode();

function canvasTex(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; }
const softTex = canvasTex(128, 128, (g, w, h) => { const r = g.createRadialGradient(64, 64, 0, 64, 64, 64); r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(0.3, 'rgba(255,255,255,.5)'); r.addColorStop(1, 'rgba(255,255,255,0)'); g.fillStyle = r; g.fillRect(0, 0, w, h); });
const woodTex = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#8a5a2c'; g.fillRect(0, 0, w, h); const R = mulberry(9); for (let i = 0; i < 70; i++) { const y = R() * h; g.strokeStyle = `rgba(${50 + R() * 40},${28 + R() * 20},10,${0.25 + R() * 0.35})`; g.lineWidth = 1 + R() * 3; g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 16) g.lineTo(x, y + 4 * Math.sin(x * 0.03 + i)); g.stroke(); } });

// ---------- lingkungan (env map untuk logam) ----------
const pm = new THREE.PMREMGenerator(renderer);
const envS = new THREE.Scene();
envS.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.ShaderMaterial({ side: THREE.BackSide,
  vertexShader: 'varying vec3 vp; void main(){ vp = normalize(position); gl_Position = projectionMatrix*modelViewMatrix*vec4(position,1.); }',
  fragmentShader: 'varying vec3 vp; void main(){ float h = vp.y*.5+.5; vec3 c = mix(vec3(.02,.025,.035), vec3(.42,.48,.58), pow(h,1.4)); gl_FragColor = vec4(c,1.); }' })));
for (const [p, s, c, k] of [[[0, 30, 12], [34, 14], 0xffffff, 3.2], [[32, 6, 4], [5, 30], 0xffe2bc, 2.6], [[-32, 4, 6], [5, 30], 0xa8c4ff, 2.2], [[0, -6, -32], [36, 8], 0xff8a3a, 1.6], [[10, 12, 30], [10, 6], 0xffffff, 2.0]]) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(...s), new THREE.MeshBasicMaterial({ color: new THREE.Color(c).multiplyScalar(k), side: THREE.DoubleSide })); m.position.set(...p); m.lookAt(0, 0, 0); envS.add(m);
}
const envTex = pm.fromScene(envS, 0.03).texture;

// ---------- stage ----------
const stage = new THREE.Scene(); stage.environment = envTex; stage.fog = new THREE.Fog(0x141a26, 16, 46);
stage.add(new THREE.HemisphereLight(0xbcd0ff, 0x1a1f2a, 0.55));
const keyL = new THREE.DirectionalLight(0xfff0dc, 1.7); keyL.position.set(4, 8, 7); stage.add(keyL);
const rimL = new THREE.DirectionalLight(0x9cc0ff, 1.3); rimL.position.set(-6, 3, -6); stage.add(rimL);
const orgL = new THREE.PointLight(ORG, 9, 9, 1.4); stage.add(orgL);
const FLOOR = -4.6;
const grid = new THREE.GridHelper(80, 64, 0x6f88b0, 0x3b4c6c); grid.position.y = FLOOR; grid.material.transparent = true; grid.material.opacity = 0.5; stage.add(grid);
function makeFloorRing() {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(new THREE.RingGeometry(1.55, 1.75, 96), new THREE.MeshBasicMaterial({ color: new THREE.Color(ORG).multiplyScalar(1.6), transparent: true, opacity: 0.95, side: THREE.DoubleSide, depthWrite: false }));
  ring.rotation.x = -Math.PI / 2; g.add(ring);
  const disc = new THREE.Mesh(new THREE.PlaneGeometry(5.2, 5.2), new THREE.MeshBasicMaterial({ map: softTex, color: ORG, transparent: true, opacity: 0.55, blending: THREE.AdditiveBlending, depthWrite: false }));
  disc.rotation.x = -Math.PI / 2; disc.position.y = 0.01; g.add(disc);
  const sh = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 2.6), new THREE.MeshBasicMaterial({ map: softTex, color: 0x000000, transparent: true, opacity: 0.55, depthWrite: false }));
  sh.rotation.x = -Math.PI / 2; sh.position.y = 0.02; g.add(sh);
  g.userData = { ring, disc }; stage.add(g); return g;
}
const ringA = makeFloorRing(), ringB = makeFloorRing();

// ---------- material ----------
const metal = (color, rough, o = {}) => new THREE.MeshStandardMaterial({ color, metalness: 1, roughness: rough, envMapIntensity: 1.25, ...o });
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0, ...o });
const M = {
  brass: metal(0xc9962e, 0.32), brassL: metal(0xe0b354, 0.26), chrome: metal(0xe4e8ee, 0.15), steel: metal(0xb3bac4, 0.28), nickel: metal(0xd6d2c6, 0.22),
  dark: std(0x07090d, { roughness: 0.5 }), navy: std(NAVY, { roughness: 0.75 }), teal: std(TEAL, { roughness: 0.5 }), yel: std(YEL, { roughness: 0.5 }), skin: std(0xFFD5B5, { roughness: 0.5 }),
  wood: std(0xffffff, { map: woodTex, roughness: 0.8 }), woodD: std(0x6b4220, { map: woodTex, roughness: 0.85 }),
  red: new THREE.MeshStandardMaterial({ color: 0xff3b2f, emissive: 0xff2a1a, emissiveIntensity: 1.4, metalness: 0.3, roughness: 0.4 }),
  shear: new THREE.MeshBasicMaterial({ color: new THREE.Color(YEL).multiplyScalar(2.2), transparent: true, opacity: 0, depthWrite: false }),
};

// ---------- kunci pin tumbler ----------
const PZ = [-1.2, -0.6, 0, 0.6, 1.2], LB = [0.55, 0.8, 0.45, 0.7, 0.6];
const SHEAR = 0.7, REST = 0.4, DRV = 0.42, CEIL = 1.7, SPR = 0.6;
const H_OK = LB.map(l => SHEAR - l);
const H_BAD = H_OK.map((h, i) => i === 2 ? h - 0.22 : h);   // satu lekuk salah -> satu pin tidak rata
class Helix extends THREE.Curve { getPoint(u, tg = new THREE.Vector3()) { const a = u * Math.PI * 2 * 7; return tg.set(0.095 * Math.cos(a), u * SPR, 0.095 * Math.sin(a)); } }
const springGeo = new THREE.TubeGeometry(new Helix(), 220, 0.019, 6, false);
function makeProf(h) {
  const pts = [[-1.62, -0.28]];
  for (let i = 0; i < 5; i++) { pts.push([PZ[i] - 0.1, h[i]], [PZ[i] + 0.1, h[i]]); if (i < 4) pts.push([(PZ[i] + PZ[i + 1]) / 2, Math.min(0.34, Math.max(h[i], h[i + 1]) + 0.1)]); }
  pts.push([1.55, 0.34], [1.75, 0.34]);
  const f = z => { if (z < pts[0][0] || z > 1.75) return -9; for (let k = 0; k < pts.length - 1; k++) if (z <= pts[k + 1][0]) { const [a, ya] = pts[k], [b, yb] = pts[k + 1]; return lerp(ya, yb, (z - a) / Math.max(1e-6, b - a)); } return 0.34; };
  return { f, pts };
}
function makeKey(h, mat, tag = false) {
  const g = new THREE.Group(); const P = makeProf(h); g.userData.prof = P.f;
  const sh = new THREE.Shape(); sh.moveTo(-1.62, -0.28);
  for (const [z, y] of P.pts.slice(1)) sh.lineTo(z, y);
  sh.lineTo(1.75, -0.45); sh.lineTo(-1.45, -0.45); sh.lineTo(-1.62, -0.28);
  const bg = new THREE.ExtrudeGeometry(sh, { depth: 0.12, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.015, bevelSegments: 1 }); bg.translate(0, 0, -0.06); bg.rotateY(-Math.PI / 2);
  const blade = new THREE.Mesh(bg, mat); g.add(blade);
  const groove = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.08, 3.2), M.dark); groove.position.set(0.075, -0.22, 0.1); g.add(groove);
  const shoulder = new THREE.Mesh(new THREE.BoxGeometry(0.16, 1.0, 0.25), mat); shoulder.position.set(0, -0.05, 1.86); g.add(shoulder);
  const bs = new THREE.Shape(); bs.absarc(0, 0, 0.72, 0, Math.PI * 2, false); const hole = new THREE.Path(); hole.absarc(0.38, 0, 0.17, 0, Math.PI * 2, true); bs.holes.push(hole);
  const bowG = new THREE.ExtrudeGeometry(bs, { depth: 0.16, bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.03, bevelSegments: 2, curveSegments: 40 }); bowG.translate(0, 0, -0.08); bowG.rotateY(-Math.PI / 2);
  const bow = new THREE.Mesh(bowG, mat); bow.position.set(0, -0.05, 2.62); g.add(bow);
  if (tag) { // gantungan syal toska-kuning
    const tg = new THREE.Group(); tg.position.set(0, -0.05, 3.0); g.add(tg); g.userData.tag = tg;
    const lp = new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.035, 8, 24), M.chrome); lp.rotation.y = Math.PI / 2; tg.add(lp);
    const a = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.95, 0.36), M.teal); a.position.set(0, -0.62, 0.12); a.rotation.x = 0.12; tg.add(a);
    const b = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.85, 0.32), M.yel); b.position.set(0, -0.6, -0.24); b.rotation.x = -0.1; tg.add(b);
  }
  return g;
}
function makeLock() {
  const g = new THREE.Group();
  const hm = M.brass.clone(); hm.transparent = true; const pmM = M.brassL.clone(); pmM.transparent = true;
  const housing = new THREE.Group(); g.add(housing);
  const body = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 3.2, 56), hm); body.rotation.x = Math.PI / 2; housing.add(body);
  const tower = new THREE.Mesh(new THREE.BoxGeometry(0.86, 1.15, 3.2), hm); tower.position.y = 1.175; housing.add(tower);
  const flange = new THREE.Mesh(new THREE.CylinderGeometry(1.18, 1.18, 0.16, 56), hm); flange.rotation.x = Math.PI / 2; flange.position.z = 1.68; housing.add(flange);
  const screw = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.9, 20), M.steel); screw.position.set(0, -0.95, 0.4); housing.add(screw);
  const plug = new THREE.Group(); g.add(plug);
  const pb = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.7, 3.36, 56), pmM); pb.rotation.x = Math.PI / 2; plug.add(pb);
  const face = new THREE.Mesh(new THREE.CylinderGeometry(0.74, 0.74, 0.08, 56), pmM); face.rotation.x = Math.PI / 2; face.position.z = 1.74; plug.add(face);
  const kw = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.95, 0.02), M.dark); kw.position.set(0, -0.05, 1.79); plug.add(kw);
  const kw2 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.1, 0.02), M.dark); kw2.position.set(0.06, -0.25, 1.791); plug.add(kw2);
  const shear = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.04, 3.7), M.shear); shear.position.set(0.0, SHEAR, 0); g.add(shear);
  const shearGlow = new THREE.Mesh(new THREE.PlaneGeometry(3.9, 0.5), new THREE.MeshBasicMaterial({ map: softTex, color: YEL, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false }));
  shearGlow.rotation.y = Math.PI / 2; shearGlow.position.set(0.02, SHEAR, 0); g.add(shearGlow);
  const bottoms = [], drivers = [], springs = [];
  PZ.forEach((z, i) => {
    const L = LB[i]; const bp = new THREE.Group(); const m = M.brass.clone();
    const c = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, L - 0.1, 24), m); c.position.y = -(L - 0.1) / 2; bp.add(c);
    const tip = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.1, 24), m); tip.rotation.x = Math.PI; tip.position.y = -(L - 0.1) - 0.05; bp.add(tip);
    bp.userData.mat = m; plug.add(bp); bottoms.push(bp);
    const dm = M.chrome.clone(); const d = new THREE.Group(); const dc = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.11, DRV, 24), dm); dc.position.y = DRV / 2; d.add(dc); d.userData.mat = dm; g.add(d); drivers.push(d);
    const s = new THREE.Mesh(springGeo, M.steel); g.add(s); springs.push(s);
  });
  g.userData = { housing, plug, hm, pm: pmM, shear, shearGlow, bottoms, drivers, springs, keys: [] };
  return g;
}
function addKeyToLock(L, key) { L.userData.plug.add(key); L.userData.keys.push(key); return key; }
function poseLock(L, o = {}) {
  const u = L.userData; const e = o.e ?? 0, kz = o.kz ?? 0, key = o.key ?? null;
  u.keys.forEach(k => k.visible = k === key && (o.showKey ?? true));
  const tops = PZ.map((z, i) => { let top = REST; if (key) { const y = key.userData.prof(z - kz); if (y > -9) top = Math.max(top, y + LB[i]); } return top; });
  u.housing.position.y = -2.5 * e;
  u.plug.rotation.z = (o.rot ?? 0) + (o.shake ?? 0);
  if (key) key.position.z = kz;
  PZ.forEach((z0, i) => {
    const z = z0 * (1 + 0.3 * e);
    u.bottoms[i].position.set(0, lerp(tops[i], 1.85, e), z);
    u.drivers[i].position.set(0, lerp(tops[i], 2.25, e), z);
    const sb = lerp(tops[i] + DRV, 2.95, e), sl = lerp(CEIL - (tops[i] + DRV), SPR, e);
    u.springs[i].position.set(0, sb, z); u.springs[i].scale.set(1, Math.max(0.05, sl / SPR), 1);
    u.bottoms[i].userData.mat.emissive.setHex(0x000000); u.drivers[i].userData.mat.emissive.setHex(0x000000);
  });
  const gh = o.ghost ?? 0; u.hm.opacity = 1 - 0.82 * gh; u.pm.opacity = 1 - 0.74 * gh; u.hm.depthWrite = u.pm.depthWrite = gh < 0.01;
  M.shear.opacity = o.shear ?? 0; u.shearGlow.material.opacity = 0.8 * (o.shear ?? 0); u.shear.visible = u.shearGlow.visible = (o.shear ?? 0) > 0;
  return tops;
}

const lockA = makeLock(); stage.add(lockA);
const keyGood = addKeyToLock(lockA, makeKey(H_OK, M.nickel));
const keyBad = addKeyToLock(lockA, makeKey(H_BAD, M.nickel.clone()));

// tangan Aru (lengan biru tua + anak kunci bergantungan syal)
const arm = new THREE.Group(); stage.add(arm);
{
  const hk = makeKey(H_OK, M.nickel, true); hk.rotation.y = Math.PI; hk.position.z = 2.62; arm.add(hk); arm.userData.key = hk;
  const hand = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 16), M.skin); hand.scale.set(0.9, 0.85, 1.15); hand.position.set(0.25, -0.1, -0.15); arm.add(hand);
  const thumb = new THREE.Mesh(new THREE.CapsuleGeometry(0.11, 0.26, 4, 10), M.skin); thumb.position.set(-0.12, 0.1, 0.18); thumb.rotation.x = 1.2; arm.add(thumb);
  const cuff = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.09, 10, 28), M.teal); cuff.position.set(0.35, -0.2, -0.75); arm.add(cuff);
  const sleeve = new THREE.Mesh(new THREE.CapsuleGeometry(0.38, 3.2, 6, 18), M.navy); sleeve.rotation.x = Math.PI / 2; sleeve.position.set(0.4, -0.25, -2.6); arm.add(sleeve);
  arm.scale.setScalar(0.7);
}
// kunci melayang (adegan 2)
const keyF = new THREE.Group(); stage.add(keyF);
const keyFin = makeKey(H_OK, M.nickel, true); keyFin.rotation.x = -Math.PI / 2; keyF.add(keyFin);
const sweep = new THREE.Sprite(new THREE.SpriteMaterial({ map: softTex, color: 0xffffff, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); sweep.scale.set(1.3, 1.3, 1); stage.add(sweep);
const sweepL = new THREE.PointLight(0xffffff, 0, 3, 1.5); stage.add(sweepL);

// gantungan 10 kunci
const ringG = new THREE.Group(); stage.add(ringG);
const ringKeys = [];
{
  const tor = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.05, 12, 64), M.chrome); ringG.add(tor);
  const mats = [0xd6d2c6, 0xc9962e, 0xb3bac4, 0xe0b354, 0xd6d2c6, 0xa9a59a, 0xc9962e, 0xd6d2c6, 0xb3bac4, 0xe0b354];
  const R = mulberry(31);
  for (let i = 0; i < 10; i++) {
    const a = lerp(-0.85, 0.85, i / 9); const mat = metal(mats[i], 0.25);
    const special = i === 6;
    const hh = special ? H_OK : H_OK.map(() => -0.1 + R() * 0.35);
    const piv = new THREE.Group(); piv.position.set(0.62 * Math.sin(a), -0.62 * Math.cos(a), 0); piv.rotation.z = a; ringG.add(piv);
    // rotasi x=-PI/2: z lokal -> y; lubang bow (0,-0.05,3.0) -> (0,3.0,0.05) -> digeser ke pivot cincin
    const k = makeKey(hh, mat, special); k.rotation.x = -Math.PI / 2; k.position.set(0, -3.0, -0.05);
    const holder = new THREE.Group(); holder.add(k);
    const sc = new THREE.Group(); sc.scale.setScalar(0.42); sc.add(holder); piv.add(sc);
    ringKeys.push({ piv, mat, key: k, special });
  }
}

// kunci kayu gaya Mesir (balok + pasak)
const wood = new THREE.Group(); stage.add(wood);
{
  const blk = new THREE.Mesh(new THREE.BoxGeometry(1.7, 2.0, 1.3), M.wood); blk.position.y = 0.35; wood.add(blk);
  const bolt = new THREE.Mesh(new THREE.BoxGeometry(4.4, 0.5, 0.6), M.woodD); bolt.position.set(0.3, -0.25, 0.0); wood.add(bolt); wood.userData.bolt = bolt;
  for (let i = 0; i < 3; i++) { const p = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1.6, 14), M.woodD); p.position.set(-0.45 + i * 0.45, 0.9, 0); wood.add(p);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.1, 14), M.wood); cap.position.set(-0.45 + i * 0.45, 1.72, 0); wood.add(cap); }
  const wk = new THREE.Group(); wk.position.set(0.2, -1.25, 0.6); wood.add(wk);
  const st = new THREE.Mesh(new THREE.BoxGeometry(3.2, 0.22, 0.32), M.wood); wk.add(st);
  for (let i = 0; i < 3; i++) { const pg = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.32, 10), M.woodD); pg.position.set(-1.0 + i * 0.45, 0.25, 0); wk.add(pg); }
}
const lockS = makeLock(); stage.add(lockS); addKeyToLock(lockS, makeKey(H_OK, M.nickel));

// kunci pintar (badan gelap + keypad menyala), berisi silinder pin cadangan
const smart = new THREE.Group(); stage.add(smart);
const smartParts = {};
{
  const rrShape = (w, h, r) => { const s = new THREE.Shape(); s.moveTo(-w / 2 + r, -h / 2); s.lineTo(w / 2 - r, -h / 2); s.quadraticCurveTo(w / 2, -h / 2, w / 2, -h / 2 + r); s.lineTo(w / 2, h / 2 - r); s.quadraticCurveTo(w / 2, h / 2, w / 2 - r, h / 2); s.lineTo(-w / 2 + r, h / 2); s.quadraticCurveTo(-w / 2, h / 2, -w / 2, h / 2 - r); s.lineTo(-w / 2, -h / 2 + r); s.quadraticCurveTo(-w / 2, -h / 2, -w / 2 + r, -h / 2); return s; };
  const bodyM = new THREE.MeshStandardMaterial({ color: 0x1c212b, metalness: 0.55, roughness: 0.32, envMapIntensity: 1.1 });
  const cover = new THREE.Group(); smart.add(cover); smartParts.cover = cover;
  const cg = new THREE.ExtrudeGeometry(rrShape(1.6, 3.4, 0.35), { depth: 0.32, bevelEnabled: true, bevelThickness: 0.06, bevelSize: 0.06, bevelSegments: 3 }); cg.translate(0, 0, 0.02);
  cover.add(new THREE.Mesh(cg, bodyM));
  const glass = new THREE.Mesh(new THREE.ExtrudeGeometry(rrShape(1.2, 1.55, 0.14), { depth: 0.02, bevelEnabled: false }), new THREE.MeshStandardMaterial({ color: 0x05070b, metalness: 0.2, roughness: 0.12 })); glass.position.set(0, 0.62, 0.4); cover.add(glass);
  smartParts.keys = [];
  for (let r = 0; r < 4; r++) for (let c = 0; c < 3; c++) { const m = new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0x7ff6ea, emissiveIntensity: 1.2, roughness: 1 }); const b = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.22, 0.03), m); b.position.set(-0.34 + c * 0.34, 1.12 - r * 0.33, 0.43); cover.add(b); smartParts.keys.push(m); }
  const lever = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.2, 0.22), M.chrome); lever.position.set(0.35, -0.45, 0.6); cover.add(lever);
  const lb = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.3, 24), M.chrome); lb.rotation.x = Math.PI / 2; lb.position.set(-0.2, -0.45, 0.5); cover.add(lb);
  const kh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.06, 28), M.brassL); kh.rotation.x = Math.PI / 2; kh.position.set(0, -1.15, 0.4); cover.add(kh);
  const khs = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.22, 0.02), M.dark); khs.position.set(0, -1.15, 0.44); cover.add(khs);
  const led = new THREE.Mesh(new THREE.CircleGeometry(0.05, 16), new THREE.MeshBasicMaterial({ color: 0x3cff9a })); led.position.set(0.5, 1.48, 0.41); cover.add(led);
  const back = new THREE.Mesh(new THREE.ExtrudeGeometry(rrShape(1.5, 3.3, 0.33), { depth: 0.28, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 2 }), bodyM); back.position.z = -0.42; smart.add(back); smartParts.back = back;
  const inner = makeLock(); inner.scale.setScalar(0.3); inner.position.set(0, -1.15, 0.05); smart.add(inner); smartParts.inner = inner; addKeyToLock(inner, makeKey(H_OK, M.nickel));
}
// siluet orang terpercaya
const person = new THREE.Group(); stage.add(person);
{
  const pmM = std(0x6d7c99, { roughness: 0.55 });
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.5, 24, 16), pmM); head.position.y = 1.0; person.add(head);
  const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.62, 1.0, 6, 16), pmM); body.position.y = -0.45; person.add(body);
  const armR = new THREE.Mesh(new THREE.CapsuleGeometry(0.16, 0.9, 4, 10), pmM); armR.position.set(0.75, -0.1, 0.35); armR.rotation.set(-1.0, 0, -0.5); person.add(armR);
  const hand = new THREE.Mesh(new THREE.SphereGeometry(0.2, 14, 10), pmM); hand.position.set(1.0, 0.18, 0.8); person.add(hand); person.userData.hand = hand;
}
const keyS = new THREE.Group(); stage.add(keyS); { const k = makeKey(H_OK, M.brassL, true); k.rotation.x = -Math.PI / 2; keyS.add(k); keyS.scale.setScalar(0.36); }
const glowS = new THREE.Sprite(new THREE.SpriteMaterial({ map: softTex, color: 0xd7ff6a, transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false })); glowS.scale.set(2.2, 2.2, 1); stage.add(glowS);

// ---------- kamera ----------
const cam = new THREE.PerspectiveCamera(40, W / H, 0.05, 400);
function look(p, tg, fov = 40) { cam.position.set(...p); cam.up.set(0, 1, 0); cam.lookAt(...tg); cam.fov = fov; cam.updateProjectionMatrix(); }
function orbit(tg, dist, az, el, fov = 40) { look([tg[0] + dist * Math.sin(az) * Math.cos(el), tg[1] + dist * Math.sin(el), tg[2] + dist * Math.cos(az) * Math.cos(el)], tg, fov); }
const proj = v => { const p = v.clone().project(cam); return [(p.x + 1) / 2 * W, (1 - p.y) / 2 * H]; };
const wpos = (obj, v = [0, 0, 0]) => { obj.updateMatrixWorld(true); return obj.localToWorld(new THREE.Vector3(...v)); };

// ---------- 2D overlay ----------
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
function background(glows) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#46546a'); g.addColorStop(0.45, '#2a3446'); g.addColorStop(1, '#0d1119'); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  for (const [x, y, r, a] of glows) { const rg = ctx.createRadialGradient(x, y, 0, x, y, r); rg.addColorStop(0, `rgba(255,140,40,${0.55 * a})`); rg.addColorStop(0.45, `rgba(255,110,30,${0.22 * a})`); rg.addColorStop(1, 'rgba(255,100,20,0)'); ctx.fillStyle = rg; ctx.fillRect(x - r, y - r, r * 2, r * 2); }
}
function subtitle(t) {
  if (t >= CLOSE) return;
  let c = null; for (const k of CH) if (t >= k.s && t < Math.min(k.show_end, CLOSE)) c = k; if (!c) return;
  const a = (c.s === 0 ? 1 : ramp(t, c.s, 0.08)) * (1 - ramp(t, Math.min(c.show_end, CLOSE) - 0.06, 0.06));
  let fs = 58; const txt = c.text, kw = c.kw; const i = kw ? txt.indexOf(kw) : -1;
  const parts = i < 0 ? [[txt, 0]] : [[txt.slice(0, i), 0], [kw, 1], [txt.slice(i + kw.length), 0]];
  let tw; do { ctx.font = `${fs}px PB`; tw = parts.reduce((s, [p, k]) => s + ctx.measureText(p).width + (k ? 28 : 0), 0); if (tw > 800) fs -= 2; } while (tw > 800 && fs > 36);
  let x = W / 2 - tw / 2; const y = 1475; const pop = c.s === 0 ? 1 : 1 + 0.06 * (1 - easeOut((t - c.s) / 0.15));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, y); ctx.scale(pop, pop); ctx.translate(-W / 2, -y); ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
  for (const [p, k] of parts) { const w = ctx.measureText(p).width;
    if (k) { ctx.fillStyle = CYEL; rr(x, y - fs * 0.68, w + 28, fs * 1.32, 12); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(p, x + 14, y + 2); x += w + 28; }
    else { ctx.shadowColor = 'rgba(0,0,0,.9)'; ctx.shadowBlur = 14; ctx.fillStyle = '#fff'; ctx.fillText(p, x, y + 2); ctx.shadowBlur = 0; x += w; } }
  ctx.restore();
}
function source(t, a, b, s) { if (t < a || t >= b) return; const al = ramp(t, a, 0.25) * (1 - ramp(t, b - 0.2, 0.2)); ctx.save(); ctx.globalAlpha = al * 0.88; ctx.font = '27px PM'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 8; ctx.fillStyle = '#e4eaf6'; ctx.fillText('Sumber: ' + s, W / 2, 1640); ctx.restore(); }
function smallText(t, a, b, s, y, f = '30px PM', col = '#e8eefc') { if (t < a || t >= b) return; const al = ramp(t, a, 0.3) * (1 - ramp(t, b - 0.25, 0.25)); ctx.save(); ctx.globalAlpha = al; ctx.font = f; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.shadowColor = '#000'; ctx.shadowBlur = 10; ctx.fillStyle = col; ctx.fillText(s, W / 2, y); ctx.restore(); }
function follow(t) { if (t < 10 || t >= 15) return; smallText(t, 10, 15, 'Follow @kabar.arunika buat fakta sehari-hari dalam 1 menit', 1725, '25px PM', '#e8eefc'); }
function pill(t) { // judul layar frame 0
  if (t > 3.6) return; const a = 1 - ramp(t, 3.25, 0.35);
  ctx.save(); ctx.globalAlpha = a; ctx.font = '52px PB'; const s1 = 'Anak kunci, kok ', s2 = 'PILIH-PILIH', s3 = '?';
  const w = ctx.measureText(s1 + s2 + s3).width; const x0 = W / 2 - w / 2 - 36, y0 = 292, h = 108;
  ctx.fillStyle = 'rgba(10,18,52,.84)'; rr(x0, y0, w + 72, h, 54); ctx.fill(); ctx.strokeStyle = 'rgba(18,194,176,.95)'; ctx.lineWidth = 4; ctx.stroke();
  ctx.textBaseline = 'middle'; ctx.textAlign = 'left'; let x = x0 + 36; const y = y0 + h / 2 + 4;
  ctx.fillStyle = '#fff'; ctx.fillText(s1, x, y); x += ctx.measureText(s1).width; ctx.fillStyle = CYEL; ctx.fillText(s2, x, y); x += ctx.measureText(s2).width; ctx.fillStyle = '#fff'; ctx.fillText(s3, x, y);
  ctx.restore();
}
function headerLogo(t) { if (t < 4.0 || t >= CLOSE) return; const a = ramp(t, 4.0, 0.4) * 0.9; const lw = 190, lh = lw * logo.height / logo.width; ctx.save(); ctx.globalAlpha = a; ctx.drawImage(logo, W / 2 - lw / 2, 262 - lh / 2, lw, lh); ctx.restore(); }
// label garis penunjuk putih tipis + pill 1 kata
function callout(t, t0, anchor, text, side = 1, dy = 0, col = '#fff', tcol = CNAVY, dx = 230) {
  if (t < t0) return; const a = ramp(t, t0, 0.25); const [ax, ay] = proj(anchor);
  ctx.save(); ctx.font = '32px PB'; const tw = ctx.measureText(text).width; const pw = tw + 44, ph = 58;
  let px = ax + side * dx; px = side > 0 ? Math.min(px, 950 - pw) : Math.max(px - pw, 130); const py = clamp(ay + dy, 330, 1350);
  const lx = side > 0 ? px : px + pw; const grow = easeOut((t - t0) / 0.3);
  ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(255,255,255,.92)'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(lerp(ax, lx, grow), lerp(ay, py, grow)); ctx.stroke();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(ax, ay, 7, 0, 7); ctx.fill();
  ctx.fillStyle = col; rr(px, py - ph / 2, pw, ph, ph / 2); ctx.fill();
  ctx.fillStyle = tcol; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(text, px + 22, py + 2); ctx.restore();
}
function drawX(x, y, s, a = 1, col = CRED, lw = 10) { ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x - s, y - s); ctx.lineTo(x + s, y + s); ctx.moveTo(x + s, y - s); ctx.lineTo(x - s, y + s); ctx.stroke(); ctx.restore(); }
function drawCheck(x, y, s, a = 1, col = CYEL, lw = 10) { ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.beginPath(); ctx.moveTo(x - s, y); ctx.lineTo(x - s * 0.3, y + s * 0.7); ctx.lineTo(x + s, y - s * 0.8); ctx.stroke(); ctx.restore(); }
function shareIcon(x, y, s, col = CNAVY) { ctx.save(); ctx.fillStyle = col; ctx.beginPath(); ctx.moveTo(x - s, y - s * 0.1); ctx.lineTo(x + s, y - s * 0.9); ctx.lineTo(x + s * 0.35, y + s * 0.95); ctx.lineTo(x + s * 0.05, y + s * 0.2); ctx.closePath(); ctx.fill(); ctx.restore(); }
function ctaShare(t) { // teks ajakan kirim di puncak
  const a0 = cs(17) + 0.25, b0 = cs(25); if (t < a0 || t >= b0) return;
  const a = ramp(t, a0, 0.25) * (1 - ramp(t, b0 - 0.25, 0.25)); const sc = 1 + 0.08 * (1 - easeOut((t - a0) / 0.35));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, 420); ctx.scale(sc, sc); ctx.translate(-W / 2, -420);
  const x0 = 130, w = 820, y0 = 350, h = 140; ctx.fillStyle = 'rgba(255,255,255,.96)'; rr(x0, y0, w, h, 30); ctx.fill();
  ctx.fillStyle = CYEL; ctx.beginPath(); ctx.arc(x0 + 78, y0 + h / 2, 46, 0, 7); ctx.fill(); shareIcon(x0 + 76, y0 + h / 2, 24);
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.font = '36px PB'; ctx.fillStyle = CNAVY; ctx.fillText('Kirim ke teman yang gantungan', x0 + 146, y0 + 46);
  const s1 = 'kuncinya isi '; ctx.fillText(s1, x0 + 146, y0 + 96); const w1 = ctx.measureText(s1).width; ctx.fillStyle = CYEL; rr(x0 + 146 + w1 - 4, y0 + 70, 70, 54, 10); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText('10', x0 + 146 + w1 + 6, y0 + 99);
  ctx.restore();
}
function counter(t) { // angka payoff bergerak dtk ~2 (bukan HUD)
  if (t < 1.8 || t >= SC[1]) return; const a = ramp(t, 1.8, 0.15) * (1 - ramp(t, SC[1] - 0.25, 0.25)); const n = Math.round(5 * easeOut((t - 1.85) / 0.75));
  const pop = 1 + 0.12 * Math.max(0, 1 - ((t - 1.85) % 0.15) / 0.15) * (t < 2.6 ? 1 : 0);
  ctx.save(); ctx.globalAlpha = a; ctx.translate(W / 2, 600); ctx.scale(pop, pop); ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillStyle = 'rgba(8,12,26,.72)'; rr(-200, -110, 400, 210, 36); ctx.fill();
  ctx.font = '170px PB'; const nw = ctx.measureText(String(n)).width; ctx.font = '64px PB'; const pw = ctx.measureText('PIN').width; const tot = nw + 24 + pw;
  ctx.font = '170px PB'; ctx.fillStyle = CYEL; ctx.shadowColor = 'rgba(255,184,0,.6)'; ctx.shadowBlur = 30; ctx.textAlign = 'left'; ctx.fillText(String(n), -tot / 2, 0); ctx.shadowBlur = 0;
  ctx.font = '64px PB'; ctx.fillStyle = '#fff'; ctx.shadowColor = '#000'; ctx.shadowBlur = 12; ctx.fillText('PIN', -tot / 2 + nw + 24, 18); ctx.restore();
}
function qmark(t, x, y) { const t0 = cs(6) - 0.05; if (t < t0) return; const a = ramp(t, t0, 0.15); const s = easeBack((t - t0) / 0.35) * (1 + 0.04 * Math.sin(t * 6));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(s, s); ctx.fillStyle = CYEL; ctx.beginPath(); ctx.arc(0, 0, 78, 0, 7); ctx.fill(); ctx.fillStyle = CNAVY; ctx.font = '120px PB'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText('?', 0, 8); ctx.restore(); }
function yaleCard(t) { const t0 = cs(29) - 0.1; if (t < t0 || t >= SC[7]) return; const a = ramp(t, t0, 0.25) * (1 - ramp(t, SC[7] - 0.2, 0.2)); const dy = 30 * (1 - easeOut((t - t0) / 0.35));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(0, dy); const x0 = 190, y0 = 360, w = 700, h = 170; ctx.fillStyle = 'rgba(10,16,34,.88)'; rr(x0, y0, w, h, 26); ctx.fill(); ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 2.5; ctx.stroke();
  ctx.fillStyle = '#5d6c88'; rr(x0 + 24, y0 + 22, 126, 126, 20); ctx.fill(); ctx.save(); rr(x0 + 24, y0 + 22, 126, 126, 20); ctx.clip(); ctx.fillStyle = '#1b2232'; ctx.beginPath(); ctx.arc(x0 + 87, y0 + 70, 28, 0, 7); ctx.fill(); ctx.beginPath(); ctx.ellipse(x0 + 87, y0 + 150, 52, 46, 0, 0, 7); ctx.fill(); ctx.restore();
  ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.font = '44px PB'; ctx.fillStyle = '#fff'; ctx.fillText('Linus Yale Jr.', x0 + 178, y0 + 62); ctx.font = '32px PM'; ctx.fillStyle = CYEL; ctx.fillText('paten 1865', x0 + 178, y0 + 118); ctx.restore(); }
function phoneIcon(t, x, y, tx, ty) { const t0 = cs(32); if (t < t0 || t >= cs(34) + 0.4) return; const a = ramp(t, t0, 0.25) * (1 - ramp(t, cs(34) + 0.1, 0.3));
  ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(127,246,234,.9)'; ctx.lineWidth = 4; ctx.setLineDash([14, 12]); ctx.lineDashOffset = -t * 60; ctx.beginPath(); ctx.moveTo(x - 40, y + 60); ctx.lineTo(tx, ty); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillStyle = '#0d121c'; rr(x - 55, y - 95, 110, 190, 20); ctx.fill(); ctx.strokeStyle = '#fff'; ctx.lineWidth = 5; ctx.stroke(); ctx.fillStyle = '#7ff6ea'; rr(x - 40, y - 72, 80, 130, 8); ctx.fill(); ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(x, y + 76, 7, 0, 7); ctx.fill();
  ctx.fillStyle = CNAVY; ctx.beginPath(); ctx.arc(x, y - 5, 18, 0, 7); ctx.fill(); ctx.fillStyle = '#7ff6ea'; ctx.fillRect(x - 5, y - 10, 10, 16);
  ctx.strokeStyle = '#7ff6ea'; ctx.lineWidth = 5; for (let k = 1; k <= 3; k++) { ctx.globalAlpha = a * (0.4 + 0.6 * ((Math.floor(t * 4) % 3) >= k - 1 ? 1 : 0.3)); ctx.beginPath(); ctx.arc(x, y - 105, 14 * k, Math.PI * 1.2, Math.PI * 1.8); ctx.stroke(); }
  ctx.restore(); }
function tally(t, nWrong, ok, a) { // 10 percobaan: 9 X merah, 1 centang
  ctx.save(); ctx.globalAlpha = a; const x0 = 190, y = 450, dx = 78; ctx.fillStyle = 'rgba(10,16,34,.75)'; rr(x0 - 50, y - 50, dx * 9 + 100, 100, 50); ctx.fill();
  for (let i = 0; i < 10; i++) { const x = x0 + i * dx; ctx.strokeStyle = 'rgba(255,255,255,.35)'; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y, 26, 0, 7); ctx.stroke();
    if (i < nWrong) drawX(x, y, 13, 1, CRED, 8); else if (i === 9 && ok) { ctx.fillStyle = CYEL; ctx.beginPath(); ctx.arc(x, y, 30, 0, 7); ctx.fill(); drawCheck(x, y, 15, 1, CNAVY, 8); } }
  ctx.restore(); }
function teamPill(x, y, text, bg, fg, a, t0, t) { if (t < t0) return; const s = easeBack((t - t0) / 0.35); ctx.save(); ctx.globalAlpha = a * ramp(t, t0, 0.15); ctx.translate(x, y); ctx.scale(s, s); ctx.font = '46px PB'; const w = ctx.measureText(text).width + 60; ctx.fillStyle = bg; rr(-w / 2, -40, w, 80, 40); ctx.fill(); ctx.fillStyle = fg; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.fillText(text, 0, 3); ctx.restore(); }
function flash(t, t0, col, k = 0.35, d = 0.35) { if (t < t0 || t > t0 + d) return; const u = (t - t0) / d; ctx.fillStyle = col.replace('A', (k * (1 - u)).toFixed(3)); ctx.fillRect(0, 0, W, H); }

// ---------- frame ----------
function sceneOf(t) { let k = 0; for (let i = 0; i < SC.length; i++) if (t >= SC[i]) k = i; return k; }
function hideAll() { [lockA, arm, keyF, sweep, ringG, wood, lockS, smart, person, keyS, glowS].forEach(o => o.visible = false); ringA.visible = ringB.visible = false; sweepL.intensity = 0; }
function setRing(r, x, z = 0, k = 1, s = 1) { r.visible = true; r.position.set(x, FLOOR, z); r.scale.setScalar(s); r.userData.ring.material.opacity = 0.95 * k; r.userData.disc.material.opacity = 0.55 * k; }
function resetLock(L) { L.position.set(0, 0, 0); L.rotation.set(0, 0, 0); L.scale.setScalar(1); }

window.renderFrame = function (t) {
  const k = sceneOf(t); const t0 = SC[k], t1 = k + 1 < SC.length ? SC[k + 1] : TOTAL; const lt = t - t0, u = clamp(lt / (t1 - t0));
  hideAll(); resetLock(lockA); const bob = 0.12 * Math.sin(t * 1.3);
  const glows = []; let focus = null; const post = { dim: 0 }; const L2 = []; // L2: daftar gambar 2D setelah render
  orgL.intensity = 9;
  if (k === 0) { // HOOK: silinder utuh + tangan Aru, dtk 1,5 meledak
    lockA.visible = true; lockA.position.y = 0.3 + bob; lockA.rotation.y = 0.38 + 0.08 * Math.sin(t * 0.6);
    const e = easeOut((t - 1.5) / 0.75); poseLock(lockA, { e });
    const kwp = wpos(lockA, [0, -0.05, 1.8]);
    if (t < 2.6) { arm.visible = true; const r = ease((t - 1.35) / 0.9); const off = new THREE.Vector3(1.0 + 2.0 * r, -2.2 - 1.6 * r, 1.6 + 1.0 * r); const p = kwp.clone().add(off); arm.position.copy(p); arm.lookAt(kwp); arm.rotateZ(0.25 * Math.sin(t * 1.1)); arm.position.addScaledVector(off.clone().normalize(), -0.25 * Math.sin(t * 2.2) * (1 - r)); }
    const az = 0.26 * ease((t - 1.5) / 3.7), dist = t < 1.5 ? lerp(12.6, 12.2, t / 1.5) : lerp(12.2, 19.6, easeOut((t - 1.5) / 0.8)) - 1.2 * ease((t - 2.3) / 2.9);
    orbit([0, lerp(0.15, -0.35, e), 0], dist, az, 0.1, 40);
    focus = [0, 0.3, 0]; setRing(ringA, 0);
    L2.push(() => { pill(t); counter(t); });
  } else if (k === 1) { // anak kunci melayang, gerigi disapu cahaya, tanda "?"
    keyF.visible = true; keyF.position.set(-0.45, 0.7 + bob, 1.5); keyF.rotation.set(0, Math.PI / 2 + 0.55 * Math.sin((t - SC[1]) * 0.7) - 0.25, 0.12); keyF.scale.setScalar(0.5);
    lockA.visible = true; lockA.position.set(1.6, 0.3, -12); lockA.rotation.y = 0.4 + 0.15 * t; poseLock(lockA, { e: 1 });
    const sw = clamp((t - (cs(5) + 0.1)) / 1.2); if (sw > 0 && sw < 1) { sweep.visible = true; const z = lerp(1.6, -1.5, sw); const p = wpos(keyFin, [0.1, keyGood.userData.prof(z) + 0.05, z]); sweep.position.copy(p); sweep.material.opacity = Math.sin(sw * Math.PI) * 0.95; sweepL.position.copy(p).add(new THREE.Vector3(0, 0, 0.6)); sweepL.intensity = 6 * Math.sin(sw * Math.PI); }
    const pan = ease((t - cs(7) - 0.2) / 1.6); const kp = wpos(keyF, [0, 0, 0]);
    const tg = [lerp(kp.x + 0.3, 1.6, pan), lerp(kp.y, 0.6, pan), lerp(kp.z, -12, pan)];
    look([lerp(0.3, -0.6, pan), lerp(1.6, 1.0, ease(lt / 2.5)) + 0.3 * pan, lerp(10.0, 8.5, pan) - 0.6 * ease(lt / 3)], tg, 40);
    focus = [-0.45, 0.7, 1.5]; setRing(ringA, -0.45, 1.5, 1); setRing(ringB, 1.6, -12, 0.7);
    const qp = proj(wpos(keyFin, [0, 0.85, -0.2]));
    L2.push(() => { if (t < cs(7) + 1.2) qmark(t, clamp(qp[0], 230, 850), clamp(qp[1], 560, 1250)); });
  } else if (k === 2) { // exploded view lengkap + label
    lockA.visible = true; lockA.position.y = 0.3 + bob * 0.6; lockA.rotation.y = 0.35 + 0.17 * lt; poseLock(lockA, { e: 1 });
    const hl = ramp(t, cs(11), 0.3); lockA.userData.bottoms.forEach(b => b.userData.mat.emissive.setRGB(0.25 * hl, 0.15 * hl, 0));
    orbit([0, -0.3, 0], lerp(19.4, 18.4, u), 0.05, 0.08, 40); focus = [0, 0.3, 0]; setRing(ringA, 0);
    const U = lockA.userData;
    const aBadan = wpos(U.housing, [0.95, -0.2, 0.6]), aSil = wpos(U.plug, [0.62, 0.2, 1.2]), aPeg = wpos(U.springs[4], [0.08, 0.3, 0]), aAtas = wpos(U.drivers[0], [-0.1, 0.2, 0]), aBawah = wpos(U.bottoms[4], [0.1, -0.3, 0]);
    L2.push(() => {
      callout(t, cs(8) + 0.1, aBadan, 'BADAN', -1, 40); callout(t, cs(8) + 0.7, aSil, 'SILINDER', 1, 30);
      callout(t, cs(10) + 0.35, aPeg, 'PEGAS', 1, -30); callout(t, cs(10) + 0.95, aAtas, 'PIN ATAS', -1, -20); callout(t, cs(11) + 0.05, aBawah, 'PIN BAWAH', 1, 40, CYEL);
      source(t, SC[2] + 0.3, SC[3], 'Wikipedia · Pin tumbler lock'); follow(t);
    });
  } else if (k === 3) { // merapat, cutaway, kunci masuk, garis geser
    lockA.visible = true; lockA.position.y = 0.3; lockA.rotation.y = 0;
    const e = 1 - ease(lt / 0.75); const gh = ramp(t, SC[3] + 0.35, 0.45);
    const ks = cs(12) + 0.35, ke = cs(14) + 0.45; const kz = lerp(3.7, 0, ease((t - ks) / (ke - ks)) * 0.15 + 0.85 * clamp((t - ks) / (ke - ks)));
    const sh = ramp(t, cs(15) - 0.05, 0.25) * (0.85 + 0.15 * Math.sin(t * 9));
    poseLock(lockA, { e, key: keyGood, kz, ghost: gh, shear: sh });
    const slow = ease((t - ke + 0.2) / 1.6);
    const az = lerp(1.05, 1.32, ease(lt / 3.5)), dist = lerp(lerp(12.6, 9.6, ease(lt / 1.2)), 7.0, slow);
    orbit([0, lerp(0.5, 0.75, slow), lerp(0, -0.1, slow)], dist, az, lerp(0.18, 0.06, slow), 40);
    focus = [0, 0.3, 0]; setRing(ringA, 0);
    const aG = wpos(lockA, [0, SHEAR, -1.75]);
    L2.push(() => { callout(t, cs(15) + 0.05, aG, 'GARIS GESER', 1, -150, CYEL, CNAVY, 40); });
  } else if (k === 4) { // PUNCAK: berputar (kunci benar) | kunci salah nyangkut
    lockA.visible = true; lockA.position.y = 0.3;
    if (t < CUT_B) {
      lockA.rotation.y = 0.0; const r = (Math.PI / 2) * easeOut((t - cs(17)) / 0.45);
      poseLock(lockA, { key: keyGood, kz: 0, ghost: 0.55, rot: -r, shear: 0.9 * (1 - ramp(t, cs(17) + 0.5, 0.5)) });
      orbit([0, 0.35, 0.4], lerp(11.2, 10.4, u), lerp(0.62, 0.72, ease(lt / 2.4)), 0.12, 40);
      const kp = wpos(lockA, [0, 0, 1.8]); const fl = proj(kp);
      L2.push(() => { flash(t, cs(17) + 0.42, 'rgba(255,200,40,A)', 0.4, 0.3); if (t > cs(17) + 0.4 && t < cs(17) + 1.0) { const q = (t - cs(17) - 0.4) / 0.6; ctx.save(); ctx.globalAlpha = 1 - q; ctx.strokeStyle = CYEL; ctx.lineWidth = 8; ctx.lineCap = 'round'; for (let i = 0; i < 10; i++) { const an = i / 10 * Math.PI * 2; const r0 = 70 + 160 * q, r1 = r0 + 60; ctx.beginPath(); ctx.moveTo(fl[0] + r0 * Math.cos(an), fl[1] + r0 * Math.sin(an)); ctx.lineTo(fl[0] + r1 * Math.cos(an), fl[1] + r1 * Math.sin(an)); ctx.stroke(); } ctx.restore(); } });
    } else {
      lockA.rotation.y = 0; const ks = CUT_B + 0.15, ke = cs(19) + 0.1; const kz = lerp(3.7, 0, clamp((t - ks) / (ke - ks)));
      const mac = t > cs(21) ? 0.07 * Math.sin((t - cs(21)) * 55) * Math.exp(-(t - cs(21)) * 2.2) : 0;
      const tops = poseLock(lockA, { key: keyBad, kz, ghost: 1, shear: ramp(t, cs(19), 0.3), shake: mac });
      const hi = ramp(t, cs(19) + 0.6, 0.3); const U = lockA.userData; U.drivers[2].userData.mat.emissive.setRGB(1.2 * hi, 0.1 * hi, 0.05 * hi); U.bottoms[2].userData.mat.emissive.setRGB(0.6 * hi, 0.05 * hi, 0);
      orbit([0, 0.6, -0.15], lerp(8.4, 7.2, ease(lt / 4)), lerp(1.4, 1.25, ease(lt / 4)), 0.05, 40);
      const aN = wpos(lockA, [0, tops[2] + DRV * 0.5, PZ[2]]); const bowp = proj(wpos(keyBad, [0, 0.1, 2.62]));
      L2.push(() => { if (t > ks) drawX(clamp(bowp[0], 170, 910), clamp(bowp[1] - 120, 620, 1300), 40, ramp(t, ks, 0.2), CRED, 14); callout(t, cs(20) - 0.05, aN, 'NYANGKUT', 1, -210, CRED, '#fff', 60); flash(t, cs(21), 'rgba(255,40,30,A)', 0.22, 0.4); });
    }
    focus = [0, 0.3, 0]; setRing(ringA, 0);
  } else if (k === 5) { // gantungan 10 kunci, dicoba bergiliran
    ringG.visible = true; ringG.position.set(0, 2.1 + bob, 0); ringG.rotation.set(0, 0.35 * Math.sin(t * 0.7), 0);
    const ts = SC[5] + 0.45, te = cs(24); const dt = (te - ts) / 9; const order = [0, 1, 2, 3, 4, 5, 7, 8, 9, 6];
    let nW = 0; const ok = t >= te;
    order.forEach((ki, j) => { const rk = ringKeys[ki]; const at = j < 9 ? ts + j * dt : te; const act = t >= at && t < at + dt * 0.95; rk.piv.rotation.x = act ? -0.35 * Math.sin(clamp((t - at) / (dt * 0.95)) * Math.PI) : 0;
      if (j < 9) { if (t >= at) nW = j + 1; rk.mat.emissive.setRGB(act ? 0.9 : (t >= at ? 0.12 : 0), act ? 0.05 : 0, 0); } else rk.mat.emissive.setRGB(ok ? 0.55 : 0, ok ? 0.5 : 0, ok ? 0.05 : 0); });
    const sp = ringKeys[6]; if (ok) { glowS.visible = true; glowS.position.copy(wpos(sp.key, [0, 0, 0.5])); glowS.material.opacity = 0.85 * ramp(t, te, 0.2); }
    const zo = easeOut((t - cs(25) - 0.05) / 0.55); post.dim = 0.5 * zo;
    look([0, lerp(1.4, 2.2, zo), lerp(12.2, 19, zo)], [0, lerp(0.75, 0.9, zo), 0], 40);
    focus = [0, 0.8, 0]; setRing(ringA, 0);
    const actKey = order.find((ki, j) => { const at = j < 9 ? ts + j * dt : te; return t >= at && t < at + dt * 0.95 && j < 9; });
    const xp = actKey !== undefined ? proj(wpos(ringKeys[actKey].key, [0, 0, -1.0])) : null;
    L2.push(() => { tally(t, nW, ok, ramp(t, ts - 0.1, 0.2) * (1 - zo)); if (xp) drawX(xp[0], xp[1], 34, 1, CRED, 12); });
  } else if (k === 6) { // kunci kayu Mesir -> menyusut jadi silinder logam + Yale
    const m = ease((t - cs(28)) / 0.9), g = easeBack((t - cs(28) - 0.35) / 0.8);
    if (m < 1) { wood.visible = true; wood.position.set(0, 0.4 + bob, 0); wood.rotation.set(0.05, 0.85 + 0.2 * Math.sin(t * 0.6) + 2.0 * m, 0); wood.scale.setScalar(Math.max(0.001, 1 - m)); }
    if (g > 0.001) { lockS.visible = true; resetLock(lockS); lockS.position.set(0, 0.1 + bob, 0); lockS.rotation.y = 0.6 + 0.5 * (t - cs(28)); lockS.scale.setScalar(0.62 * g); poseLock(lockS, {}); }
    const pulse = t > cs(30) ? 1 + 0.18 * Math.sin((t - cs(30)) * 9) * Math.exp(-(t - cs(30)) * 0.8) : 1;
    orbit([0, 0.3, 0], lerp(10.5, 9.6, u), 0.1, 0.16, 40); focus = [0, 0.3, 0]; setRing(ringA, 0, 0, t > cs(30) ? 1.2 : 1, pulse); orgL.intensity = 9 * pulse;
    const aK = wpos(wood, [0.85, 0.9, 0.65]);
    L2.push(() => { if (m < 0.6) callout(t, cs(26) + 0.4, aK, 'KAYU', 1, -60); yaleCard(t); source(t, SC[6] + 0.2, cs(29) - 0.1, '±2000 SM · Explain that Stuff'); source(t, cs(29) - 0.1, SC[7], 'paten AS 48.475, 1865 · GreatPatent'); });
    glows.push(['pulse', pulse]);
  } else if (k === 7) { // kunci pintar masuk dari kanan, lalu dibongkar: ada silinder pin cadangan
    smart.visible = true; const en = easeOut((t - SC[7]) / 0.9); const ex = ease((t - cs(34) - 0.05) / 0.7);
    smart.position.set(lerp(5.5, 0, en), 0.4 + bob, 0); smart.rotation.set(0, lerp(-0.9, -0.38, en) + 0.12 * Math.sin(t * 0.5) + 0.35 * ex, 0); smart.scale.setScalar(1);
    smartParts.cover.position.set(1.7 * ex, 0.35 * ex, 1.2 * ex); smartParts.cover.rotation.y = -0.9 * ex; smartParts.back.position.set(-0.3 * ex, 0, -0.42 - 0.6 * ex);
    const inn = smartParts.inner; inn.position.set(-0.55 * ex, lerp(-1.15, -0.2, ex), lerp(0.05, 1.3, ex)); inn.scale.setScalar(lerp(0.3, 0.5, ex)); inn.rotation.y = 0.9 * ex;
    poseLock(inn, { e: 0.6 * ease((t - cs(35)) / 0.6), key: inn.userData.keys[0], kz: 0, showKey: false });
    smartParts.keys.forEach((km, i) => { const blink = t > cs(32) + 0.1 && t < cs(33) && Math.floor((t - cs(32)) * 8) % 12 === i; km.emissiveIntensity = blink ? 3.2 : 1.1; });
    orbit([0, 0.35, 0], lerp(11.2, 10.6, u), lerp(0.0, -0.45, ex), 0.1, 40); focus = [lerp(5.5, 0, en), 0.4, 0]; setRing(ringA, focus[0]);
    const kp = proj(wpos(smartParts.cover, [0, 1.2, 0.45])); const aC = wpos(inn, [0.9, 0.3, 1.0]);
    L2.push(() => { phoneIcon(t, 820, 560, kp[0] + 40, kp[1]); callout(t, cs(35) + 0.1, aC, 'CADANGAN', 1, 60, CYEL, CNAVY, 150); source(t, SC[7] + 0.4, SC[8], 'Which?, 15 Apr 2026'); });
  } else if (k === 8 || k === 9) { // berdampingan setara; kunci cadangan ke orang terpercaya / layar terbelah
    const split = k === 9;
    lockA.visible = true; lockA.scale.setScalar(0.58); lockA.position.set(-1.3, 0.0 + bob, 0); lockA.rotation.y = 0.75 + (split ? 0.5 * (t - SC[9]) : 0.1 * Math.sin(t * 0.6)); poseLock(lockA, {});
    smart.visible = true; smart.position.set(1.3, 0.05 - bob, 0); smart.scale.setScalar(0.58); smart.rotation.set(0, -0.45 - (split ? 0.5 * (t - SC[9]) : 0.1 * Math.sin(t * 0.6)), 0);
    smartParts.cover.position.set(0, 0, 0); smartParts.cover.rotation.y = 0; smartParts.back.position.set(0, 0, -0.42); smartParts.inner.position.set(0, -1.15, 0.05); smartParts.inner.scale.setScalar(0.3); smartParts.inner.rotation.y = 0; poseLock(smartParts.inner, {});
    smartParts.keys.forEach(km => km.emissiveIntensity = 1.1);
    setRing(ringA, -1.3, 0, 1, 0.6); setRing(ringB, 1.3, 0, 1, 0.6); focus = null; glows.push(['two']);
    if (!split) {
      person.visible = true; person.position.set(0, 1.9, -3.2); person.rotation.y = -0.2;
      const f = easeOut((t - cs(37) + 0.1) / 1.55); const hp = wpos(person.userData.hand); const p0 = new THREE.Vector3(0, -0.6, 1.6);
      keyS.visible = true; keyS.position.lerpVectors(p0, hp, f).add(new THREE.Vector3(0, 0.8 * Math.sin(f * Math.PI), 0)); keyS.rotation.set(0.2, t * 1.6, 0.3 * Math.sin(t));
      look([0, lerp(1.2, 1.6, u), lerp(14.6, 14.0, u)], [0, 0.5, -0.8], 40);
      const aS = wpos(keyS, [0, 0, 0]);
      L2.push(() => { callout(t, cs(38) + 0.05, aS, 'CADANGAN', 1, -90, CYEL, CNAVY, 120); });
    } else {
      look([0, 0.9, lerp(15.2, 14.6, u)], [0, 0.25, 0], 40);
      L2.push(() => {
        const a = ramp(t, SC[9], 0.3); ctx.save(); ctx.globalAlpha = a * 0.16; ctx.fillStyle = CTEAL; ctx.fillRect(0, 0, W / 2, H); ctx.fillStyle = CYEL; ctx.fillRect(W / 2, 0, W / 2, H); ctx.globalAlpha = a; ctx.strokeStyle = 'rgba(255,255,255,.85)'; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(W / 2, 420); ctx.lineTo(W / 2, 1360); ctx.stroke(); ctx.restore();
        teamPill(300, 560, 'TIM BIASA', CTEAL, CNAVY, 1, cs(41) + 0.1, t); teamPill(780, 560, 'TIM PINTAR', CYEL, CNAVY, 1, cs(42) + 0.1, t);
      });
    }
  }

  // ---- komposit ----
  const isClose = k >= 10;
  if (!isClose) {
    // lingkaran cahaya oranye di belakang benda
    const gl = [];
    if (focus) { const p = proj(new THREE.Vector3(...focus)); gl.push([p[0], p[1], 560, 1]); }
    for (const g of glows) { if (g[0] === 'two') { for (const x of [-1.3, 1.3]) { const p = proj(new THREE.Vector3(x, 0.3, -0.5)); gl.push([p[0], p[1], 360, 0.9]); } } if (g[0] === 'pulse' && gl.length) { gl[0][2] *= g[1]; gl[0][3] *= Math.min(1.4, g[1]); } }
    orgL.position.set(focus ? focus[0] : 0, FLOOR + 1.2, focus ? focus[2] : 0);
    background(gl);
    renderer.render(stage, cam); ctx.drawImage(glc, 0, 0);
    sctx.filter = 'brightness(0.75) contrast(2.0) blur(5px)'; sctx.clearRect(0, 0, 180, 320); sctx.drawImage(glc, 0, 0, 180, 320); sctx.filter = 'none';
    ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = 0.4; ctx.drawImage(small, 0, 0, W, H); ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
    if (post.dim) { ctx.fillStyle = `rgba(4,6,14,${post.dim})`; ctx.fillRect(0, 0, W, H); }
    const vg = ctx.createRadialGradient(W / 2, H * 0.46, H * 0.3, W / 2, H * 0.5, H * 0.78); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,8,.6)'); ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    const bg = ctx.createLinearGradient(0, 1300, 0, 1920); bg.addColorStop(0, 'rgba(0,0,10,0)'); bg.addColorStop(1, 'rgba(0,0,10,.55)'); ctx.fillStyle = bg; ctx.fillRect(0, 1300, W, 620);
    L2.forEach(f => f());
    headerLogo(t); ctaShare(t);
  } else {
    background([[W / 2, 900, 520, 0.8]]);
    const a = ramp(t, CLOSE, 0.2); ctx.save(); ctx.globalAlpha = a; const lw = 330, lh = lw * logo.height / logo.width; ctx.drawImage(logo, W / 2 - lw / 2, 780 - lh / 2, lw, lh);
    ctx.font = '56px PB'; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; const s1 = 'Tulis di ', s2 = 'komentar'; const w1 = ctx.measureText(s1).width, w2 = ctx.measureText(s2).width; let x = W / 2 - (w1 + w2 + 28) / 2;
    ctx.fillStyle = '#fff'; ctx.fillText(s1, x, 1010); x += w1; ctx.fillStyle = CYEL; rr(x, 1010 - 40, w2 + 28, 80, 14); ctx.fill(); ctx.fillStyle = CNAVY; ctx.fillText(s2, x + 14, 1013); ctx.restore();
  }
  subtitle(t);
  // transisi: kedip gelap singkat tiap ganti adegan (bukan frame 0) + potongan kamera kunci salah
  const cutT = (t >= CUT_B && t < CUT_B + 0.12) ? t - CUT_B : (k > 0 && lt < 0.12 ? lt : -1);
  if (cutT >= 0) { ctx.fillStyle = `rgba(2,4,12,${0.6 * (1 - cutT / 0.12)})`; ctx.fillRect(0, 0, W, H); }
};
window.READY = true;
