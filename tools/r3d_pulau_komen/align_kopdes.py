"""Timing Pulau Komen Hari 2 dari jeda VO nyata: DP mencocokkan frasa (tanda baca) ke segmen bicara."""
import json, re, subprocess
LEAD = 0.3
txt = open('naskah.txt').read()
dur = float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','vo.wav']))
log = subprocess.run(['ffmpeg','-i','vo.wav','-af','silencedetect=n=-30dB:d=0.12','-f','null','-'],capture_output=True,text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
sil = list(zip(st, en))
segs = []; t = 0.0
for a, b in sil:
    if a - t > 0.05: segs.append([t, a])
    t = b
if dur - t > 0.05: segs.append([t, dur])
# frasa
paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
phr = []  # (words, strong, para_idx)
for pi, p in enumerate(paras):
    for m in re.finditer(r'[^.,?!:]+[.,?!:]*(\.\.\.)?', p):
        s = m.group(0).strip()
        if not s or not re.search(r'\w', s): 
            if phr and s: phr[-1] = (phr[-1][0] + [s], phr[-1][1], phr[-1][2])
            continue
        phr.append((s.split(), s[-1] in '.?!', pi))
# gabung frasa sangat pendek? tidak
n, m = len(phr), len(segs)
chars = [sum(len(w) + 1 for w in p[0]) for p in phr]
speech = sum(b - a for a, b in segs); rate = speech / sum(chars)
INF = 1e18
def seg_dur(i, j): return sum(segs[k][1] - segs[k][0] for k in range(i, j))
gap_after = [ (segs[k+1][0] - segs[k][1]) if k + 1 < m else 1.0 for k in range(m)]
# dp[p][s] = biaya terbaik frasa 0..p-1 memakai segmen 0..s-1
import math
dp = [[INF] * (m + 1) for _ in range(n + 1)]; bk = [[0] * (m + 1) for _ in range(n + 1)]
dp[0][0] = 0
for p in range(1, n + 1):
    exp = chars[p - 1] * rate
    for s in range(p, m + 1):
        best = INF; arg = 0
        for r in range(p - 1, s):
            if dp[p - 1][r] >= INF: continue
            d = seg_dur(r, s); c = (d - exp) ** 2 / max(exp, 0.3)
            g = gap_after[s - 1]
            if phr[p - 1][1] and g < 0.25: c += 0.6
            if s - r > 1: c += 0.15 * (s - r - 1)
            if dp[p - 1][r] + c < best: best = dp[p - 1][r] + c; arg = r
        dp[p][s] = best; bk[p][s] = arg
# m >= n diasumsikan
assert m >= n, (m, n)
assign = []; s = m
for p in range(n, 0, -1):
    r = bk[p][s]; assign.append((r, s)); s = r
assign.reverse()
words = []
for (ws, strong, pi), (r, s) in zip(phr, assign):
    sub = segs[r:s]; tot = sum(b - a for a, b in sub); w = [len(x) + 1 for x in ws]; W_ = sum(w)
    # peta posisi kumulatif -> waktu, melompati jeda internal
    def tmap(f):
        x = f * tot
        for a, b in sub:
            if x <= b - a: return a + x
            x -= b - a
        return sub[-1][1]
    acc = 0
    for x, wi in zip(ws, w):
        words.append({'w': x, 's': round(tmap(acc / W_) + LEAD, 3), 'e': round(tmap((acc + wi) / W_) + LEAD, 3), 'p': pi})
        acc += wi
# chunk subtitle: per frasa, maks 4 kata
chunks = []
k = 0
for (ws, strong, pi) in phr:
    grp = [ws[i:i + 4] for i in range(0, len(ws), 4)]
    if len(grp) > 1 and len(grp[-1]) == 1: grp[-2] += grp[-1]; grp.pop()
    for g in grp:
        wsx = words[k:k + len(g)]; k += len(g)
        chunks.append({'text': ' '.join(g), 's': wsx[0]['s'], 'e': wsx[-1]['e'], 'p': pi})
chunks[0]['s'] = 0.0
for i, c in enumerate(chunks):
    nxt = chunks[i + 1]['s'] if i + 1 < len(chunks) else c['e'] + 0.5
    c['show_end'] = round(min(nxt, c['e'] + 0.6), 3)
pstart = {}
for c in chunks: pstart.setdefault(c['p'], c['s'])
TOTAL = round(dur + LEAD + 1.0, 2)
json.dump({'lead': LEAD, 'words': words, 'chunks': chunks, 'para_start': [pstart[i] for i in range(len(paras))], 'total': TOTAL, 'vo_end': dur + LEAD}, open('timing.json', 'w'), indent=1, ensure_ascii=False)
for i, p in enumerate(paras): print(i, pstart[i], p[:60])
print('n frasa', n, 'segmen', m, 'TOTAL', TOTAL)
