"""Naqiva EP01 – synthesizes SFX + background music and mixes them under the voice.
Outputs audio/sfx.wav, audio/music.wav, audio/mix.wav"""
import json, wave
import numpy as np

SR = 44100
HERE = __file__.rsplit('/', 1)[0]
TL = json.load(open(f'{HERE}/audio/timeline.json'))
TOTAL = TL['total']
N = int(TOTAL * SR)
rng = np.random.default_rng(7)
L = {l['id']: l for l in TL['lines']}


def WF(lid, txt):
    for w in L[lid]['words']:
        if txt in w['w']:
            return w['s']
    return L[lid]['t0']


def read(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def write(p, a, ch=1):
    a = np.clip(a, -1, 1)
    with wave.open(p, 'w') as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())


def tt(d): return np.arange(int(d * SR)) / SR


def lp(x, a):  # one-pole low-pass, a in (0,1]
    y = np.empty_like(x); p = 0.0
    for i in range(len(x)):
        p += a * (x[i] - p); y[i] = p
    return y


def env(d, att=0.005, rel=None):
    t = tt(d); e = np.minimum(1, t / max(att, 1e-4))
    if rel: e *= np.exp(-t / rel)
    return e


# ---------- SFX generators ----------
def whoosh(d=0.6, f0=0.08, f1=0.5):
    n = rng.standard_normal(int(d * SR)).astype(np.float32)
    t = tt(d); sweep = np.interp(t, [0, d], [f0, f1])
    y = np.empty_like(n); p = 0.0
    for i in range(len(n)):
        p += sweep[i] * (n[i] - p); y[i] = p
    y -= lp(y, 0.01)
    e = np.sin(np.pi * t / d) ** 2
    return y * e * 1.6


def splash(d=0.5):
    n = rng.standard_normal(int(d * SR)).astype(np.float32)
    y = n - lp(n, 0.25)
    out = y * env(d, 0.002, 0.09) * 0.5
    for k in range(6):  # little droplets
        st = int((0.04 + k * 0.05 + rng.random() * 0.03) * SR)
        b = blip(0.07, 900 + rng.random() * 900, 2200 + rng.random() * 800) * 0.35
        out[st:st + len(b)] += b[:len(out) - st]
    return out


def blip(d=0.09, f0=500, f1=1100):
    t = tt(d); f = np.interp(t, [0, d], [f0, f1])
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env(d, 0.002, d / 3)


def pop(): return blip(0.08, 380, 1150) * 0.8


def boing(d=0.45):
    t = tt(d); f = 300 + 180 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.004, 0.18) * 0.8


def ding(f=1318.5, d=0.9):
    t = tt(d)
    y = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.01 * t) + 0.2 * np.sin(2 * np.pi * f * 3.02 * t)
    return y * env(d, 0.002, 0.28) * 0.45


def click():
    d = 0.05; n = rng.standard_normal(int(d * SR))
    return (n - lp(n, 0.4)) * env(d, 0.0005, 0.008) * 0.9


def thump(d=0.5):
    t = tt(d); f = np.interp(t, [0, d], [120, 40])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 0.14) * 1.2


def bubbles(d, rate=7):
    out = np.zeros(int(d * SR))
    for k in range(int(d * rate)):
        st = int(rng.random() * (d - 0.1) * SR)
        b = blip(0.05 + rng.random() * 0.04, 500 + rng.random() * 600, 1400 + rng.random() * 1200) * (0.15 + rng.random() * 0.2)
        out[st:st + len(b)] += b
    return out


def rain(d):
    n = rng.standard_normal(int(d * SR)).astype(np.float32)
    y = n - lp(n, 0.3)
    t = tt(d); e = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.8)
    return y * e * 0.12


def rumble(d):
    n = rng.standard_normal(int(d * SR)).astype(np.float32)
    y = lp(lp(n, 0.004), 0.01) * 18
    t = tt(d); e = np.sin(np.pi * t / d)
    return y * e * 0.6


