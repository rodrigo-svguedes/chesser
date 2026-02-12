
test:
	pytest tests -v --cov=chesser

create-env:
	python3 -m venv env

install:
	. env/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.text && \
	pip install -r requirements-dev.text

clean:
	@find . -name '*.py[cod]' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

run:
	. env/bin/activate && \
	flask --app chesser/app.py --debug run