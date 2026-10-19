"""Team metadata and safe local profile images."""

from pathlib import Path
import json
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def members():
    return json.loads((ROOT / "data/team.json").read_text(encoding="utf-8"))["members"]


def profile_image(member):
    path = (ROOT / member["image"]).resolve()
    if not path.is_relative_to((ROOT / "assets/team").resolve()) or not path.is_file():
        return None
    try:
        with Image.open(path) as picture:
            if picture.width * picture.height > 20_000_000:
                return None
            picture.verify()
        return path
    except (OSError, ValueError, Image.DecompressionBombError):
        return None
