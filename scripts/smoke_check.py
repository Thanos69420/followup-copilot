import json
from pathlib import Path


def check_file(path: str):
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"Missing: {path}")


if __name__ == "__main__":
    must_exist = [
        "app/main.py",
        "Dockerfile",
        "alembic.ini",
        "render.yaml",
        "app/static/progress.html",
    ]
    for f in must_exist:
        check_file(f)

    print(json.dumps({"ok": True, "checked": must_exist}, indent=2))
