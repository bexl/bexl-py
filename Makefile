setup::
	@pipenv install --dev

lint::
	@pipenv run tidypy check

test::
	@pipenv run coverage run --rcfile=setup.cfg --module py.test
	@pipenv run coverage report --rcfile=setup.cfg

test-watch::
	@pipenv run ptw

clean::
	@rm -rf dist build .pytest_cache

build:: clean
	@pipenv run python setup.py sdist
	@pipenv run python setup.py bdist_wheel

publish::
	@pipenv run twine upload dist/*

