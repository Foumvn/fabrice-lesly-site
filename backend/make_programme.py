"""
make_programme.py — Programme du mariage Fabrice & Leslie, construit sur le
gabarit existant `rendu billet/billets/Programme.pdf` (celui d'Arlette &
Bienvenue).

Pourquoi une reconstruction plutôt que des retouches ponctuelles :
- tout le contenu du programme tient dans UN seul flux de 744 Ko, il n'y a
  donc pas de flux isolé par ligne comme sur la carte d'invitation ;
- les heures ne sont pas du texte mais des IMAGES (« 09H00 », « 11H00»...) ;
- les polices embarquées sont sous-ensemblées : OpenSans n'a ni X ni Y, donc
  « RELIGIEUX » et « GLORY » sont impossibles à réencoder ;
- il faut passer de 4 créneaux à 3.

En revanche l'intérieur du panneau est d'un orange parfaitement uniforme
(RGB 188, 61, 23 — écart-type nul mesuré sur le rendu), donc une rustine
plate y est invisible. La méthode est donc :

1. découper les pictogrammes (voiture, alliances, coupes) et les ornements
   (papillon, alliances dorées) dans un rendu 400 dpi ;
2. recouvrir d'orange la zone des créneaux et celle des prénoms ;
3. recoller les pictogrammes aux nouvelles positions et redessiner les
   3 créneaux (heure, filet, lignes de texte) puis « Fabrice » et « Leslie ».

Les pictogrammes sont recollés en bitmap : ils sont sur un fond plat, donc
le raccord est invisible, et cela permet de les repositionner librement.

Usage :
    python make_programme.py
"""
import io
import os
import sys

import numpy as np
import pymupdf
from PIL import Image

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
BILLETS = os.path.join(_ROOT, "rendu billet", "billets")
SOURCE = os.path.join(BILLETS, "Programme.pdf")
OUTPUT = os.path.join(BILLETS, "Programme - Fabrice et Leslie.pdf")
PREVIEW = os.path.join(BILLETS, "_apercu_programme.png")

FONTS = os.path.join(_HERE, "fonts")
# Kingred est la police du titre « PROGRAMME » du gabarit, et la seule des
# polices disponibles à avoir des chiffres bas de casse alignés : Cormorant
# Garamond n'a que des chiffres elzéviriens, où le 0 se lit « o ».
HOUR_FONT = os.path.join(_ROOT, "fonts", "Kingred.otf")
TEXT_FONT = os.path.join(FONTS, "Inter-Regular.ttf")
SCRIPT_FONT = os.path.join(FONTS, "Amsterdam-Four.ttf")

# Orange du panneau, relevé sur le rendu (uniforme).
ORANGE = (188 / 255, 61 / 255, 23 / 255)
WHITE = (1, 1, 1)
# Fond vert foncé du bas de page (relevé : RGB 16, 53, 52), utilisé pour la
# rustine de la ligne « DRESS CODE ».
DARK = (16 / 255, 53 / 255, 52 / 255)
TERRACOTTA = (226 / 255, 114 / 255, 91 / 255)

# Ligne « DRESS CODE » : les anciens libellés et pastilles sont SUPPRIMÉS
# (réaction PDF, pas une simple rustine — le texte d'origine resterait sinon
# dans le flux et ressortirait à la sélection), puis la ligne est refaite.
# « DRESS CODE : » (qui finit à x = 79.1) est conservé.
DRESS_FONT = os.path.join(FONTS, "Montserrat-Regular.ttf")
DRESS_SIZE = 5.39
DRESS_BASELINE = 399.24   # encre centrée comme les libellés d'origine
DRESS_REDACT = (82.0, 392.5, 266.0, 403.5)
DRESS_X = 85.2                  # départ du premier libellé
DRESS_GAP_LABEL = 3.9           # libellé -> pastille
DRESS_GAP_SWATCH = 4.5          # pastille -> libellé suivant
DRESS_SWATCH_W, DRESS_SWATCH_H = 20.6, 6.6
DRESS_SWATCH_Y = 394.55
BURNT_ORANGE = (204 / 255, 85 / 255, 0)          # orange brûlé
DRESS_ITEMS = [
    ("Terra cota", TERRACOTTA),
    ("Orange brûlé", BURNT_ORANGE),
    ("Blanc", WHITE),
]

CROP_DPI = 400

