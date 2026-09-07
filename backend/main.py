"""
main.py — API FastAPI pour la génération des billets de mariage.
Endpoints:
  GET  /health                -> vérification santé
  GET  /guests                -> liste des invités (démo ou Firestore)
  POST /generate/{guestId}    -> génère + upload PDF1 & PDF2 d'un invité
  POST /generate-all          -> génère + upload pour tous les invités
"""
import io
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from font_manager import register_all_fonts
from batch_generator import generate_all, _generate_guest_pdfs
from cloudinary_upload import upload_invitation
import firestore_client

# --- Données de démo (utilisées SI Firestore n'est pas configuré) ---
DEMO_GUESTS = [
    {"id": "demo-001", "name": "Rostand Essima", "table_name": "Table Triomphe - Victoire"},
    {"id": "demo-002", "name": "Francklin Messomo", "table_name": "Table Triomphe - Victoire"},
    {"id": "demo-003", "name": "Freddy Ngono", "table_name": "Table Triomphe - Victoire"},
    {"id": "demo-004", "name": "Latifah Edjimbi", "table_name": "Table Triomphe - Victoire"},
    {"id": "demo-011", "name": "Gisèle Akono", "table_name": "Table Leader"},
    {"id": "demo-012", "name": "Andrea Song", "table_name": "Table Leader"},
]

app = FastAPI(title="Billetterie Mariage - Backend", version="1.0.0")


@app.on_event("startup")
def startup():
    """Enregistre + subset les polices une seule fois au démarrage."""
    register_all_fonts()


def _get_guests() -> list[dict]:
    """Retourne les invités depuis Firestore, ou la liste démo si indisponible."""
    try:
        guests = firestore_client.fetch_guests()
        if guests:
            return guests
    except Exception as e:
        print(f"[MAIN] Firestore indisponible, utilisation des données démo: {e}")
    return DEMO_GUESTS


@app.get("/health")
def health():
    """Vérification de santé de l'API."""
    return {"status": "ok", "service": "billetterie-mariage", "version": "1.0.0"}


@app.get("/guests")
def guests():
    """Liste des invités."""
    return {"guests": _get_guests(), "count": len(_get_guests())}


@app.post("/generate/{guest_id}")
def generate_one(guest_id: str, upload: bool = True):
    """Génère le PDF (3 pages) d'un invité précis."""
    guests = _get_guests()
    guest = next((g for g in guests if g["id"] == guest_id), None)
    if not guest:
        return {"error": f"Invite introuvable: {guest_id}"}

    result = _generate_guest_pdfs(guest)

    urls = {}
    if upload:
        urls["pdfUrl"] = upload_invitation(result["pdf"], guest_id)
        try:
            firestore_client.update_guest(guest_id, {
                **urls,
                "status": "generated",
            })
        except Exception:
            pass  # Firestore pas disponible -> on ignore

    return {
        "guest_id": guest_id,
        **urls,
        "pdf_size": len(result["pdf"]),
    }


@app.post("/generate-all")
def generate_all_endpoint(upload: bool = True):
    """Génère + upload le PDF de tous les invités (parallélisé)."""
    guests = _get_guests()
    report = generate_all(guests)

    uploaded = 0
    uploaded_guests = []
    for r in report["generated"]:
        try:
            if upload:
                gid = r["guest_id"]
                url = upload_invitation(r["pdf"], gid)
                uploaded_guests.append({"guest_id": gid, "pdfUrl": url})
                uploaded += 1
        except Exception as e:
            report["failed"].append({"guest_id": r["guest_id"], "error": f"upload: {e}"})

    return {
        "status": "done",
        "total": report["total"],
        "generated": report["success"],
        "uploaded": uploaded,
        "failed": report["failed"],
        "uploaded_guests": uploaded_guests,
    }


@app.post("/import")
def import_guests_endpoint(guests: list[dict]):
    """
    Importe une liste d'invités (JSON). Chaque invité:
        { name, table_name, tableId?, theme?, seatNumber? }
    Retourne le nombre d'invités importés.
    """
    imported = 0
    for g in guests:
        g["status"] = "pending"
        g["checkedIn"] = False
        g["checkedInAt"] = None
        try:
            firestore_client.add_guest(g)
            imported += 1
        except Exception as e:
            print(f"[IMPORT] Erreur {g.get('name')}: {e}")
    return {"status": "done", "imported": imported, "total": len(guests)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
