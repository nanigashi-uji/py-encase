PYTHON     ?= python3
PIP        ?= pip3

TEMPLATE_DATA_SUBDIR = src/share/py-encase/template

all: $(TEMPLATE_DATA_SUBDIR)/py_encase_template.py README.rst README.ja.rst sdist bdist_wheel

README.rst: README.md
	pandoc --from markdown --to rst $^ -o $@

README.ja.rst: README.ja.md
	pandoc --from markdown --to rst $^ -o $@

$(TEMPLATE_DATA_SUBDIR)/py_encase_template.py: src/py_encase/py_encase.py 
	mkdir -p $(TEMPLATE_DATA_SUBDIR)
	$(PYTHON) $^ --manage dump_template --output $@

clean: 
	rm -rf src/py_encase.egg-info dist/* build/* *~ test/*~ src/py_encase/*~ src/py_encase/__pycache__ $(TEMPLATE_DATA_SUBDIR)/*~

distclean: clean
	rm -rf py_encase.egg-info dist build README.rst README.ja.rst $(TEMPLATE_DATA_SUBDIR)/py_encase_template.py

sdist: README.rst README.ja.rst 
	$(PYTHON) setup.py $@

bdist_wheel: README.rst README.ja.rst
	$(PYTHON) setup.py $@

test_upload: sdist bdist_wheel
	twine upload --verbose --repository testpypi dist/*

upload: sdist bdist_wheel
	twine upload --verbose dist/*