# ---------------------------------------------------------------------------
# Contenu
# ---------------------------------------------------------------------------
COUPLE = ("Fabrice", "Leslie")

# (heure, intitulé, lieu, pictogramme). Le gabarit place l'intitulé AU-DESSUS
# du filet et le lieu en dessous ; le lieu est replié automatiquement.
PROGRAMME = [
    ("10H00", "CÉRÉMONIE CIVILE", "À LA MAIRIE D'EKOUNOU", "car"),
    ("14H00", "MARIAGE RELIGIEUX",
     "À L'ÉGLISE KINGDOM OF GLORY MINISTRIES, "
     "DERNIER POTEAU EKIÉ, CARREFOUR NON GLACÉ", "rings"),
    ("20H00", "LA SOIRÉE", "À L'HÔTEL DE VILLE, CERCLE MUNICIPAL", "glasses"),
]

# ---------------------------------------------------------------------------
# Géométrie relevée sur le gabarit
# ---------------------------------------------------------------------------
# Pictogrammes vectoriels et ornements, à découper avant recouvrement.
CROPS = {
    "car": (204.00, 113.71, 235.62, 125.90),
    "rings": (201.48, 188.75, 232.45, 211.36),
    "glasses": (202.35, 229.37, 231.62, 263.80),
    "butterfly": (139.60, 283.60, 157.40, 300.20),
    "gold_rings": (131.80, 301.60, 154.20, 318.40),
}
ORNAMENTS = ("butterfly", "gold_rings")     # recollés à leur place d'origine

# Zones recouvertes : créneaux, puis prénoms (sans toucher aux deux lignes
# « NOUS SOMMES IMPATIENTS... » dont l'encre commence à y = 322).
COVER_SLOTS = (46.0, 100.0, 252.0, 278.0)
COVER_NAMES = (90.0, 283.0, 200.0, 321.0)

SLOTS_TOP, SLOTS_BOTTOM = 105.0, 272.0

HOUR_RIGHT = 85.0            # les heures sont fer à droite
HOUR_INK_HEIGHT = 12.0       # hauteur d'encre des images d'origine
HOUR_MAX_WIDTH = 34.0        # largeur de la plus large des images (« 09H00 »)
HOUR_ABOVE_RULE = 1.1        # centre optique de l'heure, au-dessus du filet

RULE_X0, RULE_X1 = 89.0, 204.0
RULE_WIDTH = 0.75
DOT_X, DOT_R = 205.4, 1.15   # petite puce au bout du filet

TEXT_SIZE = 7.0
TEXT_CENTER = 146.5
TEXT_MAX_WIDTH = 106.0   # le pictogramme (bitmap opaque) commence à x ≈ 201
TEXT_ASCENT, TEXT_DESCENT = 7.0, 2.2
FIRST_ABOVE_RULE = 2.6       # ligne de base de la 1re ligne, au-dessus du filet
LINE_HEIGHT = 9.3

ICON_CENTER_X = 218.0

# Prénoms : mêmes corps et ligne de base que « Arlette » / « Bienvenue ».
NAME_SIZE = 9.73
NAME_BASELINE = 314.23
NAME_LEFT_END = 130.0        # « Fabrice » fer à droite, avant les alliances
NAME_RIGHT_START = 155.5     # « Leslie » fer à gauche, après les alliances
NAME_SHADOW = 0.43


def _ink_ratios(text: str, fontfile: str) -> tuple[float, float, float, float]:
    """
    Étendue d'encre réelle, par unité de corps : (largeur, hauteur, montée,
    décalage gauche). Mesurée sur un rendu, comme dans `pdf_generator`, car
    les boîtes de glyphes de PyMuPDF ne sont pas exploitables.
    """
    probe, dpi = 100.0, 200
    doc = pymupdf.open()
    page = doc.new_page(width=2400, height=900)
    bx, by = 300.0, 600.0
    page.insert_text((bx, by), text, fontsize=probe, fontname="Pr",
                     fontfile=fontfile)
    pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ys, xs = np.where(a < 240)
    doc.close()
    s = dpi / 72.0
    return ((xs.max() - xs.min() + 1) / s / probe,
            (ys.max() - ys.min() + 1) / s / probe,
            (by - ys.min() / s) / probe,
            (xs.min() / s - bx) / probe)


