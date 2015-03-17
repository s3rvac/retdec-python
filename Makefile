#
# Project:   retdec-python
# Copyright: (c) 2015 by Petr Zemek <s3rvac@gmail.com> and contributors
# License:   MIT, see the LICENSE file for more details
#
# A GNU Makefile for the project.
#

.PHONY: clean clean-pyc docs docs-coverage help lint tests tests-coverage tests-timings

help:
	@echo "Use \`make <target>', where <target> is one of the following:"
	@echo "  clean          - remove all generated files"
	@echo "  clean-pyc      - remove just Python file artifacts"
	@echo "  docs           - generate documentation"
	@echo "  docs-coverage  - generate documentation coverage"
	@echo "  lint           - check code style with flake8"
	@echo "  tests          - run tests"
	@echo "  tests-coverage - obtain test coverage"
	@echo "  tests-timings  - obtain test timings"

clean: clean-pyc
	@rm -rf .coverage coverage
	@$(MAKE) -C docs clean

clean-pyc:
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '*.py[co]' -exec rm -f {} +

docs:
	@sphinx-apidoc --force -o docs retdec
	@$(MAKE) -C docs html

docs-coverage:
	@$(MAKE) -C docs coverage

lint:
	@flake8 retdec tests

tests:
	@nosetests tests \
		--processes=-1

tests-coverage:
	@nosetests tests \
		--with-coverage \
		--cover-package retdec \
		--cover-erase \
		--cover-html \
		--cover-html-dir coverage

tests-timings:
	@nosetests tests \
		--with-timer \
		--timer-ok=10ms \
		--timer-warning=50ms
