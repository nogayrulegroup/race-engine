.all:


.PYNOY: lint
lint:
	black --line-length 79 .

.PYNOY: clean
clean:
	rm -rf __pycache__ \
		dist
