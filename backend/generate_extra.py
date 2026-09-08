"""
generate_extra.py — Génère un billet fusionné unique sans l'ajouter à GUESTS.

Usage :
    python generate_extra.py "Table Sublime" "Enfoire" extra-001

Le billet est écrit dans fusionnes/<Table>/Billet - <Nom>.pdf.
Il n'est pas importé dans Firestore.
"""
import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_fusion_v2 import (
    OUT_DIR,
    PAGE1_NEW_PNG,
    PROGRAMME,
    _safe,
    build_page1_base,
    make_one,
)

sys.stdout.reconfigure(encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_extra.py <table> <nom> [id]")
        sys.exit(1)
    table = sys.argv[1]
    name = sys.argv[2]
    gid = sys.argv[3] if len(sys.argv) > 3 else "extra-001"

    page1_base = build_page1_base()
    programme = pymupdf.open(PROGRAMME)

    out = pymupdf.open()
    make_one(out, name, table, gid, page1_base, programme)

    table_dir = os.path.join(OUT_DIR, _safe(table))
    os.makedirs(table_dir, exist_ok=True)
    dst = os.path.join(table_dir, f"Billet - {name}.pdf")
    out.save(dst, garbage=3, deflate=True)
    out.close()

    page1_base.close()
    programme.close()
    print(f"Généré : {dst}")


if __name__ == "__main__":
    main()
