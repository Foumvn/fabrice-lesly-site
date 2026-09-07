"""
pdf_generator.py — Génère UN SEUL PDF de 3 pages par invité :

  page 1 : le billet MAÎTRE « Billet dinvitation.pdf » (1059 x 1486),
           qui porte les 4 zones cliquables
  page 2 : la carte d'invitation « invitation de x.pdf » (297.75 x 419.25),
           personnalisée avec le nom de l'invité en Amsterdam-Four #E76A4A
           (même typographie/couleur que les prénoms Fabrice & Leslie)
  page 3 : la page QR, aux dimensions de la page 1, QR de grosseur moyenne

Navigation dans le document (zones cliquables de la page 1) :
  « Cliquez ici pour voir le billet »  -> ANCRE INTERNE vers la page 2
                                          (aucun réseau requis, fonctionne
                                           hors ligne dans n'importe quel
                                           lecteur PDF)
  « Confirmer votre présence »         -> lien web
  « Voir le lieu de l'évènement »      -> lien web (Google Maps)
  « Informations supplémentaires »     -> lien web

Contenu du QR : NOM|TABLE|ID  (toujours en majuscules — contrat du scanner)

Design de la page QR — réplique fidèle de la typographie de la page 1
(celle des prénoms « Leslie » et « Fabrice ») :
- nom de la table en Amsterdam-Four, en CASSE DE TITRE (jamais en capitales :
  cette script est illisible en majuscules), couleur #E76A4A, avec l'ombre
  noire décalée de 1 pt exactement comme les prénoms sur la page 1
- sous-titre de table (ex. « Victoire ») en Montserrat, discret
- mention "Présentez ce code QR à l'entrée" : Montserrat
- QR code (correction H) avec anneaux, centré.

La page QR est décrite une seule fois dans un repère « carte » de référence
(297.75 x 419.25) puis mise à l'échelle vers le format cible, ce qui garantit
une identité visuelle entre PDF1 et PDF2 quelle que soit la taille de page.
"""
import io
import os
from urllib.parse import quote

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter
from PIL import Image
import numpy as np

import pymupdf

from font_manager import register_all_fonts, FONTS_DIR
from qr_generator import generate_qr_with_rings

register_all_fonts()

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_ROOT = os.path.dirname(_HERE)                 # template/

TEMPLATES_DIR = os.path.join(_HERE, "templates")
CARD_TEMPLATE = os.path.join(TEMPLATES_DIR, "invitation-carte.pdf")
BILLET_PNG = os.path.join(TEMPLATES_DIR, "billet.png")
MASTER_BILLET = os.path.join(_TEMPLATE_ROOT, "rendu billet", "Billet dinvitation.pdf")
AMSTERDAM = os.path.join(FONTS_DIR, "Amsterdam-Four.ttf")

# Repère de référence dans lequel la page QR est composée = format de la carte.
QR_PAGE_W, QR_PAGE_H = 297.75, 419.25

# Grosseur du QR, en fraction de la largeur de page.
# La page QR reprend les dimensions de la page 1 (le grand billet), donc
# ce ratio « moyen » s'applique à une page de 1059 pt de large.
QR_RATIO_BILLET = 0.48
QR_RATIO_CARD = 0.62

# Palette
QR_BG = HexColor("#ffffff")
NAME_COLOR = HexColor("#e76a4a")        # couleur des prénoms Fabrice & Leslie (page 1)
NAME_SHADOW = HexColor("#000000")       # ombre portée des prénoms (page 1)
BODY_TEXT_COLOR = HexColor("#374151")   # corps de texte, lisible sur blanc
QR_FRAME = HexColor("#d1d5db")

# Typographie du nom de table : calquée sur « Leslie » / « Fabrice » (page 1),
# qui sont en Amsterdam-Four 21.7 pt #E76A4A avec une ombre noire à +1/-1 pt.
TABLE_FONT = "AmsterdamFour"
TABLE_SIZE = 21.7
TABLE_SHADOW_DX = 1.0
TABLE_SHADOW_DY = -1.0
TABLE_MAX_WIDTH = QR_PAGE_W - 40.0

# Rythme vertical de la page QR, exprimé en unités « carte » depuis le haut.
# Amsterdam-Four descend très bas (swash de la dernière lettre) : il faut
# 28 pt sous la ligne de base avant de pouvoir écrire quoi que ce soit.
TABLE_BASELINE_TOP = 88.0
SUBTITLE_BASELINE_TOP = 116.0
MENTION_BASELINE_TOP = 140.0
QR_BAND_GAP = 20.0        # respiration entre la mention et le cadre du QR
QR_BAND_BOTTOM = 26.0     # marge basse de la page

