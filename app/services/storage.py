from __future__ import annotations
from pathlib import Path
import json
from typing import List
from app.models.schemas import Invoice

DATA_PATH = Path(__file__).resolve().parents[2] / "data"
INVOICES_FILE = DATA_PATH / "invoices.json"


def _ensure():
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    if not INVOICES_FILE.exists():
        INVOICES_FILE.write_text("[]", encoding="utf-8")


def save_invoices(invoices: List[Invoice]) -> None:
    _ensure()
    INVOICES_FILE.write_text(json.dumps([i.model_dump(mode="json") for i in invoices], indent=2), encoding="utf-8")


def load_invoices() -> List[Invoice]:
    _ensure()
    raw = json.loads(INVOICES_FILE.read_text(encoding="utf-8"))
    return [Invoice(**item) for item in raw]
