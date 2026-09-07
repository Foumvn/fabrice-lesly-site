"""Inspecte la structure d'un PDF généré : pages, dimensions, liens, ancres."""
import argparse
import os

import pymupdf

_HERE = os.path.dirname(os.path.abspath(__file__))
KIND = {
    pymupdf.LINK_NONE: "NONE",
    pymupdf.LINK_GOTO: "GOTO (ancre interne)",
    pymupdf.LINK_URI: "URI (web)",
    pymupdf.LINK_LAUNCH: "LAUNCH",
    pymupdf.LINK_GOTOR: "GOTOR (autre fichier)",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", nargs="?",
                    default=os.path.join(_HERE, "test-invitation.pdf"))
    args = ap.parse_args()

    doc = pymupdf.open(args.pdf)
    print(f"{os.path.basename(args.pdf)} — {len(doc)} pages, "
          f"{os.path.getsize(args.pdf)/1e6:.2f} Mo")
    for i, page in enumerate(doc):
        print(f"\n  page {i+1}: {page.rect.width:.2f} x {page.rect.height:.2f} "
              f"(ratio {page.rect.width/page.rect.height:.4f})")
        links = page.get_links()
        if not links:
            print("      aucun lien")
        for l in links:
            r = l["from"]
            label = KIND.get(l["kind"], l["kind"])
            extra = ""
            if l["kind"] == pymupdf.LINK_GOTO:
                extra = f" -> page {l.get('page', -1) + 1}, to={l.get('to')}"
            elif l["kind"] == pymupdf.LINK_URI:
                extra = f" -> {l.get('uri')}"
            print(f"      [{label}] rect=({r.x0:.0f},{r.y0:.0f},"
                  f"{r.x1:.0f},{r.y1:.0f}){extra}")
        txt = page.get_text().strip().replace("\n", " | ")
        if txt:
            print(f"      texte: {txt[:150]!r}")
    doc.close()


if __name__ == "__main__":
    main()
