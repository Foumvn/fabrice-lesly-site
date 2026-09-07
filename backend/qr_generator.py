"""Génère un QR code personnalisé avec l'image anneaux.png superposée."""
import io
import os
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
RINGS_IMAGE_PATH = os.path.join(TEMPLATES_DIR, "anneaux.png")


def generate_qr_with_rings(content: str, box_size: int = 10) -> Image.Image:
    """
    content: ex. "ROSTAND ESSIMA|TABLE TRIOMPHE|ID-001"
    Utilise ERROR_CORRECT_H (30% de correction) car l'image des anneaux
    va masquer une partie du QR code au centre.
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=2,
    )
    qr.add_data(content)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

    if os.path.exists(RINGS_IMAGE_PATH):
        rings = Image.open(RINGS_IMAGE_PATH).convert("RGBA")
        ring_size = int(qr_img.size[0] * 0.22)  # ~22% du QR, pour rester scannable
        rings = rings.resize((ring_size, ring_size), Image.LANCZOS)

        pos = (
            (qr_img.size[0] - ring_size) // 2,
            (qr_img.size[1] - ring_size) // 2,
        )
        qr_img.paste(rings, pos, rings)  # masque alpha = fond transparent respecté
    else:
        print(f"[QR] !! anneaux.png introuvable: {RINGS_IMAGE_PATH}")

    return qr_img


def generate_qr_bytes(content: str, box_size: int = 10) -> bytes:
    """Retourne le QR code (avec anneaux) en PNG bytes."""
    img = generate_qr_with_rings(content, box_size)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


if __name__ == "__main__":
    # Test rapide
    img = generate_qr_with_rings("TEST|TABLE TRIOMPHE|ID-001")
    img.save(os.path.join(os.path.dirname(__file__), "test-qr.png"))
    print("[QR] Test d'image généré: test-qr.png", img.size)
