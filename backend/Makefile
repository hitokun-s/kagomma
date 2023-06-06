
PYLINT_SCORE_THRESHOLD := 9.0
PYTEST_COVERAGE_THRESHOLD := 85

.PHONY: format
format:
	poetry run isort *.py --profile black
	poetry run black *.py

.PHONY: format_ci
format_ci:
	poetry run isort *.py --profile black --check-only
	poetry run black *.py --check

.PHONY: lint
lint:
	poetry run pylint --fail-under=$(PYLINT_SCORE_THRESHOLD) *.py

.PHONY: check_type
check_type:
	poetry run mypy *.py


.PHONY: test
test:
	#poetry run pytest tests/ --cov=./ --cov-branch --cov-report=html --cov-fail-under=$(PYTEST_COVERAGE_THRESHOLD)
	poetry run pytest tests


