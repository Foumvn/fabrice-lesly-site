"""
upload_batch.py — Upload vers Cloudinary du PDF de chaque invité.

Chaque invité a son dossier Cloudinary  billets/<Nom de l'invité>/
contenant son unique invitation.pdf (3 pages).

Écrit :  Billet/urls-cloudinary.json

Usage :
    python upload_batch.py --dry-run   # ne fait rien, affiche ce qui serait envoyé
    python upload_batch.py --clean     # supprime les anciennes ressources guest-* / demo
    python upload_batch.py             # upload complet
"""
import argparse
import json
import os

from dotenv import load_dotenv

import cloudinary
import cloudinary.api
import cloudinary.uploader

from pdf_generator import PDF_FILENAME

_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_ROOT = os.path.dirname(_HERE)
DOTENV = os.path.join(_TEMPLATE_ROOT, ".env.local")
REPORT = os.path.join(_TEMPLATE_ROOT, "Billet", "rapport-complet.json")
OUT_JSON = os.path.join(_TEMPLATE_ROOT, "Billet", "urls-cloudinary.json")

RESOURCE_TYPE = "raw"


def cloudinary_config():
    load_dotenv(DOTENV)
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    )


def upload_one(path: str, folder: str, public_id: str) -> dict:
    with open(path, "rb") as f:
        res = cloudinary.uploader.upload(
            f,
            resource_type=RESOURCE_TYPE,
            folder=folder,
            public_id=public_id,
            overwrite=True,
            format="pdf",
        )
    return {
        "public_id": res["public_id"],
        "secure_url": res["secure_url"],
        "bytes": res.get("bytes"),
    }


def clean_old():
    """Supprime les anciennes ressources (ancien schéma et tests)."""
    for prefix in ["billets/invitations/", "billets/billets/"]:
        try:
            cloudinary.api.delete_resources_by_prefix(
                prefix, resource_type=RESOURCE_TYPE, type="upload"
            )
            print(f"[CLEAN] supprimé prefixe {prefix}")
        except Exception as e:
            print(f"[CLEAN] !! {prefix}: {e}")
    ids = ["sanity-check", "test-image-type-pdf"]
    cloudinary.api.delete_resources(
        ids, resource_type="image", type="upload"
    )
    print("[CLEAN] tests image supprimés")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    cloudinary_config()
    report = json.load(open(REPORT, encoding="utf-8"))

    if args.clean:
        clean_old()

    rows = []
    public_id = PDF_FILENAME.rsplit(".", 1)[0]
    for g in report["guests"]:
        folder = f"billets/{g['folder']}"
        entry = {
            "guest_id": g["guest_id"],
            "name": g["name"],
            "folder": folder,
            "path": g["path"],
            "cloudinary": {},
        }
        if args.dry_run:
            print(f"[DRY] {folder} : {g['path']}")
        else:
            try:
                entry["cloudinary"] = upload_one(g["path"], folder, public_id)
                print(f"[OK] {entry['guest_id']} -> {entry['cloudinary']['secure_url']}")
            except Exception as e:
                entry["cloudinary"] = {"error": str(e)}
                print(f"[ERR] {entry['guest_id']}: {e}")
        rows.append(entry)

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"\nTerminé : {len(rows)} invités -> {OUT_JSON}")


if __name__ == "__main__":
    main()