# URL publique du site, embarquée dans les liens cliquables des PDF.
# À définir en production via PUBLIC_BASE_URL (ex. https://mariage.example.com).
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "http://localhost:3000").rstrip("/")
LIEU_URL = "https://maps.app.goo.gl/H3Bebkz24r16gqhJ8"

# Cibles des 3 zones cliquables « web » de la page 1. Le gabarit maître
# contient des URLs placeholder (https://ton-domaine.com/...) qui sont
# systématiquement remplacées par celles-ci.
URL_PRESENCE = f"{BASE_URL}/presence"
URL_INFOS = f"{BASE_URL}/programme"

# Identification des zones dans le gabarit maître, par fragment d'URL.
ZONE_BILLET = "/billet/"              # -> ancre interne vers la page 2
ZONE_PRESENCE = "/confirmation/"      # -> URL_PRESENCE
ZONE_LIEU = "google.com/maps"         # -> LIEU_URL
ZONE_INFOS = "/informations"          # -> URL_INFOS

# Index (0-based) de la page cible de l'ancre interne : la carte d'invitation.
ANCHOR_TARGET_PAGE = 1

# Diffusion du PDF unique via Next (public/billets/<Invité>/invitation.pdf)
SERVE_DIR = "billets"
PDF_FILENAME = "invitation.pdf"

# Géométrie de la carte (297.75 x 419.25 pt)
CARD_W = 297.75
CARD_W_HALF = 297.75 / 2 - 2.275        # 146.6

# --- Nom de l'invité : bande libre et ajustement automatique ---------------
# Amsterdam-Four est une script dont l'encre monte à ~1.8x le corps et descend
# à ~0.5x : un nom occupe donc 1.8 à 2.5 fois son corps en hauteur. Dans le
# gabarit d'origine le couloir sous le titre ne mesurait que 13.4 pt, d'où les
# chevauchements. `adjust_template_layout.py` remonte le titre et la barre
# ornementale de 26 pt, ce qui dégage la bande suivante :
#   barre ornementale : 31.9 -> 37.4
#   paragraphe        : à partir de 76.8
# soit 34.3 pt utiles entre les deux, dégagements compris.
NAME_BAND_TOP = 40.0         # 2.6 pt sous la barre ornementale
NAME_BAND_BOTTOM = 74.3      # 2.5 pt avant le paragraphe
NAME_MAX_WIDTH = 238.0       # colonne centrale, hors ornements latéraux
NAME_MAX_SIZE = 15.0         # plafond, pour rester homogène d'un invité à l'autre
NAME_MIN_SIZE = 6.5

# Ombre portée du nom, calquée sur « Leslie » / « Fabrice » de la page 1
# (copie noire décalée de 0.96 pt vers la droite et vers le bas).
NAME_SHADOW_DX = 0.96
NAME_SHADOW_DY = 0.96

# Mesure de l'encre : rendu de référence puis mise à l'échelle linéaire.
_INK_REF_SIZE = 100.0
_INK_DPI = 200
_ink_cache: dict[str, tuple[float, float, float, float]] = {}

# Rect du lien « clique ici pour voir le billet » (maître du billet)
RECT_BILLET_LINK = (125, 508, 925, 964)


# ---------------------------------------------------------------------------
# URL publique du PDF, servie par Next depuis public/billets/
# ---------------------------------------------------------------------------
def _q(segment: str) -> str:
    return quote(segment, safe="")


def served_pdf_url(guest_name: str) -> str:
    return f"{BASE_URL}/{SERVE_DIR}/{_q(guest_name)}/{_q(PDF_FILENAME)}"


