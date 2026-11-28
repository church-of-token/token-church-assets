"""토큰교 릴스 BGM 생성기 (저작권 걱정 없는 자작 음원).

분위기: 근엄한 성당 오르간으로 시작 → 훅이 끝나는 순간 비트 드랍 (밈 릴스 문법).
사용: python3 tools/make_bgm.py <길이초> <드랍초> <out.wav> [--bpm 140] [--key A]
릴스 합치기: ffmpeg -i reel.mp4 -i bgm.wav -map 0:v -map 1:a -c:v copy -c:a aac -shortest out.mp4
"""
import sys, argparse, subprocess, os
import numpy as np
from scipy.signal import butter, lfilter

SR = 44100
ap = argparse.ArgumentParser()
ap.add_argument("dur", type=float); ap.add_argument("drop", type=float); ap.add_argument("out")
ap.add_argument("--bpm", type=float, default=140); ap.add_argument("--seed", type=int, default=7)
a = ap.parse_args()
rng = np.random.default_rng(a.seed)
N = int(a.dur * SR); t = np.arange(N) / SR
mix = np.zeros(N)

def hz(m): return 440 * 2 ** ((m - 69) / 12)
def env(n, att, rel):
    e = np.ones(n); A = min(int(att*SR), n); R = min(int(rel*SR), n)
    e[:A] = np.linspace(0, 1, A); e[n-R:] *= np.linspace(1, 0, R); return e
def bp(x, lo, hi, order=2):
    b, aa = butter(order, [lo/(SR/2), hi/(SR/2)], btype="band"); return lfilter(b, aa, x)
def hp(x, f):
    b, aa = butter(2, f/(SR/2), btype="high"); return lfilter(b, aa, x)

# 코드 진행 (A단조: Am - F - C - G), 한 코드 = 2박
beat = 60 / a.bpm
prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
chord_len = beat * 4  # 1마디(140bpm 기준 약 1.7초)

# 오르간: 하모닉 합성 + 약한 비브라토
draw = [(1, 1.0), (2, .55), (3, .3), (4, .25), (6, .12), (8, .1)]
i = 0; st = 0.0
while st < a.dur:
    s0 = int(st*SR); s1 = min(int((st+chord_len)*SR), N); n = s1 - s0
    tt = np.arange(n) / SR; vib = 1 + .003*np.sin(2*np.pi*5.5*tt)
    seg = np.zeros(n)
    for m in prog[i % 4] + [prog[i % 4][0] - 12]:
        for h, g in draw:
            seg += g * np.sin(2*np.pi*hz(m)*h*tt*vib)
    seg *= env(n, .08, .12)
    # 드랍 전엔 크고, 드랍 후엔 배경으로
    gain = np.where(np.arange(s0, s1)/SR < a.drop, .16, .08)
    mix[s0:s1] += seg * gain
    st += chord_len; i += 1

def place(sig, at, g=1.0):
    s = int(at*SR)
    if s >= N: return
    e = min(N, s+len(sig)); mix[s:e] += g*sig[:e-s]

# 드럼 소리
kn = int(.35*SR); kt = np.arange(kn)/SR
kick = np.sin(2*np.pi*(45*kt + (110/18)*(1-np.exp(-18*kt)))) * np.exp(-9*kt)
sn = int(.22*SR); stt = np.arange(sn)/SR
snare = bp(rng.standard_normal(sn), 1200, 6000)*np.exp(-22*stt)*.4 + np.sin(2*np.pi*190*stt)*np.exp(-30*stt)*.5
hn = int(.05*SR); hat = hp(rng.standard_normal(hn), 7000)*np.exp(-np.arange(hn)/SR*140)*.12
riser_n = int(min(a.drop, 1.2)*SR)
riser = hp(rng.standard_normal(riser_n), 3000) * np.linspace(0, 1, riser_n)**2 * .15

# 드랍 직전 라이저 + 드랍 순간 임팩트
place(riser, a.drop - riser_n/SR)
place(kick*1.4, a.drop)

# 드랍 후 트랩풍 하프타임 비트
duck = np.ones(N)
pos = a.drop; k = 0
end = a.dur - 0.9  # 마지막 0.9초는 오르간만 남겨 여운
while pos < end:
    step = k % 16
    if step in (0, 10):  # 킥
        place(kick, pos)
        s = int(pos*SR); e = min(N, s+int(.25*SR)); duck[s:e] = np.minimum(duck[s:e], np.linspace(.35, 1, e-s))
    if step in (8,):  # 스네어 (하프타임 3박)
        place(snare, pos)
    if step % 2 == 0:
        place(hat, pos, 1.0 if step % 4 == 2 else .6)
    if step in (14, 15) and (k // 16) % 2 == 1:  # 하이햇 롤
        place(hat, pos + beat/8, .6)
    # 808 베이스: 코드 루트
    if step in (0, 10):
        ci = int(pos // chord_len) % 4
        root = prog[ci][0] - 24
        bn = int(beat*1.5*SR); bt = np.arange(bn)/SR
        bass = np.sin(2*np.pi*hz(root)*bt) * np.exp(-2.2*bt) * env(bn, .005, .05)
        place(np.tanh(bass*2)*.35, pos)
    pos += beat/4; k += 1

mix *= duck ** .5
mix[-int(.6*SR):] *= np.linspace(1, 0, int(.6*SR))
mix = np.tanh(mix * 1.2) / 1.2
st = np.stack([mix, mix], 1)
tmp = a.out + ".raw.wav"
import wave
with wave.open(tmp, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())
# 성당 잔향 + 인스타 기준 음량(-14 LUFS)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
                "aecho=0.8:0.6:60|120:0.25|0.15,loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), a.out], check=True)
os.remove(tmp); print("bgm ok", a.out)
