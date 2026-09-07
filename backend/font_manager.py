"""
Gère l'enregistrement des polices custom dans ReportLab
et leur optimisation (subsetting) pour réduire le poids des PDFs.
"""
import os
from functools import lru_cache
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from fontTools import subset

FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
SUBSET_DIR = os.path.join(FONTS_DIR, "subset")
os.makedirs(SUBSET_DIR, exist_ok=True)

# Caractères réellement utilisés dans les PDFs (noms, tables, dates, FCFA/€ etc.)
CHARSET_UTILE = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789 .,'’-|:éèêëàâäùûüôöîïçÉÈÊËÀÂÄÙÛÜÔÖÎÏÇ"
    "()[]-—.!?/  &%@€$£"
)

WEIGHT_NAME_MAP = {
    "regular": "",
    "bold": "-Bold",
    "italic": "-Italic",
    "light": "-Light",
    "light_italic": "-LightItalic",
}

FONT_REGISTRY = {
    "AmsterdamFour": {
        "regular": "Amsterdam-Four.ttf",
    },
    "Montserrat": {
        "regular": "Montserrat-Regular.ttf",
        "bold": "Montserrat-Bold.ttf",
    },
    "CormorantGaramond": {
        "regular": "CormorantGaramond-Regular.ttf",
        "italic": "CormorantGaramond-Italic.ttf",
    },
    "Inter": {
        "regular": "Inter-Regular.ttf",
        "bold": "Inter-Bold.ttf",
        "light": "Inter-Light.ttf",
        "light_italic": "Inter-LightItalic.ttf",
    },
}


def _subset_font(src_path: str, dst_path: str, charset: str) -> str:
    """Réduit une police TTF aux seuls glyphes utilisés -> fichier bien plus léger."""
    if os.path.exists(dst_path):
        return dst_path

    options = subset.Options()
    options.layout_features = ["*"]  # garde kerning/ligatures
    options.desubroutinize = True
    options.name_IDs = ["*"]
    options.notdef_outline = True
    options.recommended_glyphs = True

    font = subset.load_font(src_path, options)
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(text=charset)
    subsetter.subset(font)
    subset.save_font(font, dst_path, options)
    return dst_path


@lru_cache(maxsize=1)
def register_all_fonts() -> None:
    """
    À appeler UNE SEULE FOIS au démarrage de FastAPI (event 'startup').
    Enregistre les versions subsettées des polices dans ReportLab.
    """
    print("[FONTS] Enregistrement des polices...")
    for family, variants in FONT_REGISTRY.items():
        for weight, filename in variants.items():
            src = os.path.join(FONTS_DIR, filename)
            if not os.path.exists(src):
                print(f"[FONTS] !! Polices manquante: {src}")
                continue
            dst = os.path.join(SUBSET_DIR, filename)
            _subset_font(src, dst, CHARSET_UTILE)

            font_name = f"{family}{WEIGHT_NAME_MAP[weight]}"
            try:
                pdfmetrics.registerFont(TTFont(font_name, dst))
                print(f"[FONTS] Enregistré: {font_name}")
            except Exception as e:
                print(f"[FONTS] !! Erreur enregistrement {font_name}: {e}")

        # Mappe bold/italic pour que ReportLab résolve <b> automatiquement
        if "bold" in variants and "regular" in variants:
            try:
                pdfmetrics.registerFontFamily(
                    family,
                    normal=family,
                    bold=f"{family}-Bold",
                    italic=f"{family}-Italic",
                )
            except Exception as e:
                print(f"[FONTS] !! Erreur registerFontFamily {family}: {e}")
    print("[FONTS] Polices enregistrées.")


if __name__ == "__main__":
    register_all_fonts()
