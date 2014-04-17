
PYVERSION ?= 3
export PYVERSION

.PHONY: test
test:
	@if [ ! -e env$$PYVERSION ]; then ./mkenv; fi
	@if [ ! -e env$$PYVERSION/bin/py.test ] || [ ! -e env$$PYVERSION/bin/coverage ]; then \
		./env$$PYVERSION/bin/pip install -r test-requirements.txt; \
	fi
	@./env$$PYVERSION/bin/py.test --doctest-glob='*.rst' --cov-report term --cov melba .

