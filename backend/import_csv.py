"""
import_csv.py — Importe des invités depuis un CSV vers Firestore (ou fichier JSON démo).

Format attendu du CSV (colonnes) :
    table_name,table_subtitle,table_theme,guest_name
Exemple :
    Table Triomphe,Victoire,GLOIRE / ROYAL,Rostand Essima

Usage:
    python import_csv.py chemin/vers/fichier.csv [--json sortie.json]
"""
import argparse
import csv
import json
import os
import sys

_BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # template/


def parse_csv(path: str) -> list[dict]:
    """Lit un CSV et retourne une liste d'invités structurés."""
    guests = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("guest_name") or "").strip()
            table_name = (row.get("table_name") or "").strip()
            if not name or not table_name:
                continue
            subtitle = (row.get("table_subtitle") or "").strip()
            theme = (row.get("table_theme") or "").strip()
            full_table = f"{table_name}"
            if subtitle:
                full_table += f" - {subtitle}"
            guests.append({
                "name": name,
                "table_name": full_table,
                "tableId": table_name.lower().replace(" ", "-"),
                "theme": theme,
                "status": "pending",
                "checkedIn": False,
                "checkedInAt": None,
            })
    return guests


def import_to_firestore(guests: list[dict]) -> int:
    """Importe les invités dans Firestore. Retourne le nombre importé."""
    import firestore_client
    count = 0
    for g in guests:
        try:
            firestore_client.add_guest(g)
            count += 1
        except Exception as e:
            print(f"  !! Erreur import {g['name']}: {e}")
    return count


def main():
    parser = argparse.ArgumentParser(description="Import des invités depuis CSV")
    parser.add_argument("csv", help="Chemin vers le fichier CSV")
    parser.add_argument("--json", help="Optionnel: exporter les invités en JSON (pour démo)")
    parser.add_argument("--firestore", action="store_true", help="Importer dans Firestore")
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        print(f"Fichier introuvable: {args.csv}")
        sys.exit(1)

    guests = parse_csv(args.csv)
    print(f"[CSV] {len(guests)} invités lus depuis {args.csv}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(guests, f, ensure_ascii=False, indent=2)
        print(f"[JSON] Exporté vers {args.json}")

    if args.firestore:
        count = import_to_firestore(guests)
        print(f"[FIRESTORE] {count} invités importés dans Firestore")
    else:
        print("[INFO] Utilisez --firestore pour importer dans Firestore")


if __name__ == "__main__":
    main()
