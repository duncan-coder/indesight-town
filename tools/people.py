"""把多張角色動作表（洋紅背景、2 列 x 4 格）合成遊戲用的 people.png。
用法：python3 tools/people.py 輸出.png 角色1.png 角色2.png ...
每個角色輸出 2 列：第 1 列正面往右下走，第 2 列背面往左上走，各 4 格。
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

TH = 96  # 角色高度（px），遊戲內縮 0.25 倍

def frames_of(src):
    a = np.asarray(Image.open(src).convert('RGB')).astype(np.int32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    alpha = np.clip((150 - (np.minimum(r, b) - g)) / 90.0, 0, 1)
    fr = alpha < 1; lim = g + 40
    rgb = a.copy()
    rgb[..., 0] = np.where(fr, np.minimum(r, np.maximum(lim, r * alpha)), r)
    rgb[..., 2] = np.where(fr, np.minimum(b, np.maximum(lim, b * alpha)), b)
    # 每格角色可能被拆成幾塊（例如手提的袋子），先膨脹再找連通區塊
    lab, n = ndimage.label(ndimage.binary_dilation(alpha > 0.4, iterations=12))
    comps = [s for s in ndimage.find_objects(lab) if (s[0].stop - s[0].start) > 150]
    comps.sort(key=lambda s: (round(s[0].start / 300), s[1].start))
    if len(comps) != 8:
        raise SystemExit(f'{src}: 找到 {len(comps)} 個角色，預期 8 個')
    # 去掉膨脹的邊
    tight = []
    for s in comps:
        m = alpha[s] > 0.4
        ys, xs = np.nonzero(m)
        tight.append((slice(s[0].start + ys.min(), s[0].start + ys.max() + 1),
                      slice(s[1].start + xs.min(), s[1].start + xs.max() + 1)))
    k = TH / max(s[0].stop - s[0].start for s in tight)
    out = []
    for sl in tight:
        crop = np.dstack([rgb[sl], alpha[sl] * 255]).astype(np.uint8)
        im = Image.fromarray(crop, 'RGBA')
        top = alpha[sl][:int(alpha[sl].shape[0] * .4)]
        cx = np.nonzero(top.sum(0) > 0.5)[0]
        hc = (cx.min() + cx.max()) / 2  # 以頭部中心對齊，走路時身體不會左右跳
        im = im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        out.append((im, hc * k))
    return out

dst, srcs = sys.argv[1], sys.argv[2:]
chars = [frames_of(s) for s in srcs]
CW = int(np.ceil(max(max(hc, im.width - hc) for ch in chars for im, hc in ch) * 2 + 4))
CH = TH + 2
sheet = Image.new('RGBA', (CW * 4, CH * 2 * len(chars)), (0, 0, 0, 0))
for ci, ch in enumerate(chars):
    for i, (im, hc) in enumerate(ch):
        row = ci * 2 + i // 4
        sheet.alpha_composite(im, (int((i % 4) * CW + CW / 2 - hc), row * CH + CH - 1 - im.height))
sheet.putalpha(sheet.getchannel('A').point(lambda v: 255 if v > 110 else 0))
sheet.quantize(colors=128, method=Image.FASTOCTREE, dither=Image.NONE).save(dst, optimize=True)
print(f'cell {CW} {CH}  characters {len(chars)}  sheet {sheet.size}')