def shimmer(d=1.4, base=1046.5):
    out = np.zeros(int(d * SR))
    for k, m in enumerate([1, 1.25, 1.5, 2, 2.5, 3]):
        st = int(k * 0.09 * SR); s = ding(base * m, d - k * 0.09) * 0.5
        out[st:st + len(s)] += s[:len(out) - st]
    return out


def riser(d=1.2):
    t = tt(d); f = np.interp(t, [0, d], [180, 720])
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + whoosh(d, 0.02, 0.3)[:len(t)] * 0.6
    return y * (t / d) ** 1.5


sfx = np.zeros(N, np.float32)


def put(t, a, g=1.0):
    i = int(t * SR)
    if i >= N: return
    a = a[:N - i]
    sfx[i:i + len(a)] += a * g


scenes = TL['scenes']
put(0.0, whoosh(0.5, 0.15, 0.6), 0.5); put(0.08, thump(), 0.55)
put(0.3, pop(), 0.5)
put(WF('P1', 'ترسبات') - 0.05, pop(), 0.5); put(WF('P1', 'معدنية'), ding(1568), 0.35)
put(5.35, whoosh(0.35, 0.2, 0.7), 0.4); put(5.7, boing(), 0.55)
for T in [scenes[1][0], scenes[2][0], scenes[3][0], scenes[4][0]]:
    put(T - 0.35, whoosh(0.6), 0.55); put(T - 0.02, splash(), 0.55)
# S2
put(8.3, rain(3.6), 1.0)
put(10.4, splash(0.4), 0.4)
put(10.2, rumble(2.2), 0.8)
put(11.0, bubbles(6.6, 5), 0.6)
for k in ['التربة', 'والصخور', 'الكالسيوم', 'والمانيزيوم']:
    put(WF('D2', k) - 0.05, pop(), 0.45)
# S3
put(18.15, pop(), 0.4); put(18.3, bubbles(9.5, 6), 0.55)
put(WF('P3', 'تركيز'), bubbles(1.2, 14), 0.6)
put(WF('P3', 'القاصح') - 0.05, thump(), 0.6); put(WF('P3', 'القاصح'), ding(1046.5), 0.3)
for i in range(3): put(L['P4']['t0'] + 0.1 + i * 0.25, pop(), 0.45)
put(WF('P4', 'مدينة') - 0.1, ding(1318.5), 0.25)
# S4
for i in range(14): put(29.4 + i * 0.27, click(), 0.35)
put(WF('P5', 'الشعرة') - 0.1, pop(), 0.4)
put(L['P6']['t0'] - 0.1, whoosh(0.5, 0.1, 0.4), 0.3)
put(L['P6']['t0'] + 0.3, pop(), 0.45); put(WF('P6', 'خشين') - 0.1, pop(), 0.45)
put(WF('P6', 'كيختالف') - 0.1, ding(1174.7), 0.3)
# S5
put(41.1, pop(), 0.5); put(41.45, ding(880), 0.25)
put(L['P8']['t0'] - 0.2, whoosh(0.4, 0.2, 0.6), 0.3)
put(L['P8']['t0'] + 0.5, bubbles(0.8, 12), 0.5)
put(L['P8']['t0'] + 2.5, ding(1568), 0.3)
# S6
put(50.45, whoosh(0.35, 0.2, 0.7), 0.35); put(50.8, boing(), 0.45)
put(L['P9']['t0'] - 0.1, pop(), 0.5)
put(WF('P9', 'اختار') + 0.2, ding(1318.5), 0.35); put(WF('P9', 'وكمل') + 0.2, ding(1568), 0.35)
put(58.8, riser(1.0), 0.5); put(59.6, shimmer(1.6, 783.99), 0.6); put(WF('P10', 'الحل') - 0.1, thump(), 0.5)
# S7
put(64.05, whoosh(0.5, 0.15, 0.6), 0.45); put(64.6, pop(), 0.5)
for i in range(4): put(65.3 + i * 0.15, pop(), 0.35)
put(67.4, click(), 0.8); put(67.45, ding(1568), 0.4); put(67.6, ding(2093), 0.3)
put(69.45, boing(), 0.35)
put(71.2, whoosh(0.7, 0.08, 0.4), 0.45); put(71.3, shimmer(2.2, 1046.5), 0.55)

