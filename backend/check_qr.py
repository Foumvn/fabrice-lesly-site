"""
Contrôle qualité : décode le QR de la page 2 de chaque PDF généré et le
compare au contrat NOM|TABLE|ID attendu par le scanner.

Le décodage utilise zxing-cpp (ZXing), l'implémentation de référence dont
dérivent la plupart des lecteurs mobiles — bien plus fiable que le détecteur
d'OpenCV, qui échoue sur des QR parfaitement valides.

Chaque page est testée à plusieurs résolutions pour simuler des conditions de
scan variées (photo lointaine, capture rapprochée).

    python check_qr.py            # tout le rapport
    python check_qr.py --dpi 96 150 250
"""
import argparse
import json
import os

import numpy as np
import pymupdf
import zxingcpp

_HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(os.path.dirname(_HERE), "Billet", "rapport-complet.json")
DEFAULT_DPI = (72, 100, 150, 200, 300)
QR_PAGE_INDEX = 2   # page 3 du document unique


def decode_page(page, dpi: int) -> str:
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
        pix.height, pix.width, pix.n
    )
    results = zxingcpp.read_barcodes(img)
    return results[0].text if results else ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dpi", nargs="*", type=int, default=list(DEFAULT_DPI))
    parser.add_argument("--report", default=REPORT)
    args = parser.parse_args()

    report = json.load(open(args.report, encoding="utf-8"))
    checks, failures = 0, []

    for guest in report["guests"]:
        expected = "{}|{}|{}".format(
            guest["name"].upper(), guest["table"].upper(), guest["guest_id"]
        )
        doc = pymupdf.open(guest["path"])
        # Le QR est sur la page 3 du document unique.
        qr_page = doc[QR_PAGE_INDEX]
        for dpi in args.dpi:
            checks += 1
            got = decode_page(qr_page, dpi)
            if got != expected:
                failures.append((guest["name"], dpi, got, expected))
        doc.close()

    print(f"QR décodés : {checks - len(failures)}/{checks} "
          f"({len(report['guests'])} invités x {len(args.dpi)} dpi)")
    for name, dpi, got, exp in failures:
        print(f"  ECHEC {name} {dpi}dpi: {got!r} != {exp!r}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
