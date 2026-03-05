.PHONY: run test lint smoke

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

smoke:
	python3 scripts/smoke_check.py

test:
	python3 -m py_compile app/main.py app/db.py app/core/config.py app/core/security.py app/services/*.py app/workers/*.py

lint:
	@echo "lint placeholder"
