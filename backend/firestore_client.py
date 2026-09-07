"""
firestore_client.py — Lecture/écriture des invités dans Firebase Firestore.
Utilise firebase-admin (SDK serveur). Nécessite un fichier de clé de service
(serviceAccountKey.json) pour l'accès aux collections côté backend.

Si aucun fichier de credentials n'est présent, les fonctions lèvent une
exception claire (main.py bascule alors sur les données de démo).
"""
import os
import datetime
import firebase_admin
from firebase_admin import firestore

_BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # template/
_SERVICE_ACCOUNT = os.path.join(_BASE_DIR, "serviceAccountKey.json")


def _ensure_credentials():
    """Lève une exception si aucun credentials Firebase n'est disponible."""
    if not os.path.exists(_SERVICE_ACCOUNT):
        raise FileNotFoundError(
            "Fichier de credentials Firebase introuvable: "
            f"{_SERVICE_ACCOUNT}. Placez votre serviceAccountKey.json "
            "à la racine de template/ pour accéder à Firestore."
        )


def _get_app():
    if not firebase_admin._apps:
        _ensure_credentials()
        from firebase_admin import credentials
        cred = credentials.Certificate(_SERVICE_ACCOUNT)
        firebase_admin.initialize_app(cred)
    return list(firebase_admin._apps.values())[0]


def get_firestore():
    """Retourne le client Firestore (initialisé une seule fois)."""
    return firestore.client(_get_app())


def fetch_guests() -> list[dict]:
    """
    Récupère tous les invités depuis la collection Firestore 'guests'.
    Chaque document doit contenir au minimum:
        name, table_name, id (ou doc id), etc.
    """
    db = get_firestore()
    docs = db.collection("guests").stream()

    guests = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = data.get("id") or doc.id
        guests.append(data)

    return guests


def fetch_guest(guest_id: str) -> dict:
    """Récupère un invité par son id."""
    db = get_firestore()
    doc = db.collection("guests").document(guest_id).get()
    if not doc.exists:
        return None
    data = doc.to_dict()
    data["id"] = guest_id
    return data


def add_guest(guest: dict) -> str:
    """Ajoute un invité à Firestore. Retourne son doc id."""
    db = get_firestore()
    doc_ref = db.collection("guests").document()
    data = dict(guest)
    data["id"] = doc_ref.id
    doc_ref.set(data)
    return doc_ref.id


def update_guest(guest_id: str, updates: dict):
    """Met à jour les champs d'un invité."""
    db = get_firestore()
    db.collection("guests").document(guest_id).update(updates)


def mark_checkin(guest_id: str, checked_in_by: str = "scanner"):
    """Enregistre le check-in d'un invité."""
    db = get_firestore()
    db.collection("guests").document(guest_id).update({
        "checkedIn": True,
        "checkedInAt": datetime.datetime.utcnow().isoformat(),
        "checkedInBy": checked_in_by,
    })
