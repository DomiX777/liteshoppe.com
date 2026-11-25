"""HairLab EP01 – builds the voice track, lip-sync curves and timeline.js.

Inputs : audio/host.wav, audio/drop.wav (+ *_words.json word timings)
Outputs: audio/voice.wav, timeline.js (lines, words, scenes, mouth curves)
"""
import json, wave, re
import numpy as np

SR = 44100
FPS = 30
TOTAL = 75.0
HERE = __file__.rsplit('/', 1)[0]

# Placement of every line on the video timeline (seconds)
ORDER = [
    ('P1', 0.5), ('D1', 5.6),
    ('P2', 8.8), ('D2', 12.0),
    ('P3', 18.5), ('P4', 23.4),
    ('P5', 28.9), ('P6', 34.0),
    ('P7', 41.4), ('P8', 45.9),
    ('D3', 50.8), ('P9', 52.6), ('P10', 59.0),
    ('P11', 65.1), ('D4', 69.6),
]
SCENES = [[0, 8.3], [8.3, 18], [18, 28.4], [28.4, 41], [41, 50.4], [50.4, 64.4], [64.4, 75]]

KEY = ['ترسبات', 'معدنية', 'السبب', 'الجبال', 'الأرض', 'التربة', 'والصخور', 'الكالسيوم', 'والمانيزيوم',
       'تركيز', 'القاصح', 'والقساوة', 'مدينة', 'لمدينة', 'يترسبو', 'يتشبثو', 'الشعرة', 'خشين', 'لمعة',
       'قشرة', 'جفاف', 'الكالكير', 'اختبار', 'قساوة', 'شعرك', 'بارد', 'الحل', 'تابعنا', 'أسرار', 'ندير', 'الجاية']


def read(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


def split_host(words):
    lines, cur = [], []
    for w in words:
        if w['text'].startswith('['):
            continue
        cur.append(w)
        t = w['text']
        if (t.endswith('؟') or t.endswith('!') or (t.endswith('.') and not t.endswith('...'))):
            lines.append(cur); cur = []
    if cur:
        lines.append(cur)
    return lines


def split_drop(words):
    lines, cur = [], []
    for w in words:
        if w['text'].startswith('['):
            if cur: lines.append(cur)
            cur = []
            continue
        cur.append(w)
    if cur: lines.append(cur)
    return lines


host_w = json.load(open(f'{HERE}/audio/host_words.json'))['words']
drop_w = json.load(open(f'{HERE}/audio/drop_words.json'))['words']
H = split_host(host_w); D = split_drop(drop_w)
assert len(H) == 11, len(H)
assert len(D) == 4, len(D)
src = {'P': read(f'{HERE}/audio/host.wav'), 'D': read(f'{HERE}/audio/drop.wav')}
segs = {}
for i, l in enumerate(H): segs[f'P{i+1}'] = l
for i, l in enumerate(D): segs[f'D{i+1}'] = l


def clip_bounds(key):
    spk, idx = key[0], int(key[1:])
    group = H if spk == 'P' else D
    l = group[idx - 1]
    s = l[0]['start'] - 0.06
    e = l[-1]['end'] + 0.12
    if idx < len(group):
        e = min(e, group[idx][0]['start'] - 0.03)
    if idx > 1:
        s = max(s, group[idx - 2][-1]['end'] + 0.02)
    return max(0, s), e


voice = {'P': np.zeros(int(TOTAL * SR), np.float32), 'D': np.zeros(int(TOTAL * SR), np.float32)}
lines_out = []
for key, T in ORDER:
    s, e = clip_bounds(key)
    a = src[key[0]][int(s * SR):int(e * SR)].copy()
    f = int(0.012 * SR)
    a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    i0 = int(T * SR)
    voice[key[0]][i0:i0 + len(a)] += a
    words = []
    for w in segs[key]:
        txt = w['text']
        clean = re.sub(r'[.,،!؟?:…]+$', '', txt)
        words.append({'w': txt, 's': round(T + w['start'] - s, 3), 'e': round(T + w['end'] - s, 3),
                      'k': 1 if clean in KEY else 0})
    lines_out.append({'id': key, 'spk': key[0], 't0': round(T, 3), 't1': round(T + e - s, 3), 'words': words})
    print(key, f'{T:6.2f} -> {T+e-s:6.2f}', ' '.join(w['w'] for w in words))

# overlap check
for a, b in zip(lines_out, lines_out[1:]):
    assert a['t1'] <= b['t0'] + 1e-6, (a['id'], b['id'])


def mouth(sig):
    n = int(TOTAL * FPS); hop = SR // FPS
    out = np.zeros(n)
    for i in range(n):
        seg = sig[i * hop:(i + 1) * hop + hop // 2]
        out[i] = np.sqrt(np.mean(seg ** 2)) if len(seg) else 0
    ref = np.percentile(out[out > 0.01], 90) if (out > 0.01).any() else 1
    out = np.clip(out / ref, 0, 1)
    out[out < 0.08] = 0
    # light smoothing: fast attack, quicker release
    sm = np.zeros_like(out)
    for i in range(n):
        p = sm[i - 1] if i else 0
        sm[i] = p + (out[i] - p) * (0.75 if out[i] > p else 0.55)
    return [round(float(x), 2) for x in sm]


mix = voice['P'] + voice['D']
peak = np.abs(mix).max()
mix = mix / peak * 0.89
with wave.open(f'{HERE}/audio/voice.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

TL = {'fps': FPS, 'total': TOTAL, 'scenes': SCENES, 'lines': lines_out,
      'mouthP': mouth(voice['P']), 'mouthD': mouth(voice['D'])}
open(f'{HERE}/timeline.js', 'w').write('window.TL=' + json.dumps(TL, ensure_ascii=False) + ';\n')
json.dump(TL, open(f'{HERE}/audio/timeline.json', 'w'), ensure_ascii=False)
print('ok')
