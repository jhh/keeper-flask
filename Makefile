PGDUMP=/usr/pgsql-11/bin/pg_dump
PGDUMP_OPTS=--clean --create --no-owner --no-password
DB=keeper
SQLFILE := $(shell mktemp /tmp/keeper.XXXXX).sql

all: run

clean:
	pipenv --rm && rm -rf *.egg-info && rm -rf dist && rm -rf *.log*

run:
	@echo "running debug server at http://127.0.0.1:8050/"
	@pipenv run dash

requirements:
	pipenv lock -r > $(HOME)/python/ansible/roles/keeper/files/requirements.txt

install: requirements
	pipenv run sdist

dump-db:
	ssh hub \
	"$(PGDUMP) $(PGDUMP_OPTS) $(DB) > $(SQLFILE)"
	echo $(SQLFILE)

copy-db: dump-db
	scp -C hub:$(SQLFILE) .

init-db: copy-db
	psql < $(shell basename $(SQLFILE)) && rm $(shell basename $(SQLFILE))

