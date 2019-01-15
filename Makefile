all: run

clean:
	pipenv --rm && rm -rf *.egg-info && rm -rf dist && rm -rf *.log*

run:
	PIPENV_DONT_LOAD_ENV=1 pipenv run flask

requirements:
	pipenv lock -r > $(HOME)/python/ansible/roles/keeper/files/requirements.txt

install: requirements
	pipenv run sdist
