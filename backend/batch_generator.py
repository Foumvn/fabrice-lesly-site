"""batch_generator.py — génération parallélisée du PDF de chaque invité."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pdf_generator import generate_invitation

MAX_WORKERS = 8  # génération PDF = CPU-bound court -> 6-8 threads suffisent


def _generate_guest_pdfs(guest: dict) -> dict:
    """Génère le PDF unique (3 pages) d'un invité."""
    pdf = generate_invitation(guest["name"], guest["table_name"], guest["id"])
    return {"guest_id": guest["id"], "pdf": pdf}


def generate_all(guests: list[dict]) -> dict:
    """Génère le PDF de tous les invités en parallèle."""
    results = []
    failed = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(_generate_guest_pdfs, g): g for g in guests}
        for future in as_completed(futures):
            guest = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                failed.append({"guest_id": guest["id"], "error": str(e)})

    return {"generated": results, "failed": failed, "total": len(guests), "success": len(results)}
