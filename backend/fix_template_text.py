"""
fix_template_text.py — Corrige une ligne de texte du gabarit invitation-carte.pdf
sans retoucher le fond (vert texturé + ornements).

Chaque ligne du gabarit est un mini flux de contenu isolé du type :

    q BT 1 0 0 1 <x> <y> Tm /MRegular 6.2 Tf 1 1 1 rg [<CID CID ...>]TJ ET Q

Les glyphes sont des CID sur 2 octets d'une police sous-ensemblée : on ne peut
donc pas remplacer « DJUIGUIM » par « DJIMGUIN » en clair. La table
code <-> caractère est reconstruite en alignant les CID du flux avec le texte
extrait par PyMuPDF, ce qui permet de réencoder la ligne corrigée. Toutes les
lettres nécessaires figurent déjà dans la ligne d'origine, donc dans le
sous-ensemble embarqué.

La ligne est ensuite recentrée sur son centre optique initial.

Usage :
    python fix_template_text.py --dry-run
    python fix_template_text.py
"""
import argparse
import os
import re
import shutil
import sys

import pymupdf

_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(_HERE, "templates", "invitation-carte.pdf")

WRONG = "DJUIGUIM"
RIGHT = "DJIMGUIN"

_HEX_TJ = re.compile(rb"\[<([0-9A-Fa-f]+)>\]\s*TJ")
_TM = re.compile(rb"([-\d.]+)\s+([-\d.]+)\s+Tm")


def _codes(hex_bytes: bytes) -> list[str]:
    s = hex_bytes.decode("ascii")
    return [s[i:i + 4] for i in range(0, len(s), 4)]


def find_line_stream(doc: pymupdf.Document, needle: str):
    """Renvoie (xref, raw, codes, texte) du flux contenant `needle`."""
    page = doc[0]
    target = None
    for b in page.get_text("dict")["blocks"]:
        if b["type"] != 0:
            continue
        for l in b["lines"]:
            for s in l["spans"]:
                if needle in s["text"]:
                    target = s
    if target is None:
        raise SystemExit(f"Texte {needle!r} absent du gabarit.")

    text = target["text"]
    for xref in page.get_contents():
        raw = doc.xref_stream(xref)
        m = _HEX_TJ.search(raw)
        if not m:
            continue
        codes = _codes(m.group(1))
        if len(codes) == len(text):
            return xref, raw, codes, text
    raise SystemExit("Flux de contenu correspondant introuvable.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    doc = pymupdf.open(TEMPLATE)
    xref, raw, codes, text = find_line_stream(doc, WRONG)
    print(f"[INFO] flux xref {xref} : {text!r}")

    # Table caractère -> CID, reconstruite depuis la ligne elle-même.
    charmap: dict[str, str] = {}
    for ch, code in zip(text, codes):
        charmap.setdefault(ch, code)

    new_text = text.replace(WRONG, RIGHT)
    missing = sorted({c for c in new_text if c not in charmap})
    if missing:
        raise SystemExit(f"Glyphes absents du sous-ensemble : {missing}")
    print(f"[INFO] corrigé  : {new_text!r}")

    new_hex = "".join(charmap[c] for c in new_text).encode("ascii")
    new_raw = _HEX_TJ.sub(b"[<" + new_hex + b">]TJ", raw, count=1)

    # Centre optique d'origine, à préserver après le changement de largeur.
    span = next(s for b in doc[0].get_text("dict")["blocks"] if b["type"] == 0
                for l in b["lines"] for s in l["spans"] if WRONG in s["text"])
    center_before = (span["bbox"][0] + span["bbox"][2]) / 2

    if args.dry_run:
        print("[DRY] aucune écriture. Centre initial:", round(center_before, 2))
        return

    shutil.copyfile(TEMPLATE, TEMPLATE + ".bak")
    doc.update_stream(xref, new_raw)
    doc.saveIncr()
    doc.close()

    # Recentrage : on mesure la nouvelle largeur puis on décale le Tm.
    doc = pymupdf.open(TEMPLATE)
    span = next(s for b in doc[0].get_text("dict")["blocks"] if b["type"] == 0
                for l in b["lines"] for s in l["spans"] if RIGHT in s["text"])
    center_after = (span["bbox"][0] + span["bbox"][2]) / 2
    dx = center_before - center_after
    print(f"[INFO] centre {center_before:.2f} -> {center_after:.2f} (dx {dx:+.2f})")

    if abs(dx) > 0.05:
        raw2 = doc.xref_stream(xref)
        m = _TM.search(raw2)
        x, y = float(m.group(1)), float(m.group(2))
        raw2 = raw2[:m.start()] + f"{x + dx:.5f} {y:.5f} Tm".encode() + raw2[m.end():]
        doc.update_stream(xref, raw2)
        doc.saveIncr()
        doc.close()
        doc = pymupdf.open(TEMPLATE)
        span = next(s for b in doc[0].get_text("dict")["blocks"] if b["type"] == 0
                    for l in b["lines"] for s in l["spans"] if RIGHT in s["text"])
        print(f"[INFO] recentré : {(span['bbox'][0] + span['bbox'][2]) / 2:.2f}")

    print("[OK] gabarit corrigé :", TEMPLATE, "(sauvegarde .bak)")


if __name__ == "__main__":
    main()
