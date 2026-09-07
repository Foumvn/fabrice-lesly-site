"""
push_firestore.py — Importe les invités + URLs des PDFs dans Firestore
VIA les routes Next.js (firebase/web SDK) : POST /api/guests (avec id) puis
PUT /api/guests/{id} pour les URLs Cloudinary.

Prérequis : le serveur Next doit tourner (npm run dev).
            template/.env.local doit contenir NEXT_PUBLIC_FIREBASE_*.

Usage :
    python push_firestore.py                          # importe les 40 invités (sans URL)
    python push_firestore.py --urls <json>            # importe + écrit pdfUrl
"""
import argparse
import json
import os
import sys

import requests

from import_csv import parse_csv

_HERE = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_ROOT = os.path.dirname(_HERE)
DATA_CSV = os.path.join(_HERE, "data", "invites.csv")
DEFAULT_URLS = os.path.join(_TEMPLATE_ROOT, "Billet", "urls-cloudinary.json")

NEXT_BASE = os.environ.get("PUBLIC_BASE_URL", "http://localhost:3000").rstrip("/")


def load_cloud_urls(path: str) -> dict:
    """
    Extrait {guest_id: url_cloudinary} depuis urls-cloudinary.json.

    Tolère les deux formes rencontrées : la liste écrite par upload_batch.py
    et l'ancien objet {"uploaded": [...]}.
    """
    raw = json.load(open(path, encoding="utf-8"))
    rows = raw["uploaded"] if isinstance(raw, dict) else raw

    urls = {}
    for row in rows:
        gid = row.get("guest_id")
        cloud = row.get("cloudinary") or {}
        url = cloud.get("secure_url") or row.get("pdfUrl")
        if gid and url:
            urls[gid] = url
    return urls


def guest_payload(g: dict, urls: dict | None) -> dict:
    table = g["table_name"]
    theme = g.get("theme") or ""
    gid = g["id"]
    payload = {
        "id": gid,
        "name": g["name"],
        "tableName": table,
        "theme": theme,
        "status": "pending",
        "checkedIn": False,
        "checkedInAt": None,
        "qrData": f"{g['name'].upper()}|{table.upper()}|{gid}",
    }
    if urls and gid in urls:
        payload["pdfUrl"] = urls[gid]
        payload["status"] = "uploaded"
    return payload


def _clear_guests():
    """Vide la collection guests via l'API Next.js."""
    try:
        r = requests.get(f"{NEXT_BASE}/api/guests", timeout=20)
        if r.status_code != 200:
            print(f"[WARN] Impossible de lister les invités: HTTP {r.status_code}")
            return
        for g in r.json().get("guests", []):
            gid = g.get("id")
            if not gid:
                continue
            d = requests.delete(f"{NEXT_BASE}/api/guests/{gid}", timeout=20)
            if d.status_code == 200:
                print(f"[DEL] {gid}")
            else:
                print(f"[WARN] échec suppression {gid}: HTTP {d.status_code}")
    except Exception as e:
        print(f"[WARN] Erreur nettoyage: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="?", const=DEFAULT_URLS,
                        help="Fichier urls-cloudinary.json optionnel")
    parser.add_argument("--rebuild", action="store_true",
                        help="Vide d'abord la collection guests, puis réimporte")
    args = parser.parse_args()

    urls = None
    if args.urls:
        if not os.path.exists(args.urls):
            print("Fichier URLs introuvable:", args.urls)
            sys.exit(1)
        urls = load_cloud_urls(args.urls)
        print(f"[INFO] URLs Cloudinary chargées pour {len(urls)} invités")

    guests = parse_csv(DATA_CSV)
    for i, g in enumerate(guests, 1):
        g["id"] = f"guest-{i:03d}"

    if args.rebuild:
        print("[INFO] Rebuild demandé : nettoyage de la collection guests")
        _clear_guests()

    ok, err = 0, []
    for g in guests:
        payload = guest_payload(g, urls)
        try:
            r = requests.post(f"{NEXT_BASE}/api/guests", json=payload, timeout=20)
            if r.status_code == 201:
                ok += 1
                print(f"[OK] {g['id']} {g['name']} "
                      f"{'(+ url)' if payload.get('pdfUrl') else ''}")
            else:
                err.append((g["id"], g["name"], f"HTTP {r.status_code}: {r.text[:120]}"))
                print(f"[ERR] {g['id']} {g['name']}: HTTP {r.status_code} {r.text[:120]}")
        except Exception as e:
            err.append((g["id"], g["name"], str(e)))
            print(f"[ERR] {g['id']} {g['name']}: {e}")

    print(f"\nImportés : {ok}/{len(guests)} dans Firestore (via {NEXT_BASE})")
    if err:
        print("Erreurs:", err[:10])


if __name__ == "__main__":
    main()