# ---------------------------------------------------------------------------
# Page 1 — la carte personnalisée
# ---------------------------------------------------------------------------
def _ink_metrics(text: str) -> tuple[float, float, float, float]:
    """
    Étendue d'encre RÉELLE du texte en Amsterdam-Four, par unité de corps.

    Renvoie (largeur, hauteur, montée, gauche) où :
      - montée = hauteur d'encre au-dessus de la ligne de base,
      - gauche = décalage de l'encre par rapport au point d'insertion.

    Les boîtes de glyphes de la police ne sont pas exploitables (PyMuPDF
    renvoie la même boîte englobante pour tous les glyphes) et les hampes de
    cette script varient énormément d'un nom à l'autre : « Mama Léopoldine »
    occupe 1.84x son corps en hauteur, « MR et Mme Wilfrid Assako » 2.46x.
    L'encre est donc mesurée sur un rendu, puis mise à l'échelle : les
    proportions sont linéaires en fonction du corps.
    """
    if text in _ink_cache:
        return _ink_cache[text]

    doc = pymupdf.open()
    page = doc.new_page(width=1400, height=700)
    bx, by = 250.0, 450.0
    page.insert_text((bx, by), text, fontsize=_INK_REF_SIZE,
                     fontname="Ams", fontfile=AMSTERDAM)
    pix = page.get_pixmap(dpi=_INK_DPI, colorspace=pymupdf.csGRAY)
    scale = _INK_DPI / 72.0
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ys, xs = np.where(a < 240)
    doc.close()

    if not len(xs):
        metrics = (0.0, 0.0, 0.0, 0.0)
    else:
        metrics = (
            (xs.max() - xs.min() + 1) / scale / _INK_REF_SIZE,   # largeur
            (ys.max() - ys.min() + 1) / scale / _INK_REF_SIZE,   # hauteur
            (by - ys.min() / scale) / _INK_REF_SIZE,             # montée
            (xs.min() / scale - bx) / _INK_REF_SIZE,             # gauche
        )
    _ink_cache[text] = metrics
    return metrics


def fit_guest_name(guest_name: str) -> tuple[float, float, float]:
    """
    Calcule (corps, x, ligne_de_base) pour que le nom remplisse au mieux la
    bande libre sans jamais toucher le titre ni le bord de la carte.

    Le corps est déduit de l'encre réelle : la contrainte de hauteur ou celle
    de largeur s'applique selon la longueur du nom, et l'ombre portée est
    intégrée au budget. Le nom est ensuite centré optiquement, verticalement
    dans la bande et horizontalement sur l'axe de la carte.
    """
    w_r, h_r, up_r, left_r = _ink_metrics(guest_name)
    if not w_r or not h_r:
        return NAME_MAX_SIZE, CARD_W_HALF, NAME_BAND_BOTTOM

    band_h = (NAME_BAND_BOTTOM - NAME_BAND_TOP) - NAME_SHADOW_DY
    band_w = NAME_MAX_WIDTH - NAME_SHADOW_DX
    size = min(NAME_MAX_SIZE, band_h / h_r, band_w / w_r)
    size = max(NAME_MIN_SIZE, size)

    ink_w, ink_h, ink_up = w_r * size, h_r * size, up_r * size
    # Centrage vertical de l'encre dans la bande, puis remontée à la ligne de base.
    ink_top = NAME_BAND_TOP + (band_h - ink_h) / 2
    baseline = ink_top + ink_up
    x = CARD_W_HALF - (ink_w + NAME_SHADOW_DX) / 2 - left_r * size
    return size, x, baseline


def personalize_card(guest_name: str, template_path: str = None) -> io.BytesIO:
    if template_path is None:
        template_path = CARD_TEMPLATE

    doc = pymupdf.open(template_path)
    page = doc[0]

    size, x, baseline = fit_guest_name(guest_name)

    # Ombre noire puis nom orange : même traitement que « Leslie » / « Fabrice ».
    page.insert_text((x + NAME_SHADOW_DX, baseline + NAME_SHADOW_DY), guest_name,
                     fontsize=size, fontname="Ams", fontfile=AMSTERDAM,
                     color=(0, 0, 0))
    page.insert_text((x, baseline), guest_name,
                     fontsize=size, fontname="Ams", fontfile=AMSTERDAM,
                     color=(0xE7 / 255.0, 0x6A / 255.0, 0x4A / 255.0))

    buf = io.BytesIO(doc.tobytes(garbage=3, deflate=True))
    doc.close()
    return buf


# ---------------------------------------------------------------------------
# Page 2 — page QR (même format que la page 1), fond blanc
# ---------------------------------------------------------------------------
def _split_table_label(table_name: str) -> tuple[str, str]:
    """
    « Table Triomphe - Victoire » -> ("Table Triomphe", "Victoire")
    « Table Leader »              -> ("Table Leader", "")

    Le nom principal est ramené en casse de titre : Amsterdam-Four est une
    script calligraphique dont les capitales sont illisibles (les glyphes
    s'enchevêtrent). La page 1 écrit d'ailleurs « Leslie » et « Fabrice »,
    pas « LESLIE » et « FABRICE ».
    """
    main, _, subtitle = table_name.partition(" - ")
    main, subtitle = main.strip(), subtitle.strip()
    if main.isupper():
        main = main.title()
    return main, subtitle


