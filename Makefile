MAKEFLAGS += --always-make

VERSION := $(shell python3 -c "from xkits.attribute import __version__; print(__version__)")

all: build reinstall test


clean-cover:
	rm -rf cover .coverage coverage.xml htmlcov
clean-tox:
	rm -rf .stestr .tox
clean: build-clean test-clean clean-cover clean-tox


upgrade-xpip-build:
	pip3 install -i https://pypi.org/simple --upgrade xpip-build
upgrade-xpip-upload:
	pip3 install -i https://pypi.org/simple --upgrade xpip-upload
upgrade-xpip: upgrade-xpip-build upgrade-xpip-upload
	pip3 install -i https://pypi.org/simple --upgrade xpip-mirror


upload:
	xpip-upload --config-file .pypirc dist/*


build-clean:
	xpip-build --debug setup --clean
build-requirements:
	pip3 install -r requirements.txt
build: build-clean build-requirements
	xpip-build --debug setup --all


install:
	pip3 install --force-reinstall --no-deps dist/*.whl
uninstall:
	pip3 uninstall -y xkits
reinstall: uninstall install


test-prepare:
	pip3 install --upgrade mock pylint flake8 pytest pytest-cov
pylint:
	pylint $(shell git ls-files xkits/*.py test/*.py example/*.py)
flake8:
	flake8 xkits --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 xkits --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
pytest:
	pytest --cov=xkits --cov-report=term-missing --cov-report=xml --cov-report=html --cov-config=.coveragerc --cov-fail-under=100
pytest-clean:
	rm -rf .pytest_cache
test: test-prepare pylint flake8 pytest
test-clean: pytest-clean

tag:
	git tag -a v${VERSION} -m "release v${VERSION}"
	git push origin --tags
