from PIL import Image, ImageFilter
import numpy as np
def top(a):
    rows=(a.mean(2)[:,0:272]>30).sum(1); w=np.where(rows>230)[0]; return w[0]
def crop(i,h=100):
    a=np.array(Image.open('src/%03d.png'%i).convert('RGB')); t=top(a); return a[t:t+h,0:360]
refA=np.median(np.stack([crop(i) for i in range(2,104,2)]),0)
refB=np.median(np.stack([crop(i) for i in range(142,166)]),0)
ref=refB.copy()
ref[:44]=refA[:44]                      # top rows: monitor UI, clean in early frames
row=np.median(refB[44:,140:190],1)      # lower rows: person sits right; fill with the row's dark background
ref[44:,190:260]=row[:,None,:]
ref=ref.astype(np.uint8)
np.save('ref.npy',ref); Image.fromarray(ref).resize((720,200)).save('ref.png')
Y0,Y1,X0,X1=0,100,92,252
def F(m,f): return np.array(Image.fromarray((m*255).astype(np.uint8)).filter(f))>0
def clean_arr(c):
    # replace the old white title (and the light-grey popup it sits on, which vanishes a few frames later anyway)
    c=c.copy()
    reg=c[Y0:Y1,X0:X1]
    m=F(reg.astype(int).min(2)>=165,ImageFilter.MaxFilter(5))
    reg[m]=ref[Y0:Y1,X0:X1][m]
    return c
def clean(i): return clean_arr(crop(i,100))
if __name__=='__main__':
    out=[np.vstack([crop(i),clean(i)]) for i in [107,109,111,113]]
    Image.fromarray(np.hstack(out)).resize((1440*2,400)).save('clean_test.png')
