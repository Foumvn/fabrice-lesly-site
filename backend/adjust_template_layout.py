"""
adjust_template_layout.py — Retouches de mise en page du gabarit
`templates/invitation-carte.pdf`, appliquées directement dans les flux de
contenu (aucun re-rendu, donc aucune perte de qualité et fond intact).

Repère du flux principal (xref 250) : il débute par
`q .24 0 0 -.24 0 426.96 cm`, et la MediaBox est décalée de 7.71 pt, si bien
que la conversion est simplement  y_page = 0.24 x Y_flux  (y_page vers le bas).
Un point de page vaut donc 1/0.24 = 4.1666 unités de flux.

Quatre retouches :

1. Titre « MARIAGE CIVIL ET RELIGIEUX » remonté de TITLE_UP.
   C'est un flux de texte isolé (xref 259) : il suffit de décaler son Tm.

2. Barre ornementale sous le titre, remontée d'autant pour rester solidaire du
   titre. Elle est vectorielle, dans le flux principal, encadrée par un clip :
   on décale le rectangle de clip ET la matrice du groupe.

3. Photo des mariés (/X13) descendue de PHOTO_DOWN. Elle est détourée par un
   cercle qui, lui, ne bouge pas : l'image glisse donc dans son hublot et
   dégage le haut des têtes.

4. Ligne du lieu réécrite. Les polices du gabarit sont sous-ensemblées et il
   leur manque les minuscules a, s, b, f, g, h, j, k, q, w, y, z : on ne peut
   donc pas réencoder le nouveau libellé comme dans `fix_template_text.py`.
   Les deux flux de texte de la ligne sont donc vidés (le fond reste intact,
   aucune rustine opaque) et la ligne est redessinée en Montserrat, la même
   famille que l'original.

Le script n'agit que sur les valeurs d'origine exactes : relancé deux fois, il
refuse de cumuler les décalages.

Usage :
    python adjust_template_layout.py --dry-run
    python adjust_template_layout.py
"""
import argparse
import os
import re
import shutil
import sys

import pymupdf

_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(_HERE, "templates", "invitation-carte.pdf")
BACKUP = TEMPLATE + ".layout.bak"

TITLE_UP = 26.0       # pt de page : remontée du titre + de la barre
PHOTO_DOWN = 10.0     # pt de page : descente de la photo dans son hublot

PT = 1.0 / 0.24       # 1 pt de page = 4.1666 unités de flux

TITLE_XREF = 259
MAIN_XREF = 250

# Ligne du lieu : deux flux de texte isolés, « Lieu : » en gras puis la suite.
LIEU_XREFS = (286, 287)
LIEU_BOLD = "Lieu :"
LIEU_REST = " La soirée : hotel de ville cercle municipal"
LIEU_SIZE = 6.2
LIEU_BASELINE = 199.72        # ligne de base d'origine (Tm 227.24 en PDF)
LIEU_CENTER = 297.75 / 2 - 2.275
FONTS_DIR = os.path.join(_HERE, "fonts")
MONTSERRAT_BOLD = os.path.join(FONTS_DIR, "Montserrat-Bold.ttf")
MONTSERRAT_REGULAR = os.path.join(FONTS_DIR, "Montserrat-Regular.ttf")

# Valeurs d'origine (le script échoue si elles ont déjà bougé).
DIVIDER_CLIP = b"547.25289 242.36081 143.6549 21.860535 re"
DIVIDER_CM = b".35833744 0 0 .35833744 547.28878 242.59471 cm"
PHOTO_CM = b"793.3458 0 0 -1190.0188 222.99558 1920.8316 cm"


def _fmt(v: float) -> str:
    return f"{v:.5f}".rstrip("0").rstrip(".")


def patch_title(doc: pymupdf.Document) -> bytes:
    raw = doc.xref_stream(TITLE_XREF)
    m = re.search(rb"([-\d.]+)\s+([-\d.]+)\s+Tm", raw)
    x, y = float(m.group(1)), float(m.group(2))
    new_y = y + TITLE_UP           # Tm est en coordonnées PDF : +y = vers le haut
    print(f"  titre    Tm y {y:.3f} -> {new_y:.3f}")
    return raw[:m.start()] + f"{_fmt(x)} {_fmt(new_y)} Tm".encode() + raw[m.end():]


def patch_main(raw: bytes) -> bytes:
    dy = TITLE_UP * PT            # dans le flux, Y croît vers le bas : remonter = -dy
    clip_new = (f"547.25289 {_fmt(242.36081 - dy)} 143.6549 21.860535 re").encode()
    cm_new = (f".35833744 0 0 .35833744 547.28878 "
              f"{_fmt(242.59471 - dy)} cm").encode()
    photo_new = (f"793.3458 0 0 -1190.0188 222.99558 "
                 f"{_fmt(1920.8316 + PHOTO_DOWN * PT)} cm").encode()

    for old, new, label in ((DIVIDER_CLIP, clip_new, "clip barre"),
                            (DIVIDER_CM, cm_new, "barre     "),
                            (PHOTO_CM, photo_new, "photo     ")):
        if raw.count(old) != 1:
            raise SystemExit(f"[ABANDON] {label.strip()} : "
                             f"{raw.count(old)} occurrence(s) de la valeur "
                             f"d'origine (gabarit déjà retouché ?)")
        raw = raw.replace(old, new)
        print(f"  {label} {old.decode()}\n            -> {new.decode()}")
    return raw


def rewrite_lieu(doc: pymupdf.Document) -> None:
    """Vide les flux de la ligne du lieu et la redessine, centrée, en Montserrat."""
    page = doc[0]
    for xref in LIEU_XREFS:
        doc.update_stream(xref, b" ")

    bold = pymupdf.Font(fontfile=MONTSERRAT_BOLD)
    regular = pymupdf.Font(fontfile=MONTSERRAT_REGULAR)
    w_bold = bold.text_length(LIEU_BOLD, fontsize=LIEU_SIZE)
    w_rest = regular.text_length(LIEU_REST, fontsize=LIEU_SIZE)
    x = LIEU_CENTER - (w_bold + w_rest) / 2

    page.insert_text((x, LIEU_BASELINE), LIEU_BOLD, fontsize=LIEU_SIZE,
                     fontname="MtsB", fontfile=MONTSERRAT_BOLD, color=(1, 1, 1))
    page.insert_text((x + w_bold, LIEU_BASELINE), LIEU_REST, fontsize=LIEU_SIZE,
                     fontname="MtsR", fontfile=MONTSERRAT_REGULAR, color=(1, 1, 1))
    print(f"  lieu       « {LIEU_BOLD}{LIEU_REST} »")
    print(f"             x {x:.2f} -> {x + w_bold + w_rest:.2f} "
          f"(largeur {w_bold + w_rest:.2f} pt)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    doc = pymupdf.open(TEMPLATE)
    print(f"[INFO] titre remonté de {TITLE_UP} pt, photo descendue de "
          f"{PHOTO_DOWN} pt")
    title_raw = patch_title(doc)
    main_raw = patch_main(doc.xref_stream(MAIN_XREF))

    if args.dry_run:
        print("[DRY] aucune écriture.")
        return

    shutil.copyfile(TEMPLATE, BACKUP)
    doc.update_stream(TITLE_XREF, title_raw)
    doc.update_stream(MAIN_XREF, main_raw)
    rewrite_lieu(doc)
    doc.saveIncr()
    doc.close()
    print(f"[OK] gabarit retouché (sauvegarde : {os.path.basename(BACKUP)})")


if __name__ == "__main__":
    main()
