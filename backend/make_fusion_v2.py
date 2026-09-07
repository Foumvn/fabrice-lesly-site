"""
make_fusion_v2.py — Régénère les billets fusionnés de 4 pages (1058 x 1486 pt).

Nouveautés par rapport à make_fusion.py :
  page 1 : NOUVELLE enveloppe « page 1 new.png » (faute de français corrigée),
           avec les MÊMES ancres internes que l'existant :
             - enveloppe (128, 515, 926, 998) -> page 2 (carte d'invitation)
             - bouton lieu  (385, 1205, 685, 1430) -> page 3 (programme)
  page 2 : carte d'invitation personnalisée — reprise telle quelle de la
           fusion existante (ou du dossier Billet/<Nom>/, ou générée depuis
           le gabarit pour les nouveaux invités)
  page 3 : Programme - Fabrice et Leslie.pdf (inchangé)
  page 4 : page QR régénérée avec la NOUVELLE numérotation guest-001..025
           (contrat du scanner : NOM|TABLE|ID, en majuscules)

Nouveau plan de table (renumérotation complète) :
  guest-001..010 -> Table Apogée
  guest-011..020 -> Table Couronne
  guest-021..023 -> Table Majesté   (Delano Saha, Priscillia Ondo, Opportun Enyegue)
  guest-024..025 -> Billets cartonnés (Mama Denise, Mama Léopoldine)
  Table Triomphe - Victoire : vide (aucun invité)

Les anciennes fusions sont sauvegardées dans fusionnes/_ancien_<date>/.

Usage :
    python make_fusion_v2.py
"""
import os
import shutil
import sys
import datetime

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdf_generator import _draw_qr_page, _qr_content, QR_RATIO_BILLET, personalize_card

sys.stdout.reconfigure(encoding="utf-8")

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)                       # template/
BILLETS = os.path.join(_ROOT, "rendu billet", "billets")
OUT_DIR = os.path.join(BILLETS, "fusionnes")
PAGE1_NEW_PNG = os.path.join(BILLETS, "page 1 new.png")
PROGRAMME = os.path.join(BILLETS, "Programme - Fabrice et Leslie.pdf")
GUESTS_DIR = os.path.join(_ROOT, "Billet")

PAGE_W, PAGE_H = 1058.0, 1486.0

# Zones cliquables de la page 1 — identiques à l'existant (relevées sur billet.png)
LINK_ENVELOPPE = (128, 515, 926, 998)     # -> page 2 (carte d'invitation)
LINK_LIEU = (385, 1205, 685, 1430)        # -> page 3 (programme)

# Nouveaux liens externes sur la page 1 (bas de page)
LINK_PRESENCE = (80, 1205, 380, 1430)     # -> /presence
LINK_INFO = (688, 1205, 988, 1430)        # -> /

# ---------------------------------------------------------------------------
# Nouveau plan de table (ordre = nouvelle numérotation guest-001..029)
# ---------------------------------------------------------------------------
APOGEE = [
    "Gisèle Akono", "Andrea Song", "Armel Mboh", "Diane Ebissesseye",
    "Jules Ngono", "Mikael Ebassa", "Vanessa Foumane", "Pangrasse Angoni",
    "Felicien Fodsoh", "Michou Fezeu",
]
COURONNE = [
    "Ornella Messina", "Falone Kakeu", "Melissa Ntsoumba", "Muriel Akono",
    "Synthia Akono", "Ingrid Tang", "Kendal Bebine", "Norvège",
    "Leslie Abbia", "Anastasie Mandeng",
]
MAJESTE = [
    "Delano Saha", "Priscillia Ondo", "Opportun Enyegue",
    "Dorice Tsogo", "Dodine", "Ronel", "Olivia Mengue",
]
CARTONNES = ["Mama Denise", "Mama Léopoldine"]

GUESTS = (
    [("Table Apogée", n) for n in APOGEE]
    + [("Table Couronne", n) for n in COURONNE]
    + [("Table Majesté", n) for n in MAJESTE]
    + [("Billets cartonnés", n) for n in CARTONNES]
)


def _safe(name: str) -> str:
    return "".join("-" if c in '\\/:*?"<>|' else c for c in name).strip()


def build_page1_base() -> pymupdf.Document:
    """Document d'une page : la nouvelle enveloppe « page 1 new.png »."""
    doc = pymupdf.open()
    page = doc.new_page(width=PAGE_W, height=PAGE_H)
    page.insert_image(pymupdf.Rect(0, 0, PAGE_W, PAGE_H), filename=PAGE1_NEW_PNG)
    return doc


