
.PHONY: test
test:
	@if [ ! -e env ]; then ./mkenv; fi
	@if [ ! -e env/bin/py.test ]; then ./env/bin/pip install pytest; fi
	@./env/bin/py.test melba

