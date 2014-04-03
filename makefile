
.PHONY: test
test:
	@if [ ! -e env ]; then ./mkenv; fi
	@if [ ! -e env/bin/py.test ]; then \
		./env/bin/pip install -U pytest; \
		./env/bin/pip install -U pytest-cov; \
	fi
	@./env/bin/py.test --cov-report term --cov melba melba/tests

