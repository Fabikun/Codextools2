from PIL import Image, ImageDraw, ImageFont
import numpy as np, os, math
S=2; W,H=360*S,640*S; FPS=30; N=150
F='/root/.fonts/'
def font(name,size): return ImageFont.truetype(F+name,size*S)
bold=font('Poppins-Bold.ttf',46); semi=font('Poppins-SemiBold.ttf',13) if os.path.exists(F+'Poppins-SemiBold.ttf') else font('Poppins-Bold.ttf',13)
logo_f=font('Poppins-Bold.ttf',17); btn_f=font('Poppins-Bold.ttf',17)
cav=ImageFont.truetype(F+'Caveat-Var.ttf',52*S)
try: cav.set_variation_by_axes([700])
except Exception as e: print('cav',e)
LIME=(158,232,79); AMBER=(240,194,127); WHITE=(255,255,255); GREY=(138,147,140); DARK=(10,13,11)

# source frames: clean segment A (1..108) stretched, then B (142..168)
B=list(range(144,166)); A_out=N-len(B)
seq=[1+round(i*104/(A_out-1)) for i in range(A_out)]+B
def src_top(a):
    rows=(a[:,0:272]>30).sum(1); w=np.where(rows>230)[0]; return w[0]
ease=lambda x: 0.5-0.5*math.cos(math.pi*min(max(x,0),1))
def eout(x): x=min(max(x,0),1); return 1-(1-x)**3

# words: (text, font, color, y)
words=[('aprende',bold,WHITE,74),('soporte',bold,WHITE,124),('respiratorio',bold,LIME,174),('sin complicarte',cav,AMBER,226)]
X0=24
os.makedirs('out',exist_ok=True)
reveal={}
for k in range(N):
    t=k/FPS
    sy=118+190*ease((t-0.15)/3.3)          # screen top (1x units)
    im=Image.new('RGB',(W,H),(0,0,0)); d=ImageDraw.Draw(im,'RGBA')
    # header: codex mark + cyber day label
    cx,cy=X0+8,34
    r=7
    d.polygon([((cx)*S,(cy-r)*S),((cx+r)*S,cy*S),(cx*S,(cy+r)*S),((cx-r)*S,cy*S)],outline=LIME,width=3)
    d.text(((cx+15)*S,cy*S),'CODEX',font=logo_f,fill=WHITE,anchor='lm')
    lab='CYBER DAY'
    ls=4.0*S; x=(360-24)*S; 
    chars=list(lab); widths=[d.textlength(c,font=semi) for c in chars]
    tot=sum(widths)+ls*(len(chars)-1); x-=tot
    pulse=0.75+0.25*math.sin(t*6)
    col=tuple(int(c*pulse) for c in LIME)
    for c,w in zip(chars,widths): d.text((x,cy*S),c,font=semi,fill=col,anchor='lm'); x+=w+ls
    # words (behind screen): reveal once uncovered
    for i,(txt,f,colr,y) in enumerate(words):
        bottom=y+44
        if i not in reveal and (sy>bottom-6 or (i==0 and t>0.1)): reveal[i]=t
        if i in reveal:
            p=eout((t-reveal[i])/0.35)
            layer=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer)
            ld.text((X0*S,(y+14*(1-p))*S),txt,font=f,fill=colr+(int(255*p),),anchor='lt')
            im.paste(layer,(0,0),layer)
            if i==3 and p>0:  # underline stroke under the handwritten line
                L=d.textlength(txt,font=f)*eout((t-reveal[i]-0.15)/0.4)
                d.line([(X0*S,(y+62)*S),(X0*S+L,(y+60)*S)],fill=AMBER,width=3*S)
    # screen crop from source, placed at sy
    a=np.array(Image.open('src/%03d.png'%seq[k]).convert('RGB'))
    top=src_top(a.mean(2))
    c=np.zeros((188,360,3),np.uint8); part=a[top:top+188,0:360]; c[:part.shape[0]]=part
    c[:22,276:]=0   # drop leftover source logo
    crop=Image.fromarray(c)
    crop=crop.resize((crop.width*S,crop.height*S),Image.LANCZOS)
    im.paste(crop,(0,int(sy*S)))
    # cyber day CTA button at the end
    if t>3.2:
        p=eout((t-3.2)/0.4)
        bw,bh=260,46; bx=(360-bw)/2-6; by=560+20*(1-p)
        layer=Image.new('RGBA',(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer)
        ld.rounded_rectangle([bx*S,by*S,(bx+bw)*S,(by+bh)*S],radius=10*S,fill=LIME+(int(255*p),))
        ld.text(((bx+bw/2)*S,(by+bh/2)*S),'cyber day codex',font=btn_f,fill=DARK+(int(255*p),),anchor='mm')
        tx=(bx+bw/2+d.textlength('cyber day codex',font=btn_f)/S/2+12); ty=by+bh/2
        ld.polygon([(tx*S,(ty-6)*S),((tx+9)*S,ty*S),(tx*S,(ty+6)*S)],fill=DARK+(int(255*p),))
        im.paste(layer,(0,0),layer)
    im.save('out/%03d.png'%k)
print('ok')
