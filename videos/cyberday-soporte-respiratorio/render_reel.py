# Reel 1080x1920, 5 s. Screen drops on each punch (synced to the hit sounds); a word is revealed per hit.
from PIL import Image, ImageDraw, ImageFont
import numpy as np, os, math, random
S=3; W,H=360*S,640*S; FPS=30; N=150
F='/root/.fonts/'
def font(name,size): return ImageFont.truetype(F+name,int(size*S))
bold=font('Poppins-Bold.ttf',40); semi=font('Poppins-SemiBold.ttf',12)
logo_f=font('Poppins-Bold.ttf',16); ph_f=font('Poppins-SemiBold.ttf',17); stk_f=font('Poppins-Bold.ttf',22)
cav=ImageFont.truetype(F+'Caveat-Var.ttf',46*S)
try: cav.set_variation_by_axes([700])
except Exception: pass
LIME=(158,232,79); AMBER=(240,194,127); WHITE=(255,255,255); DARK=(10,13,11)

# timeline: src 10..135 then cut to 142..165 (skips the frames where the old title moves over the screen)
seq=list(range(10,136))+list(range(142,166))
HITS=[62,93,126]           # output frames of the punch sounds (src 72,103,136)
STOPS=[166,208,250,352]    # screen top (in 360x640 units) before hit1, after hit1, hit2, hit3
words=[('aprende',bold,WHITE,122),('soporte',bold,WHITE,164),('respiratorio',bold,LIME,206),('sin complicarte',cav,AMBER,244)]
X0=24
def eout(x): x=min(max(x,0),1); return 1-(1-x)**3
def eback(x):
    x=min(max(x,0),1); c=1.9; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def src_top(a):
    rows=(a[:,0:272]>30).sum(1); w=np.where(rows>230)[0]; return w[0]
random.seed(3)
os.makedirs('out2',exist_ok=True)
for k in range(N):
    # screen y: step down at each hit with overshoot
    sy=STOPS[0]; last=None
    for i,h in enumerate(HITS):
        if k>=h: sy=STOPS[i]+(STOPS[i+1]-STOPS[i])*eback((k-h)/7); last=h
    shake=(0,0)
    if last is not None and k-last<8:
        amp=5*(1-(k-last)/8); shake=(random.uniform(-amp,amp),random.uniform(-amp,amp))
    im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im)
    # header (below reels top UI)
    cx,cy=X0+8,100; r=7
    d.polygon([(cx*S,(cy-r)*S),((cx+r)*S,cy*S),(cx*S,(cy+r)*S),((cx-r)*S,cy*S)],outline=LIME,width=3)
    d.text(((cx+15)*S,cy*S),'CODEX',font=logo_f,fill=WHITE,anchor='lm')
    ls=4*S; chars=list('CYBER DAY'); ws=[d.textlength(c,font=semi) for c in chars]
    x=(360-24)*S-(sum(ws)+ls*(len(chars)-1)); pul=0.75+0.25*math.sin(k/FPS*6)
    for c,w in zip(chars,ws): d.text((x,cy*S),c,font=semi,fill=tuple(int(v*pul) for v in LIME),anchor='lm'); x+=w+ls
    # words: drawn behind the screen; each pops in when the screen uncovers it
    for i,(txt,f,col,y) in enumerate(words):
        start=0 if i==0 else HITS[i-1]+1
        if k<start: continue
        p=eout((k-start)/6); sc=1.12-0.12*p
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        ld.text((X0*S,(y+8*(1-p))*S),txt,font=f,fill=col+(int(255*min(1,p*1.5)),),anchor='lt')
        if sc!=1:
            lay=lay.resize((int(W*sc),int(H*sc)),Image.BICUBIC)
            ox=int(X0*S*(sc-1)); oy=int(y*S*(sc-1)); lay=lay.crop((ox,oy,ox+W,oy+H))
        im.paste(lay,(0,0),lay)
        if i==3:
            L=d.textlength(txt,font=f)*eout((k-start-3)/10)
            if L>0: d.line([(X0*S,(y+52)*S),(X0*S+L,(y+50)*S)],fill=AMBER,width=3*S)
    # screen
    sf=seq[k]
    a=np.array(Image.open('src/%03d.png'%sf).convert('RGB')); top=src_top(a.mean(2))
    c=np.zeros((188,360,3),np.uint8); part=a[top:top+188,0:360]; c[:part.shape[0]]=part
    c[:22,276:]=0
    crop=Image.fromarray(c).resize((360*S,188*S),Image.LANCZOS)
    # sticker over the old burned-in title (src 103..135), slams in with hit 2
    if 103<=sf<=135:
        p=eout((sf-103)/3)
        sw,sh=150,58
        st=Image.new('RGBA',(sw*S,sh*S),(0,0,0,0)); sd=ImageDraw.Draw(st)
        sd.rounded_rectangle([0,0,sw*S-1,sh*S-1],radius=10*S,fill=LIME)
        sd.text((sw*S/2,sh*S/2),'cyber day',font=stk_f,fill=DARK,anchor='mm')
        sc=1.6-0.6*p
        st=st.resize((int(sw*S*sc),int(sh*S*sc)),Image.BICUBIC).rotate(-5,expand=True,resample=Image.BICUBIC)
        cx2,cy2=175*S,40*S
        crop.paste(st,(int(cx2-st.width/2),int(cy2-st.height/2)),st)
    im.paste(crop,(int(shake[0]*S),int((sy+shake[1])*S)))
    # phrase pointing to Meta's own CTA button (revealed by hit 3, drawn over the screen's clearance)
    if k>=HITS[2]+5:
        p=eout((k-HITS[2]-5)/6); al=int(255*p); py=324+8*(1-p)
        lay=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lay)
        a1='toca '; a2='más información'
        ld.text((X0*S,py*S),a1,font=ph_f,fill=WHITE+(al,),anchor='lm')
        x2=X0*S+ld.textlength(a1,font=ph_f)
        ld.text((x2,py*S),a2,font=ph_f,fill=LIME+(al,),anchor='lm')
        ax=(x2+ld.textlength(a2,font=ph_f))/S+12; bob=3*math.sin((k-HITS[2])/FPS*2*math.pi*2.2)
        ay=py+bob
        ld.line([(ax*S,(ay-9)*S),(ax*S,(ay+7)*S)],fill=LIME+(al,),width=3*S)
        ld.polygon([((ax-6)*S,(ay+2)*S),((ax+6)*S,(ay+2)*S),(ax*S,(ay+10)*S)],fill=LIME+(al,))
        im.paste(lay,(0,0),lay)
    im.save('out2/%03d.png'%k)
print('ok')