def _fit_size(c: canvas.Canvas, text: str, font: str, size: float,
              max_width: float) -> float:
    """Réduit `size` jusqu'à ce que `text` tienne dans `max_width`."""
    if not text:
        return size
    w = c.stringWidth(text, font, size)
    return size * (max_width / w) if w > max_width else size


def _draw_script_line(c: canvas.Canvas, text: str, cx: float, baseline: float,
                      size: float) -> None:
    """
    Dessine une ligne dans le style EXACT des prénoms de la page 1 :
    une ombre noire décalée puis le remplissage #E76A4A par-dessus.
    """
    c.setFont(TABLE_FONT, size)
    c.setFillColor(NAME_SHADOW)
    c.drawCentredString(cx + TABLE_SHADOW_DX, baseline + TABLE_SHADOW_DY, text)
    c.setFillColor(NAME_COLOR)
    c.drawCentredString(cx, baseline, text)


def _draw_qr_page(table_name: str, qr_content: str,
                  page_w: float = QR_PAGE_W, page_h: float = QR_PAGE_H,
                  qr_ratio: float = QR_RATIO_CARD) -> io.BytesIO:
    """
    Page QR, fond blanc, aux dimensions `page_w` x `page_h`.

    La mise en page est décrite dans le repère de référence de la carte
    (297.75 x 419.25) puis mise à l'échelle, si bien que PDF1 et PDF2
    partagent rigoureusement la même composition.

    `qr_ratio` fixe la grosseur du QR en fraction de la largeur de page.
    """
    qr_img = generate_qr_with_rings(qr_content)
    bg = Image.new("RGB", qr_img.size, "white")
    bg.paste(qr_img, mask=qr_img.split()[3] if qr_img.mode == "RGBA" else None)
    qr_img = bg

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_w, page_h))

    # Fond blanc sur toute la page cible
    c.setFillColor(QR_BG)
    c.rect(0, 0, page_w, page_h, stroke=0, fill=1)

    # Passage dans le repère « carte » : tout ce qui suit est exprimé en
    # unités de la page 1 du PDF1.
    c.saveState()
    c.scale(page_w / QR_PAGE_W, page_h / QR_PAGE_H)

    main, subtitle = _split_table_label(table_name)

    # --- Nom de la table : typographie des prénoms de la page 1 ---
    size = _fit_size(c, main, TABLE_FONT, TABLE_SIZE, TABLE_MAX_WIDTH)
    _draw_script_line(c, main, QR_PAGE_W / 2, QR_PAGE_H - TABLE_BASELINE_TOP, size)

    # --- Sous-titre éventuel (« Victoire »), discret, en Montserrat ---
    if subtitle:
        sub_size = _fit_size(c, subtitle, "Montserrat", 8.0, TABLE_MAX_WIDTH)
        c.setFont("Montserrat", sub_size)
        c.setFillColor(BODY_TEXT_COLOR)
        c.drawCentredString(QR_PAGE_W / 2, QR_PAGE_H - SUBTITLE_BASELINE_TOP,
                            subtitle)

    # --- Mention d'entrée (Montserrat, comme le corps de la carte) ---
    c.setFont("Montserrat", 9.5)
    c.setFillColor(BODY_TEXT_COLOR)
    c.drawCentredString(QR_PAGE_W / 2, QR_PAGE_H - MENTION_BASELINE_TOP,
                        "Présentez ce code QR à l'entrée")
    c.restoreState()

    # --- QR code : dessiné hors du repère mis à l'échelle pour rester
    #     parfaitement carré, quelle que soit la page cible.
    #     Il est centré dans la bande libre sous la mention. ---
    qr_size = page_w * qr_ratio
    pad = qr_size * 0.027
    cx = (page_w - qr_size) / 2
    band_top = page_h * (1 - (MENTION_BASELINE_TOP + QR_BAND_GAP) / QR_PAGE_H)
    band_bottom = page_h * (QR_BAND_BOTTOM / QR_PAGE_H)
    cy = band_bottom + (band_top - band_bottom - qr_size) / 2
    c.setStrokeColor(QR_FRAME)
    c.setLineWidth(0.7 * page_w / QR_PAGE_W)
    c.roundRect(cx - pad, cy - pad, qr_size + 2 * pad, qr_size + 2 * pad,
                pad * 1.2, stroke=1, fill=0)
    c.drawImage(ImageReader(qr_img), cx, cy, width=qr_size, height=qr_size,
                mask="auto")

    c.save()
    buf.seek(0)
    return buf


def _qr_content(table_name: str, guest_name: str, guest_id: str) -> str:
    """Contrat lu par le scanner : NOM|TABLE|ID, en majuscules."""
    return f"{guest_name.upper()}|{table_name.upper()}|{guest_id}"