# ---------- music (lo-fi, 96 bpm, Am–F–C–G) ----------
BPM = 96; beat = 60 / BPM
mus = np.zeros(N, np.float32)
def note(m): return 440 * 2 ** ((m - 69) / 12)
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
bar = 4 * beat
nb = int(TOTAL / bar) + 1


def pad(freqs, d):
    t = tt(d); y = np.zeros_like(t)
    for f in freqs:
        for det in (-0.6, 0.6):
            y += np.sin(2 * np.pi * (f + det) * t) + 0.25 * np.sin(2 * np.pi * 2 * (f + det) * t)
    e = np.minimum(1, t / 0.4) * np.minimum(1, (d - t) / 0.4)
    return y * e / len(freqs) * 0.09


def pluck(f, d=0.45):
    t = tt(d)
    y = np.sin(2 * np.pi * f * t) * 0.7 + np.sin(2 * np.pi * 2 * f * t) * 0.25 + np.sin(2 * np.pi * 3 * f * t) * 0.08
    return y * env(d, 0.003, 0.12) * 0.16


def kick():
    d = 0.3; t = tt(d); f = np.interp(t, [0, 0.12, d], [140, 50, 45])
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, 0.002, 0.09) * 0.5


def hat():
    d = 0.06; n = rng.standard_normal(int(d * SR))
    return (n - lp(n, 0.6)) * env(d, 0.001, 0.015) * 0.08


def mput(t, a, g=1.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    a = a[:N - i]; mus[i:i + len(a)] += a * g


TEASE0, TEASE1 = 58.8, 64.4
for b in range(nb):
    t0 = b * bar; ch = prog[b % 4]
    mput(t0, pad([note(m) for m in ch], bar + 0.3))
    mput(t0, pad([note(ch[0] - 12)], bar + 0.2), 0.8)
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12, ch[1] + 12, ch[2] + 12]
    for k in range(8):
        tk = t0 + k * beat / 2
        if TEASE0 <= tk < TEASE1: continue
        mput(tk, pluck(note(arp[k])), 0.9 if k % 2 == 0 else 0.6)
        mput(tk, hat(), 1.0)
    for k in (0, 2):
        tk = t0 + k * beat
        if TEASE0 <= tk < TEASE1 or tk < 0.2: continue
        mput(tk, kick())
# teaser: darker filtered drone instead
d = TEASE1 - TEASE0
t = tt(d); drone = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.4 * t) + 0.3 * np.sin(2 * np.pi * 110 * t * (1 + 0.002 * np.sin(t)))) * 0.1
drone *= np.minimum(1, t / 0.5) * np.minimum(1, (d - t) / 0.3)
i0 = int(TEASE0 * SR); mus[i0:i0 + len(drone)] = mus[i0:i0 + len(drone)] * 0.25 + drone
# fades
tm = np.arange(N) / SR
mus *= np.minimum(1, tm / 0.8) * np.clip((TOTAL - tm) / 2.0, 0, 1)

# ---------- ducking ----------
voice = read(f'{HERE}/audio/voice.wav')[:N]
voice = np.pad(voice, (0, N - len(voice)))
hop = 441
rms = np.sqrt(np.convolve(voice ** 2, np.ones(hop) / hop, 'same'))
act = (rms > 0.02).astype(np.float32)
act = np.convolve(act, np.ones(int(0.25 * SR)) / int(0.25 * SR), 'same')
act = np.clip(act * 2, 0, 1)
duck = 1 - 0.55 * act
mus_d = mus * duck

write(f'{HERE}/audio/sfx.wav', sfx)
write(f'{HERE}/audio/music.wav', mus)
mix = voice * 1.0 + mus_d * 0.26 + sfx * 0.42
mix = mix / max(1e-6, np.abs(mix).max()) * 0.95
write(f'{HERE}/audio/mix_raw.wav', mix)
print('peaks', np.abs(voice).max(), np.abs(mus_d).max(), np.abs(sfx).max())
