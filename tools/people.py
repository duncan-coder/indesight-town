import sys, colorsys
import numpy as np
from PIL import Image
from scipy import ndimage
src,out=sys.argv[1],sys.argv[2]
TH=96  # target figure height in px (world = TH*0.25)
a=np.asarray(Image.open(src).convert('RGB')).astype(np.int32)
r,g,b=a[...,0],a[...,1],a[...,2]
m=np.minimum(r,b)-g
alpha=np.clip((150-m)/90.0,0,1)
fr=alpha<1; lim=g+40
rgb=a.copy()
rgb[...,0]=np.where(fr,np.minimum(r,np.maximum(lim,r*alpha)),r)
rgb[...,2]=np.where(fr,np.minimum(b,np.maximum(lim,b*alpha)),b)
lab,n=ndimage.label(alpha>0.4)
objs=ndimage.find_objects(lab)
comps=[(s, (lab[s]>0).sum()) for s in objs]
comps=[c for c in comps if c[1]>3000]
comps.sort(key=lambda c:(round(c[0][0].start/300), c[0][1].start))
print('components',len(comps),[ (c[0][0].start,c[0][1].start) for c in comps])
assert len(comps)==8
hmax=max(c[0][0].stop-c[0][0].start for c in comps)
k=TH/hmax
frames=[]
for (sl,_) in comps:
    ys,xs=sl
    crop=np.dstack([rgb[sl],(alpha[sl]*255)]).astype(np.uint8)
    im=Image.fromarray(crop,'RGBA')
    # horizontal anchor: centre of the head (top 40%)
    al=alpha[sl]; top=al[:int(al.shape[0]*.4)]
    cx=np.nonzero(top.sum(0)>0.5)[0]; hc=(cx.min()+cx.max())/2
    w=max(1,round(im.width*k)); h=max(1,round(im.height*k))
    im=im.resize((w,h),Image.LANCZOS)
    frames.append((im,hc*k))
CW=max(max(f[1],f[0].width-f[1]) for f in frames)*2+4; CW=int(np.ceil(CW)); CH=TH+2
def recolor(img, scarf_h=None, hair=None):
    px=np.asarray(img).astype(np.float32)/255.
    H,W=px.shape[:2]; o=px.copy()
    hsv=np.zeros((H,W,3))
    for y in range(H):
        for x in range(W):
            hsv[y,x]=colorsys.rgb_to_hsv(*px[y,x,:3])
    h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]; A=px[...,3]>.5
    if scarf_h is not None:
        red=A&((h<.05)|(h>.93))&(s>.5)&(v>.3)
        lab,n=ndimage.label(red,structure=np.ones((3,3)))
        sizes=ndimage.sum(red,lab,range(1,n+1))
        keep=np.isin(lab,[i+1 for i,sz in enumerate(sizes) if sz>=25])
        for y,x in zip(*np.nonzero(keep)):
            o[y,x,:3]=colorsys.hsv_to_rgb(scarf_h,s[y,x]*.9,v[y,x])
    if hair:
        f,ds=hair
        hm=A&(h>=.04)&(h<=.12)&(s>.45)&(v<.8)
        for y,x in zip(*np.nonzero(hm)):
            o[y,x,:3]=colorsys.hsv_to_rgb(h[y,x],min(1,s[y,x]*ds),min(1,v[y,x]*f))
    return Image.fromarray((np.clip(o,0,1)*255).astype(np.uint8),'RGBA')
variants=[(None,None),(.60,(.55,.6)),(.33,(1.35,.75)),(.78,(.75,.9))]
sheet=Image.new('RGBA',(CW*4,CH*2*len(variants)),(0,0,0,0))
for vi,(sh,hair) in enumerate(variants):
    for i,(im,hc) in enumerate(frames):
        im2=recolor(im,sh,hair) if (sh is not None or hair) else im
        row=vi*2+i//4; col=i%4
        sheet.alpha_composite(im2,(int(col*CW+CW/2-hc), row*CH+CH-1-im2.height))
al=sheet.getchannel('A').point(lambda v:255 if v>110 else 0)
sheet.putalpha(al)
sheet.quantize(colors=96,method=Image.FASTOCTREE,dither=Image.NONE).save(out,optimize=True)
print('cell',CW,CH,'sheet',sheet.size)
