"""cloudinary_upload.py — Upload des PDFs vers Cloudinary."""
import io
import os
import cloudinary
import cloudinary.api
import cloudinary.uploader
from dotenv import load_dotenv

# Charge les variables d'env depuis le .env local (situé au niveau parent du template)
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # template/
_ENV_PATH = os.path.join(_BASE_DIR, ".env.local")
if os.path.exists(_ENV_PATH):
    load_dotenv(_ENV_PATH)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def upload_pdf(pdf_bytes: bytes, public_id: str, folder: str = "billets") -> str:
    """
    Upload un PDF (bytes) vers Cloudinary et retourne l'URL sécurisée.
    pdf_bytes: contenu binaire du PDF
    public_id: identifiant unique (ex. "guest-001-invitation")
    """
    upload_result = cloudinary.uploader.upload(
        io.BytesIO(pdf_bytes),
        resource_type="raw",
        public_id=public_id,
        folder=folder,
        format="pdf",
        overwrite=True,
    )
    return upload_result["secure_url"]


CLOUD_FOLDER = "billets/invitations"


def upload_invitation(pdf_bytes: bytes, guest_id: str) -> str:
    """Upload le PDF de l'invité (3 pages) et retourne l'URL."""
    return upload_pdf(pdf_bytes, f"{guest_id}-invitation", folder=CLOUD_FOLDER)


if __name__ == "__main__":
    # Test upload (fichier PDF minimal)
    minimal_pdf = io.BytesIO()
    from reportlab.pdfgen import canvas as rl_canvas
    c = rl_canvas.Canvas(minimal_pdf)
    c.drawString(100, 750, "Test upload Cloudinary")
    c.save()
    minimal_pdf.seek(0)

    url = upload_pdf(minimal_pdf.getvalue(), "test-upload", folder="tests")
    print("[CLOUDINARY] Uploadé:", url)
