import sys
from PIL import Image
import numpy as np
src,out,target_w=sys.argv[1],sys.argv[2],int(sys.argv[3])
im=Image.open(src).convert('RGB'); a=np.asarray(im).astype(np.int32)
r,g,b=a[...,0],a[...,1],a[...,2]
# magenta-ness: high R and B, low G
m=np.minimum(r,b)-g
alpha=np.clip((150-m)/90.0,0,1)          # m>=150 -> 0, m<=60 -> 1
# despill: pull R,B down toward G-based estimate on fringe pixels
fr=alpha<1
out_rgb=a.copy()
lim=g+40
out_rgb[...,0]=np.where(fr,np.minimum(r,np.maximum(lim,r*alpha)),r)
out_rgb[...,2]=np.where(fr,np.minimum(b,np.maximum(lim,b*alpha)),b)
rgba=np.dstack([out_rgb,alpha*255]).astype(np.uint8)
im2=Image.fromarray(rgba,'RGBA')
bbox=im2.getchannel('A').point(lambda v:255 if v>40 else 0).getbbox()
im2=im2.crop(bbox)
s=target_w/im2.width
im3=im2.resize((target_w,round(im2.height*s)),Image.LANCZOS)
# harden alpha, quantize to a small palette for a pixel feel and small file
al=im3.getchannel('A').point(lambda v:255 if v>110 else 0)
im3.putalpha(al)
q=im3.quantize(colors=64,method=Image.FASTOCTREE,dither=Image.NONE)
q.save(out,optimize=True)
print('bbox',bbox,'out',q.size)