def hour_metrics(hours: list[str]) -> tuple[float, dict]:
    """
    Corps COMMUN à toutes les heures — sinon chacune saturerait la largeur
    disponible avec un corps différent, et leur hauteur varierait d'un créneau
    à l'autre — puis les cotes d'encre de chacune à ce corps.
    """
    ratios = {h: _ink_ratios(h, HOUR_FONT) for h in hours}
    size = min(min(HOUR_INK_HEIGHT / h_r, HOUR_MAX_WIDTH / w_r)
               for w_r, h_r, _, _ in ratios.values())
    cotes = {h: {"w": w_r * size, "up": up_r * size, "left": left_r * size,
                 "h": h_r * size}
             for h, (w_r, h_r, up_r, left_r) in ratios.items()}
    return size, cotes


def wrap(text: str, font: pymupdf.Font, size: float, max_w: float) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and font.text_length(trial, fontsize=size) > max_w:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    doc = pymupdf.open(SOURCE)
    page = doc[0]

    # 1. Découpe des pictogrammes et ornements dans un rendu haute résolution.
    scale = CROP_DPI / 72.0
    full = page.get_pixmap(dpi=CROP_DPI)
    sheet = Image.frombytes("RGB", (full.width, full.height), full.samples)
    pieces = {}
    icon_ink = {}            # centre d'encre de chaque pictogramme, en points
    orange8 = np.array([round(c * 255) for c in ORANGE])
    for name, (x0, y0, x1, y1) in CROPS.items():
        crop = sheet.crop((round(x0 * scale), round(y0 * scale),
                           round(x1 * scale), round(y1 * scale)))
        arr = np.asarray(crop).copy()
        if name not in ORNAMENTS:
            # La découpe emporte un bout de l'ancien filet (et sa puce) à
            # gauche du pictogramme : on l'efface avant recollage, sinon il
            # flotte à côté du nouveau filet.
            cut = int((206.0 - x0) * scale)
            if cut > 0:
                arr[:, :cut] = orange8
                crop = Image.fromarray(arr)
            # Centre de l'ENCRE (pas du cadre) : c'est lui qui doit être
            # aligné sur le nouveau filet.
            dist = np.abs(arr.astype(int) - orange8).sum(axis=2)
            ys, xs = np.where(dist > 40)
            icon_ink[name] = ((x0 + (xs.min() + xs.max() + 1) / 2 / scale),
                                (y0 + (ys.min() + ys.max() + 1) / 2 / scale))
        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        pieces[name] = buf.getvalue()
        print(f"  découpé {name:11} {crop.width}x{crop.height} px")

    # 2. Rustines orange.
    for zone in (COVER_SLOTS, COVER_NAMES):
        page.draw_rect(pymupdf.Rect(*zone), color=None, fill=ORANGE)

    # 3. Ornements recollés à l'identique.
    for name in ORNAMENTS:
        page.insert_image(pymupdf.Rect(*CROPS[name]), stream=pieces[name])

    # 4. Créneaux : hauteur de chaque bloc, puis répartition verticale.
    text_font = pymupdf.Font(fontfile=TEXT_FONT)
    blocks = []
    for hour, title, place, icon in PROGRAMME:
        lines = [title] + wrap(place, text_font, TEXT_SIZE, TEXT_MAX_WIDTH)
        text_h = (TEXT_ASCENT + FIRST_ABOVE_RULE
                  + LINE_HEIGHT * (len(lines) - 1) + TEXT_DESCENT)
        ix0, iy0, ix1, iy1 = CROPS[icon]
        blocks.append({"hour": hour, "lines": lines, "icon": icon,
                       "icon_w": ix1 - ix0, "icon_h": iy1 - iy0,
                       "text_h": text_h, "h": max(text_h, iy1 - iy0)})

    total = sum(b["h"] for b in blocks)
    gap = (SLOTS_BOTTOM - SLOTS_TOP - total) / (len(blocks) - 1)
    print(f"  hauteur des blocs {[round(b['h'], 1) for b in blocks]} "
          f"-> interligne {gap:.1f} pt")

    hour_size, hour_cotes = hour_metrics([b["hour"] for b in blocks])
    print(f"  corps commun des heures : {hour_size:.2f}")

    y = SLOTS_TOP
    for b in blocks:
        text_top = y + (b["h"] - b["text_h"]) / 2
        rule_y = text_top + TEXT_ASCENT + FIRST_ABOVE_RULE

        # Filet + puce
        page.draw_line(pymupdf.Point(RULE_X0, rule_y),
                       pymupdf.Point(RULE_X1, rule_y),
                       color=WHITE, width=RULE_WIDTH)
        page.draw_circle(pymupdf.Point(DOT_X, rule_y), DOT_R,
                         color=None, fill=WHITE)

        # Heure : fer à droite et encre centrée juste au-dessus du filet.
        c = hour_cotes[b["hour"]]
        w, up, left = c["w"], c["up"], c["left"]
        ink_center = rule_y - HOUR_ABOVE_RULE
        page.insert_text((HOUR_RIGHT - w - left,
                          ink_center - c["h"] / 2 + up),
                         b["hour"], fontsize=hour_size, fontname="Hr",
                         fontfile=HOUR_FONT, color=WHITE)

        # Lignes de texte : la première au-dessus du filet, les autres dessous
        for i, line in enumerate(b["lines"]):
            baseline = (rule_y - FIRST_ABOVE_RULE if i == 0
                        else rule_y + LINE_HEIGHT * i)
            lw = text_font.text_length(line, fontsize=TEXT_SIZE)
            page.insert_text((TEXT_CENTER - lw / 2, baseline), line,
                             fontsize=TEXT_SIZE, fontname="Txt",
                             fontfile=TEXT_FONT, color=WHITE)

        # Pictogramme : encre centrée (x = ICON_CENTER_X, y = filet)
        cx, cy = icon_ink[b["icon"]]
        dx, dy = ICON_CENTER_X - cx, rule_y - cy
        ix0, iy0, ix1, iy1 = CROPS[b["icon"]]
        page.insert_image(pymupdf.Rect(ix0 + dx, iy0 + dy,
                                       ix1 + dx, iy1 + dy),
                          stream=pieces[b["icon"]])
        print(f"  {b['hour']} largeur {w:5.2f} encre {c['h']:5.2f}  "
              f"filet y={rule_y:6.2f}  {len(b['lines'])} ligne(s)")
        y += b["h"] + gap

    # 5. Prénoms, dans le style de « Arlette » / « Bienvenue ».
    script = pymupdf.Font(fontfile=SCRIPT_FONT)
    left, right = COUPLE
    wl = script.text_length(left, fontsize=NAME_SIZE)
    for text, x in ((left, NAME_LEFT_END - wl), (right, NAME_RIGHT_START)):
        page.insert_text((x + NAME_SHADOW, NAME_BASELINE + NAME_SHADOW), text,
                         fontsize=NAME_SIZE, fontname="Scr",
                         fontfile=SCRIPT_FONT, color=(0.35, 0.09, 0.02))
        page.insert_text((x, NAME_BASELINE), text, fontsize=NAME_SIZE,
                         fontname="Scr", fontfile=SCRIPT_FONT, color=WHITE)
    print(f"  prénoms : « {left} » et « {right} »")

    # 6. Dress code : suppression des anciens libellés et pastilles (texte et
    #    traits), le fond est une image — elle n'est pas touchée.
    page.add_redact_annot(pymupdf.Rect(*DRESS_REDACT))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE,
                          graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED)
    dress_font = pymupdf.Font(fontfile=DRESS_FONT)
    x = DRESS_X
    for label, color in DRESS_ITEMS:
        page.insert_text((x, DRESS_BASELINE), label, fontsize=DRESS_SIZE,
                         fontname="Dr", fontfile=DRESS_FONT, color=WHITE)
        x += dress_font.text_length(label, fontsize=DRESS_SIZE) + DRESS_GAP_LABEL
        swatch = pymupdf.Rect(x, DRESS_SWATCH_Y,
                              x + DRESS_SWATCH_W, DRESS_SWATCH_Y + DRESS_SWATCH_H)
        page.draw_rect(swatch, color=None, fill=color)
        page.draw_rect(swatch, color=WHITE, width=0.4)
        x += DRESS_SWATCH_W + DRESS_GAP_SWATCH
    print(f"  dress code : {' / '.join(l for l, _ in DRESS_ITEMS)} "
          f"(fin x={x - DRESS_GAP_SWATCH:.1f})")

    doc.save(OUTPUT, garbage=3, deflate=True)
    doc.close()

    out = pymupdf.open(OUTPUT)
    out[0].get_pixmap(dpi=170).save(PREVIEW)
    out.close()
    print(f"\n[OK] {OUTPUT}\n     aperçu : {PREVIEW}")


if __name__ == "__main__":
    main()
