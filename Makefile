# SPDX-License-Identifier: MIT
PY ?= python3

.PHONY: check gen validate privacy test status
check: validate privacy test
	$(PY) tools/gen.py --check
validate:
	$(PY) tools/validate.py
privacy:
	$(PY) tools/privacy_scan.py
test:
	$(PY) -m pytest -q tests
gen:
	$(PY) tools/gen.py
status:
	$(PY) tools/pr_status.py
