"""
make_fusion.py — Billet fusionné de 4 pages pour les 26 invités.

Chaque PDF produit, aux dimensions uniformes 1058 x 1486 pt :
  page 1 : billet.png (enveloppe), avec liens internes
             - enveloppe        -> page 2 (invitation)
             - bouton lieu      -> page 3 (programme)
  page 2 : carte d'invitation personnalisée (Billet/<Nom>/invitation.pdf p.2)
  page 3 : Programme - Fabrice et Leslie.pdf
  page 4 : page QR régénérée avec la NOUVELLE table de l'invité :
             invités  1-10 -> Table Apogée
             invités 11-20 -> Table Couronne
             invités 21-26 -> Table Majesté
           contenu du QR : NOM|TABLE|ID (contrat du scanner).

Sortie : rendu billet/billets/fusionnes/Billet - <Nom>.pdf

Usage :
    python make_fusion.py
"""
import os
import sys
import unicodedata

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from import_csv import parse_csv
from pdf_generator import _draw_qr_page, _qr_content, QR_RATIO_BILLET

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
BILLETS = os.path.join(_ROOT, "rendu billet", "billets")
OUT_DIR = os.path.join(BILLETS, "fusionnes")
BILLET_PNG = os.path.join(BILLETS, "billet.png")
PROGRAMME = os.path.join(BILLETS, "Programme - Fabrice et Leslie.pdf")
GUESTS_DIR = os.path.join(_ROOT, "Billet")

PAGE_W, PAGE_H = 1058.0, 1486.0   # même ratio que la carte (298 x 419)

# Zones cliquables de la page 1 (relevées sur billet.png)
LINK_ENVELOPPE = (128, 515, 926, 998)     # -> page 2
LINK_LIEU = (385, 1205, 685, 1430)        # -> page 3

# Les 26 invités, dans l'ordre donné (1-26)
INVITES = [
    "Gisèle Akono", "Andrea Song", "Armel Mboh", "Diane Ebissesseye",
    "Jules Ngono", "Mikael Ebassa", "Vanessa Foumane", "Pangrasse Angoni",
    "Felicien Fodsoh", "Michou Fezeu", "Ornella Messina", "Falone Kakeu",
    "Melissa Ntsoumba", "Muriel Akono", "Synthia Akono", "Ingrid Tang",
    "Kendal Bebine", "Norvège", "Leslie Abbia", "Anastasie Mandeng",
    "Dodine", "Olivia Mengue", "Ronel Tchoulayeu", "Alex", "Dorice Tsogo",
    "Manuella Foumane",
]


def table_of(index: int) -> str:
    """index 1-26 -> nom de la nouvelle table."""
    if index <= 10:
        return "Table Apogée"
    if index <= 20:
        return "Table Couronne"
    return "Table Majesté"


def _norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn").strip()


def build_index() -> dict:
    """Nom normalisé -> (dossier Billet/<Nom>, id guest-NNN du CSV)."""
    guests = parse_csv(os.path.join(_HERE, "data", "invites.csv"))
    index = {}
    for i, g in enumerate(guests, start=1):
        index[_norm(g["name"])] = (g["name"], f"guest-{i:03d}")
    return index


def _safe(name: str) -> str:
    return "".join("-" if c in '\\/:*?"<>|' else c for c in name).strip()


def make_one(out: pymupdf.Document, name: str, table: str, gid: str,
             invitation_pdf: str, billet: pymupdf.Document,
             programme: pymupdf.Document) -> None:
    # Page 1 : billet (les liens sont posés après création des pages cibles)
    p1 = out.new_page(width=PAGE_W, height=PAGE_H)
    p1.show_pdf_page(p1.rect, billet, 0)

    # Page 2 : carte d'invitation personnalisée (mise à l'échelle, ratio id.)
    with pymupdf.open(invitation_pdf) as inv:
        p2 = out.new_page(width=PAGE_W, height=PAGE_H)
        p2.show_pdf_page(p2.rect, inv, 1)

    # Page 3 : programme (même ratio -> agrandi sans distorsion)
    p3 = out.new_page(width=PAGE_W, height=PAGE_H)
    p3.show_pdf_page(p3.rect, programme, 0)

    # Page 4 : QR régénéré avec la nouvelle table
    qr = _draw_qr_page(table, _qr_content(table, name, gid),
                       page_w=PAGE_W, page_h=PAGE_H, qr_ratio=QR_RATIO_BILLET)
    with pymupdf.open(stream=qr.getvalue(), filetype="pdf") as q:
        out.insert_pdf(q)

    # Liens internes de la page 1 (pages 2 et 3 existent désormais ; l'objet
    # page est rechargé car insert_pdf invalide la référence précédente)
    p1 = out[0]
    p1.insert_link({"kind": pymupdf.LINK_GOTO,
                    "from": pymupdf.Rect(*LINK_ENVELOPPE), "page": 1})
    p1.insert_link({"kind": pymupdf.LINK_GOTO,
                    "from": pymupdf.Rect(*LINK_LIEU), "page": 2})


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(OUT_DIR, exist_ok=True)
    index = build_index()
    billet = pymupdf.open()
    bp = billet.new_page(width=PAGE_W, height=PAGE_H)
    bp.insert_image(pymupdf.Rect(0, 0, PAGE_W, PAGE_H), filename=BILLET_PNG)
    programme = pymupdf.open(PROGRAMME)

    ok, err = 0, []
    for i, nom in enumerate(INVITES, start=1):
        found = index.get(_norm(nom))
        if not found:
            err.append(nom)
            print(f"[??] {nom} : introuvable dans le CSV")
            continue
        real_name, gid = found
        inv_pdf = os.path.join(GUESTS_DIR, _safe(real_name), "invitation.pdf")
        if not os.path.exists(inv_pdf):
            err.append(nom)
            print(f"[??] {nom} : {inv_pdf} absent")
            continue
        table = table_of(i)
        out = pymupdf.open()
        make_one(out, real_name, table, gid, inv_pdf, billet, programme)
        dst = os.path.join(OUT_DIR, f"Billet - {real_name}.pdf")
        out.save(dst, garbage=3, deflate=True)
        out.close()
        ok += 1
        print(f"[OK] {i:2d} {real_name:26} {table:15} -> {os.path.basename(dst)}")
    billet.close()
    programme.close()
    print(f"\nTerminé : {ok}/{len(INVITES)} billets dans {OUT_DIR}")
    if err:
        print("Non faits :", err)


if __name__ == "__main__":
    main()
