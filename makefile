
.PHONY: test
test:
	@if [ ! -e env ]; then ./mkenv; fi
	@if [ ! -e env/bin/py.test ] || [ ! -e env/bin/coverage ]; then \
		./env/bin/pip install -r test-requirements.txt; \
	fi
	@./env/bin/py.test --cov-report term --cov melba melba/tests

