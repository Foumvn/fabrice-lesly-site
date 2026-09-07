"""
generation_locale.py — Génération batch LOCALE du PDF unique de chaque invité.

Entrée :  data/invites.csv  (colonnes table_name, table_subtitle, table_theme, guest_name)

Sortie :  template/Billet/<Nom de l'invité>/invitation.pdf   (3 pages)
              page 1 : billet, avec ancre interne vers la page 2 + 3 liens web
              page 2 : carte d'invitation personnalisée
              page 3 : page QR

Usage :
    python generation_locale.py                 # tout le CSV
    python generation_locale.py --ids 1 2 3     # uniquement les invités 1,2,3
"""
import argparse
import csv
import json
import os
import sys

import pymupdf

from import_csv import parse_csv
from pdf_generator import (ANCHOR_TARGET_PAGE, PDF_FILENAME, URL_INFOS,
                           URL_PRESENCE, LIEU_URL, generate_invitation)

_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_ROOT = os.path.dirname(_HERE)                 # template/
DATA_CSV = os.path.join(_HERE, "data", "invites.csv")
OUT_ROOT = os.path.join(_TEMPLATE_ROOT, "Billet")

MAX_WID = "\\/:*?\"<>|"


def safe_name(name: str) -> str:
    return "".join("-" if c in MAX_WID else c for c in name).strip()


def load_guests(csv_path: str = DATA_CSV) -> list[dict]:
    guests = parse_csv(csv_path)
    for i, g in enumerate(guests, start=1):
        g["id"] = f"guest-{i:03d}"
    return guests


def _is_white(page) -> bool:
    """Le fond de la page QR doit être blanc (échantillon des coins)."""
    pix = page.get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
    for x, y in [(3, 3), (pix.width - 4, 3), (3, pix.height - 4), (pix.width - 4, pix.height - 4)]:
        i = getattr(pix, "pixel")(x, y)
        if min(i) < 245:
            return False
    return True


def verify(pdf_path: str, guest: dict, report: dict) -> dict:
    """
    Contrôles PyMuPDF du PDF unique de 3 pages :
      - structure (3 pages, dimensions, ratios)
      - page 1 : l'ancre interne pointe bien sur la page 2, et les 3 liens
        web ne contiennent plus de placeholder « ton-domaine.com »
      - page 2 : le nom de l'invité y figure
      - page 3 : nom de table, mention, QR, fond blanc, dimensions = page 1
    """
    d = pymupdf.open(pdf_path)
    report["pages"] = len(d)
    if len(d) != 3:
        d.close()
        return report

    page1, page2, page3 = d[0], d[1], d[2]
    for idx, page in enumerate((page1, page2, page3), start=1):
        report[f"page{idx}_size"] = f"{page.rect.width:.1f}x{page.rect.height:.1f}"

    # --- page 1 : ancre interne + liens web ---
    links = page1.get_links()
    report["links"] = len(links)
    anchors = [l for l in links if l["kind"] == pymupdf.LINK_GOTO]
    web = [l for l in links if l["kind"] == pymupdf.LINK_URI]
    report["anchor_count"] = len(anchors)
    report["anchor_targets_page2"] = (
        len(anchors) == 1 and anchors[0].get("page") == ANCHOR_TARGET_PAGE
    )
    report["web_link_count"] = len(web)
    uris = [l.get("uri") or "" for l in web]
    report["no_placeholder_url"] = not any("ton-domaine.com" in u for u in uris)
    report["expected_web_urls"] = sorted(uris) == sorted(
        [URL_PRESENCE, LIEU_URL, URL_INFOS]
    )

    # --- page 2 : la carte personnalisée ---
    report["name_on_page2"] = guest["name"] in page2.get_text().replace("\xa0", " ")

    # --- page 3 : la page QR ---
    report["qr_page_white"] = _is_white(page3)
    report["qr_image_on_page3"] = bool(page3.get_images(full=True))
    report["page3_size_matches_page1"] = (
        abs(page1.rect.width - page3.rect.width) < 0.5
        and abs(page1.rect.height - page3.rect.height) < 0.5
    )
    qr_text = page3.get_text().replace("\xa0", " ")
    # Le nom de table est écrit en casse de titre (typographie des prénoms) :
    # on compare donc sans tenir compte de la casse.
    main_table = guest["table_name"].partition(" - ")[0].strip()
    report["table_on_page3"] = main_table.lower() in qr_text.lower()
    report["mention_on_page3"] = "PRÉSENTEZ CE CODE QR" in qr_text.upper()

    d.close()
    return report


def generate_one(guest: dict) -> dict:
    name = guest["name"]
    table = guest["table_name"]
    gid = guest["id"]
    folder = safe_name(name)

    guest_dir = os.path.join(OUT_ROOT, folder)
    os.makedirs(guest_dir, exist_ok=True)
    path_pdf = os.path.join(guest_dir, PDF_FILENAME)

    pdf = generate_invitation(name, table, gid)
    with open(path_pdf, "wb") as f:
        f.write(pdf)

    return {
        "guest_id": gid,
        "name": name,
        "folder": folder,
        "table": table,
        "path": path_pdf,
        "size": len(pdf),
        "verify": verify(path_pdf, guest, {}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="*", type=int, default=None,
                        help="Invités à générer (1 = premier du CSV)")
    parser.add_argument("--json", help="Chemin optionnel du rapport JSON")
    args = parser.parse_args()

    guests = load_guests()
    if args.ids:
        guests = [g for i, g in enumerate(guests, 1) if i in args.ids]
        if not guests:
            print("Aucun invité sélectionné.")
            sys.exit(1)

    os.makedirs(OUT_ROOT, exist_ok=True)

    report = {"total": len(guests), "ok": 0, "errors": [], "guests": []}
    for g in guests:
        try:
            r = generate_one(g)
            report["guests"].append(r)
            v = r["verify"]
            failed = [k for k, val in v.items() if isinstance(val, bool) and not val]
            if v.get("pages") != 3 or failed:
                report["errors"].append({"guest_id": r["guest_id"],
                                         "name": r["name"],
                                         "failed_checks": failed or ["pages != 3"]})
                print(f"[KO] {r['guest_id']} {g['name']}  echecs={failed}")
                continue
            report["ok"] += 1
            print(f"[OK] {r['guest_id']} {g['name']}  "
                  f"pages={v['pages']} ancre->p{v['anchor_count'] and 2} "
                  f"web={v['web_link_count']} nom_p2={v['name_on_page2']}")
        except Exception as e:
            report["errors"].append({"guest_id": g.get("id"), "name": g.get("name"), "error": str(e)})
            print(f"[ERR] {g.get('id')} {g.get('name')}: {e}")

    print(f"\nTerminé : {report['ok']}/{report['total']} invités dans {OUT_ROOT}")
    if report["errors"]:
        print("Erreurs:", report["errors"])

    json_path = args.json or os.path.join(OUT_ROOT, "rapport-complet.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("Rapport:", json_path)


if __name__ == "__main__":
    main()