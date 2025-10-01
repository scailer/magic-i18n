SHELL := /bin/bash

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf *.log
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .cache
	rm -rf .eggs/
	rm -rf .pytest_cache/
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
