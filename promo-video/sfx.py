# Generates out/sfx.wav: ambient pad + whooshes at scene cuts + bass impacts + UI clicks
import numpy as np, wave
SR=44100; DUR=40.0; n=int(SR*DUR); t=np.arange(n)/SR
rng=np.random.default_rng(1); out=np.zeros((n,2))
def add(sig,at,gain=1.0,pan=0.0):
    i=int(at*SR); j=min(n,i+len(sig)); s=sig[:j-i]*gain
    out[i:j,0]+=s*(1-pan)/1; out[i:j,1]+=s*(1+pan)/1
# pad: Am9-ish chord, slow tremolo, swells
chords=[[110,164.8,220,261.6,329.6],[87.3,130.8,174.6,220,261.6],[98,146.8,196,246.9,293.7],[82.4,123.5,164.8,207.7,246.9]]
pad=np.zeros(n)
for k,ch in enumerate(chords*3):
    a=k*DUR/12; b=a+DUR/12+1.0; m=(t>=a)&(t<b); tt=t[m]-a
    env=np.minimum(1,tt/0.8)*np.minimum(1,(b-a-tt)/1.0)
    for f in ch: pad[m]+=env*(np.sin(2*np.pi*f*t[m])+0.3*np.sin(2*np.pi*f*2.003*t[m]))
pad*= (0.7+0.3*np.sin(2*np.pi*0.25*t)); pad/=np.abs(pad).max(); pad*=0.10
pad*=np.minimum(1,t/1.5)*np.minimum(1,(DUR-t)/1.5)
out[:,0]+=pad; out[:,1]+=pad
# pulse beat (soft kick each 0.5s from 4.5s to 31)
def kick(L=0.35,f0=120,f1=40):
    tt=np.arange(int(SR*L))/SR; f=f1+(f0-f1)*np.exp(-tt*25); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-tt*9)
for b in np.arange(4.0,36.0,0.5): add(kick(),b,0.22)
# whoosh
def whoosh(L=0.9):
    m=int(SR*L); x=rng.standard_normal(m); tt=np.arange(m)/SR
    # moving bandpass via simple resonant filter sweep
    y=np.zeros(m); y1=y2=0.0
    for i in range(m):
        fc=300+3500*np.sin(np.pi*tt[i]/L)**2; r=0.97; w=2*np.pi*fc/SR
        yi=x[i]+2*r*np.cos(w)*y1-r*r*y2; y[i]=yi; y2=y1; y1=yi
    y/=np.abs(y).max(); return y*np.sin(np.pi*tt/L)**2
W=whoosh()
def impact(L=1.6):
    tt=np.arange(int(SR*L))/SR; return np.sin(2*np.pi*(45+60*np.exp(-tt*8))*tt)*np.exp(-tt*3)+0.3*rng.standard_normal(len(tt))*np.exp(-tt*30)
def click(f=1800):
    tt=np.arange(int(SR*0.06))/SR; return np.sin(2*np.pi*f*tt)*np.exp(-tt*80)
for i,c in enumerate([4,9,14,19,24,28.5,32.5,36]): add(W,c-0.55,0.45,(-1)**i*0.4); add(impact(),c,0.35)
add(impact(),0.3,0.45); add(impact(2.5),36.1,0.55)
for c in [32.95,33.45,33.95,34.45]: add(click(2600),c,0.3)
for c in [8.05, 17.6]: add(click(1500),c,0.35)            # cursor click, booking btn
for c in [20.1,20.55,21.0,21.45,21.9]: add(click(2200),c,0.25)  # POS taps
add(click(1200),22.5,0.3)
for c in [17.9,22.75,27.2]:  # success chime
    tt=np.arange(int(SR*0.8))/SR; add((np.sin(2*np.pi*880*tt)+np.sin(2*np.pi*1320*tt))*np.exp(-tt*5)*0.5,c,0.25)
out/=max(1,np.abs(out).max()/0.9)
w=wave.open('out/sfx.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close(); print('ok')
