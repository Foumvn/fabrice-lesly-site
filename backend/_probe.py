import os
import sys

import numpy as np
import pymupdf
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "rendu billet", "billets")

DPI = 400
S = DPI / 72.0
files = [("ORIGINAL", os.path.join(OUT, "Programme.pdf")),
         ("NOUVEAU", os.path.join(OUT, "Programme - Fabrice et Leslie.pdf"))]

crops = []
for label, path in files:
    d = pymupdf.open(path)
    pix = d[0].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    a = np.asarray(img).astype(int)
    d.close()

    # Encre claire dans la bande des prenoms uniquement (au-dessus de y=321)
    z = a[int(297 * S):int(321 * S), int(90 * S):int(205 * S)]
    m = (z[..., 0] > 215) & (z[..., 1] > 190) & (z[..., 2] > 165)
    ys, xs = np.where(m)
    print(f"{label}: prenoms  x {90+xs.min()/S:6.2f}-{90+xs.max()/S:6.2f}  "
          f"y {297+ys.min()/S:6.2f}-{297+ys.max()/S:6.2f}  "
          f"h={(ys.max()-ys.min())/S:5.2f}")

    c = img.crop((int(40 * S), int(100 * S), int(265 * S), int(340 * S)))
    crops.append(c.resize((c.width // 2, c.height // 2), Image.LANCZOS))

sheet = Image.new("RGB", (sum(c.width for c in crops) + 12,
                          max(c.height for c in crops)), "white")
x = 0
for c in crops:
    sheet.paste(c, (x, 0))
    x += c.width + 12
sheet.save(os.path.join(OUT, "_compare_programme.png"))
print("comparatif:", os.path.join(OUT, "_compare_programme.png"))
