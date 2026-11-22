"""Synthesise the SFX kit (whoosh, pop, ding, impact, cha-ching, riser, zap) as 48k stereo WAVs."""
import numpy as np, wave, sys, os
SR = 48000
rng = np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def env(n, a, r):  # attack / release in samples-fraction
    e = np.ones(n); A=int(n*a); R=int(n*r)
    if A: e[:A]=np.linspace(0,1,A)
    if R: e[-R:]=np.linspace(1,0,R)**2
    return e
def lp(x, k):  # one-pole lowpass, k in (0,1) per-sample or array
    y=np.zeros_like(x); s=0.0; k=np.broadcast_to(k,x.shape)
    for i in range(len(x)): s+=k[i]*(x[i]-s); y[i]=s
    return y
def norm(x, peak_db=-6):
    return x/ (np.max(np.abs(x))+1e-9) * 10**(peak_db/20)
def save(name, x, pan=None):
    x=np.clip(x,-1,1)
    st=np.stack([x,x],1) if pan is None else np.stack([x*pan[0],x*pan[1]],1)
    with wave.open(name,'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st*32767).astype('<i2').tobytes())

def whoosh(d=0.45):
    n=int(SR*d); tt=np.linspace(0,1,n)
    noise=rng.standard_normal(n)
    sweep=0.02+0.25*np.sin(np.pi*tt)**2            # filter opens and closes
    x=lp(noise,sweep)-lp(noise,sweep*0.25)          # band-pass-ish
    return norm(x*np.sin(np.pi*tt)**1.5, -6)
def pop(d=0.12):
    tt=t(d); f=900*np.exp(-tt*40)+300
    x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*45)
    return norm(x,-6)
def ding(d=1.0):
    tt=t(d); x=sum(a*np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,a,k in [(1568,1,4),(3136,.45,7),(4704,.2,10),(2093,.3,5)])
    return norm(x*env(len(tt),0.003,0),-6)
def impact(d=0.9):
    tt=t(d); f=120*np.exp(-tt*6)+38
    body=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*5)
    crack=lp(rng.standard_normal(len(tt)),0.35)*np.exp(-tt*30)
    x=np.tanh(2.2*(body+0.6*crack))
    return norm(x,-4)
def cha_ching(d=1.1):
    tt=t(d); n=len(tt)
    click=lp(rng.standard_normal(n),0.6)*np.exp(-tt*80)
    bell=np.zeros(n)
    for start,f in [(0.06,2637),(0.16,3520)]:
        s=int(start*SR); u=tt[:n-s]
        bell[s:]+=sum(a*np.sin(2*np.pi*f*m*u)*np.exp(-u*k) for m,a,k in [(1,1,5),(2.01,.4,8),(2.76,.25,11)])
    coins=np.zeros(n)
    for i in range(14):
        s=int((0.1+0.05*i+0.01*rng.random())*SR); 
        if s>=n: break
        u=tt[:n-s]; coins[s:]+=0.25*np.sin(2*np.pi*(5000+2000*rng.random())*u)*np.exp(-u*60)
    return norm(0.8*click+bell+coins,-6)
def riser(d=1.5):
    tt=t(d); n=len(tt); p=tt/d
    f=200+1800*p**2
    tone=np.sin(2*np.pi*np.cumsum(f)/SR)+0.5*np.sin(2*np.pi*np.cumsum(f*1.5)/SR)
    noise=lp(rng.standard_normal(n),0.02+0.5*p**2)
    x=(0.5*tone+noise)*p**2.2
    x*=env(n,0,0.03)
    return norm(x,-6)
def zap(d=0.25):
    tt=t(d); f=2400*np.exp(-tt*18)+120
    x=np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-tt*14)
    return norm(lp(x,0.35),-8)

out=sys.argv[1]
os.makedirs(out,exist_ok=True)
for name,fn in [('whoosh',whoosh),('pop',pop),('ding',ding),('impact',impact),('cha_ching',cha_ching),('riser',riser),('zap',zap)]:
    save(os.path.join(out,name+'.wav'), fn()); print(name)
