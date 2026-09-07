"""
deploy_public.py — Diffusion locale + mise à jour Firestore des PDFs.

1. Copie   template/Billet/<Invité>/invitation.pdf
        -> template/public/billets/<Invité>/invitation.pdf
   (le serveur Next le sert ensuite sur http://localhost:3000/billets/...)
2. Met à jour dans Firestore (via les routes Next.js) :
      pdfUrl       = invitation.pdf servi localement
      cloudPdfUrl  = invitation.pdf sur Cloudinary (si disponible)

Usage :
    python deploy_public.py            # copie + Firestore
    python deploy_public.py --no-copy  # seulement Firestore
"""
import argparse
import json
import os
import shutil

import requests

from pdf_generator import PDF_FILENAME

_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_ROOT = os.path.dirname(_HERE)
REPORT = os.path.join(_TEMPLATE_ROOT, "Billet", "rapport-complet.json")
CLOUDY_JSON = os.path.join(_TEMPLATE_ROOT, "Billet", "urls-cloudinary.json")
PUBLIC_BILLETS = os.path.join(_TEMPLATE_ROOT, "public", "billets")

NEXT_BASE = os.environ.get("PUBLIC_BASE_URL", "http://localhost:3000").rstrip("/")
SERVE_DIR = "billets"


def _served_url(guest_folder: str, filename: str) -> str:
    from urllib.parse import quote
    return f"{NEXT_BASE}/{SERVE_DIR}/{quote(guest_folder, safe='')}/{quote(filename, safe='')}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-copy", action="store_true")
    args = parser.parse_args()

    report = json.load(open(REPORT, encoding="utf-8"))
    cloudy = {}
    if os.path.exists(CLOUDY_JSON):
        for e in json.load(open(CLOUDY_JSON, encoding="utf-8")):
            cloudy[e["guest_id"]] = e.get("cloudinary") or {}

    if not args.no_copy:
        if os.path.isdir(PUBLIC_BILLETS):
            shutil.rmtree(PUBLIC_BILLETS)
        os.makedirs(PUBLIC_BILLETS, exist_ok=True)

    ok, errors = 0, []
    for g in report["guests"]:
        gid = g["guest_id"]
        folder = g["folder"]
        try:
            if not args.no_copy:
                dst_dir = os.path.join(PUBLIC_BILLETS, folder)
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copyfile(g["path"],
                                os.path.join(dst_dir, PDF_FILENAME))

            payload = {
                "pdfUrl": _served_url(folder, PDF_FILENAME),
                "status": "uploaded",
                "folder": folder,
            }
            cl = cloudy.get(gid, {})
            if cl.get("secure_url"):
                payload["cloudPdfUrl"] = cl["secure_url"]

            r = requests.put(f"{NEXT_BASE}/api/guests/{gid}", json=payload, timeout=30)
            if r.status_code == 200:
                ok += 1
            else:
                errors.append((gid, f"HTTP {r.status_code}: {r.text[:140]}"))
                print(f"[ERR] {gid}: HTTP {r.status_code} {r.text[:140]}")
        except Exception as e:
            errors.append((gid, str(e)))
            print(f"[ERR] {gid}: {e}")

    print(f"\nFirestore mis à jour : {ok}/{len(report['guests'])}" +
          ("  (public/billets copié)" if not args.no_copy else ""))
    if errors:
        print("Erreurs:", errors[:5])


if __name__ == "__main__":
    main()