def make_one(out: pymupdf.Document, name: str, table: str, gid: str,
             page1_base: pymupdf.Document,
             programme: pymupdf.Document) -> None:
    # --- page 1 : la nouvelle enveloppe ---
    out.insert_pdf(page1_base)

    old_fusion = os.path.join(OUT_DIR, f"Billet - {name}.pdf")
    invitation_pdf = os.path.join(GUESTS_DIR, _safe(name), "invitation.pdf")

    if os.path.exists(old_fusion):
        # Carte + programme reprises telles quelles de la fusion existente
        # (pages 2 et 3, index 1 et 2).
        with pymupdf.open(old_fusion) as src:
            out.insert_pdf(src, from_page=1, to_page=2)
    else:
        # Carte personnalisée : dossier Billet/<Nom>/ ou gabarit
        p2 = out.new_page(width=PAGE_W, height=PAGE_H)
        if os.path.exists(invitation_pdf):
            with pymupdf.open(invitation_pdf) as inv:
                p2.show_pdf_page(p2.rect, inv, 1)
        else:
            card_buf = personalize_card(name)
            with pymupdf.open(stream=card_buf.getvalue(), filetype="pdf") as card:
                p2.show_pdf_page(p2.rect, card, 0)

        # Programme
        p3 = out.new_page(width=PAGE_W, height=PAGE_H)
        p3.show_pdf_page(p3.rect, programme, 0)

    # --- page 4 : QR régénéré (nouvelle numérotation) ---
    qr = _draw_qr_page(table, _qr_content(table, name, gid),
                       page_w=PAGE_W, page_h=PAGE_H, qr_ratio=QR_RATIO_BILLET)
    with pymupdf.open(stream=qr.getvalue(), filetype="pdf") as q:
        out.insert_pdf(q)

    # --- ancres internes de la page 1, identiques à l'existant ---
    p1 = out[0]
    p1.insert_link({"kind": pymupdf.LINK_GOTO,
                    "from": pymupdf.Rect(*LINK_ENVELOPPE), "page": 1})
    p1.insert_link({"kind": pymupdf.LINK_GOTO,
                    "from": pymupdf.Rect(*LINK_LIEU), "page": 2})

    # --- liens externes (bas de page 1) ---
    p1.insert_link({"kind": pymupdf.LINK_URI,
                    "from": pymupdf.Rect(*LINK_PRESENCE),
                    "uri": "https://fabrice-leslie-two.vercel.app/presence"})
    p1.insert_link({"kind": pymupdf.LINK_URI,
                    "from": pymupdf.Rect(*LINK_INFO),
                    "uri": "https://fabrice-leslie-two.vercel.app/"})


def main():
    stamp = datetime.date.today().isoformat()
    backup_dir = os.path.join(OUT_DIR, f"_ancien_{stamp}")

    # 1. Sauvegarde de toutes les anciennes fusions
    old_files = [f for f in os.listdir(OUT_DIR) if f.endswith(".pdf")]
    if old_files:
        os.makedirs(backup_dir, exist_ok=True)
        for f in old_files:
            shutil.copy2(os.path.join(OUT_DIR, f), os.path.join(backup_dir, f))
        print(f"Sauvegarde de {len(old_files)} anciennes fusions -> {backup_dir}")

    # 2. Génération des nouvelles fusions
    page1_base = build_page1_base()
    programme = pymupdf.open(PROGRAMME)

    ok, err = 0, []
    for i, (table, name) in enumerate(GUESTS, start=1):
        gid = f"guest-{i:03d}"
        try:
            out = pymupdf.open()
            make_one(out, name, table, gid, page1_base, programme)
            dst = os.path.join(OUT_DIR, f"Billet - {name}.pdf")
            out.save(dst, garbage=3, deflate=True)
            out.close()
            ok += 1
            print(f"[OK] {gid}  {name:24} {table:17} ({os.path.basename(dst)})")
        except Exception as e:
            err.append((name, str(e)))
            print(f"[ERREUR] {gid} {name} : {e}")

    page1_base.close()
    programme.close()

    # 3. Retirer les anciennes fusions dont les invités ne sont plus dans la liste
    kept = {f"Billet - {n}.pdf" for _, n in GUESTS}
    removed = 0
    for f in old_files:
        if f not in kept:
            os.remove(os.path.join(OUT_DIR, f))
            removed += 1
            print(f"[RETIRE] {f} (invité absent du nouveau plan)")

    print(f"\nTerminé : {ok}/{len(GUESTS)} billets générés dans {OUT_DIR}")
    print(f"Retirés : {removed} (invités hors nouveau plan ; sauvegarde dans {backup_dir})")
    if err:
        print("Échecs :", err)


if __name__ == "__main__":
    main()
