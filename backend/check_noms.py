"""
check_noms.py — Contrôle que le nom de chaque invité ne touche rien sur la carte.

Rend chaque carte personnalisée à 200 dpi, isole l'encre orange du nom dans la
bande qui lui est réservée, puis mesure les dégagements réels avec la barre
ornementale au-dessus et le paragraphe en dessous. C'est une vérification
pixel, indépendante du calcul de `fit_guest_name()`.

Usage :
    python check_noms.py
    python check_noms.py "Un Nom À Tester" "Un Autre"
"""
import os
import sys

import numpy as np
import pymupdf

from import_csv import parse_csv
from pdf_generator import fit_guest_name, personalize_card

_HERE = os.path.dirname(os.path.abspath(__file__))
DATA_CSV = os.path.join(_HERE, "data", "invites.csv")

BAR_BOTTOM = 37.39         # bas de la barre ornementale
PARAGRAPH_TOP = 76.83      # haut du paragraphe
X_SAFE = (26.0, 272.0)     # colonne centrale, hors ornements latéraux
MIN_GAP = 1.0              # dégagement minimal exigé, en pt

DPI = 200
SCALE = DPI / 72.0


def name_ink_bbox(name: str):
    """bbox (x0, y0, x1, y1) en pt de l'encre orange du nom, ou None."""
    doc = pymupdf.open("pdf", personalize_card(name).getvalue())
    pix = doc[0].get_pixmap(dpi=DPI)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, 3).astype(int)
    doc.close()

    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    orange = (r > 150) & (g > 40) & (g < 170) & (b < 130)
    # On borne à la bande du nom : « Leslie » et « Fabrice » sont aussi orange.
    orange[int(PARAGRAPH_TOP * SCALE):] = False
    orange[:int(BAR_BOTTOM * SCALE)] = False
    ys, xs = np.where(orange)
    if not len(xs):
        return None
    # `orange` couvre toute la page : les indices sont déjà absolus.
    return (xs.min() / SCALE, ys.min() / SCALE,
            (xs.max() + 1) / SCALE, (ys.max() + 1) / SCALE)


def main():
    names = sys.argv[1:]
    if not names:
        names = [g["name"] for g in parse_csv(DATA_CSV)]

    fails = []
    worst_top = worst_bottom = (1e9, "")
    for name in names:
        size, _, _ = fit_guest_name(name)
        bb = name_ink_bbox(name)
        if bb is None:
            fails.append((name, "nom introuvable sur le rendu"))
            continue
        x0, y0, x1, y1 = bb
        gap_top, gap_bottom = y0 - BAR_BOTTOM, PARAGRAPH_TOP - y1
        worst_top = min(worst_top, (gap_top, name))
        worst_bottom = min(worst_bottom, (gap_bottom, name))
        if gap_top < MIN_GAP:
            fails.append((name, f"barre à {gap_top:.2f} pt"))
        if gap_bottom < MIN_GAP:
            fails.append((name, f"paragraphe à {gap_bottom:.2f} pt"))
        if x0 < X_SAFE[0] or x1 > X_SAFE[1]:
            fails.append((name, f"déborde en x : {x0:.1f}-{x1:.1f}"))
        print(f"  {name:32} corps {size:5.2f}  barre {gap_top:5.2f}  "
              f"paragraphe {gap_bottom:5.2f}  x {x0:6.2f}-{x1:6.2f}")

    print(f"\nnoms testés : {len(names)}")
    print(f"dégagement minimal / barre       : {worst_top[0]:.2f} pt ({worst_top[1]})")
    print(f"dégagement minimal / paragraphe  : {worst_bottom[0]:.2f} pt ({worst_bottom[1]})")
    print("échecs :", fails or "AUCUN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