# ---------------------------------------------------------------------------
# Zones cliquables de la page 1
# ---------------------------------------------------------------------------
def _rewire_page1_links(page, target_page_rect) -> dict:
    """
    Réécrit les 4 zones cliquables du billet maître :

      - la zone « Cliquez ici pour voir le billet » devient une ANCRE INTERNE
        (LINK_GOTO) vers la carte d'invitation, page 2 du même document ;
      - les 3 autres deviennent de vrais liens web (le gabarit maître porte
        des placeholders « https://ton-domaine.com/… » qu'il faut remplacer).

    Retourne le décompte par type, pour vérification.
    """
    web_targets = {
        ZONE_PRESENCE: URL_PRESENCE,
        ZONE_LIEU: LIEU_URL,
        ZONE_INFOS: URL_INFOS,
    }
    counts = {"anchor": 0, "web": 0, "unknown": 0}
    anchor_rect = None

    for link in page.get_links():
        uri = link.get("uri") or ""
        rect = link["from"]
        page.delete_link(link)

        if ZONE_BILLET in uri:
            anchor_rect = rect
            continue

        for fragment, target in web_targets.items():
            if fragment in uri:
                page.insert_link({
                    "kind": pymupdf.LINK_URI,
                    "from": rect,
                    "uri": target,
                })
                counts["web"] += 1
                break
        else:
            # Zone inconnue : on la conserve telle quelle plutôt que de la perdre.
            page.insert_link({"kind": pymupdf.LINK_URI, "from": rect, "uri": uri})
            counts["unknown"] += 1

    # L'ancre est posée en dernier : si le gabarit n'a pas de zone « billet »,
    # on retombe sur le rectangle de référence.
    if anchor_rect is None:
        anchor_rect = pymupdf.Rect(*RECT_BILLET_LINK)
    page.insert_link({
        "kind": pymupdf.LINK_GOTO,
        "from": anchor_rect,
        "page": ANCHOR_TARGET_PAGE,
        # Haut de la page cible, pour que la carte s'affiche entière.
        "to": pymupdf.Point(0, target_page_rect.height),
        "zoom": 0.0,
    })
    counts["anchor"] += 1
    return counts


# ---------------------------------------------------------------------------
# Le PDF complet : 3 pages
# ---------------------------------------------------------------------------
def generate_invitation(guest_name: str, table_name: str, guest_id: str,
                        template_path: str = None) -> bytes:
    """
    Assemble le document unique de 3 pages :
        1. billet maître (zones cliquables)
        2. carte d'invitation personnalisée au nom de l'invité
        3. page QR, aux dimensions de la page 1

    L'assemblage se fait avec PyMuPDF : les liens des pages sources sont
    conservés, et l'ancre interne ne peut être posée qu'une fois les 3 pages
    réunies (l'index de page n'existe pas avant).
    """
    out_doc = pymupdf.open()

    # --- page 1 : le billet maître ---
    with pymupdf.open(MASTER_BILLET) as master:
        out_doc.insert_pdf(master, from_page=0, to_page=0)
    billet_rect = out_doc[0].rect

    # --- page 2 : la carte personnalisée ---
    card_buf = personalize_card(guest_name, template_path)
    with pymupdf.open(stream=card_buf.getvalue(), filetype="pdf") as card:
        out_doc.insert_pdf(card, from_page=0, to_page=0)

    # --- page 3 : la page QR, aux dimensions de la page 1 ---
    qr_buf = _draw_qr_page(
        table_name,
        _qr_content(table_name, guest_name, guest_id),
        page_w=billet_rect.width,
        page_h=billet_rect.height,
        qr_ratio=QR_RATIO_BILLET,
    )
    with pymupdf.open(stream=qr_buf.getvalue(), filetype="pdf") as qr:
        out_doc.insert_pdf(qr, from_page=0, to_page=0)

    # --- zones cliquables : ancre interne + liens web ---
    _rewire_page1_links(out_doc[0], out_doc[ANCHOR_TARGET_PAGE].rect)

    data = out_doc.tobytes(garbage=3, deflate=True)
    out_doc.close()
    return data


if __name__ == "__main__":
    pdf = generate_invitation("Rostand Essima", "Table Triomphe - Victoire",
                              "guest-001")
    out = os.path.join(os.path.dirname(__file__), "test-invitation.pdf")
    with open(out, "wb") as f:
        f.write(pdf)
    print(f"[PDF] {out}: {len(pdf)} octets")