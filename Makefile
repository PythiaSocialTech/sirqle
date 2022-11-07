.ONESHELL:

.PHONY: data, help, install
include .env
export

SHELL = /bin/zsh
BIN = .venv_dev/bin/


install: ## install dev venv
	@python3 -m venv .venv_dev
	@$(BIN)pip install -r requirements_dev.txt

startdb: ## start the database
	@surreal start --bind 127.0.0.1:9120 --log trace --user test --pass test memory > /dev/null 2>db_log.txt &
	@echo "SurrealDB started at 127.0.0.1:9120"

test: startdb ## run the test suite
	@echo "URL='http://127.0.0.1:9120'\nNAMESPACE='test'\nDATABASE='test'\nUSERNAME='test'\nPASSWORD='test'" > .db_conf
	@$(BIN)python -m pytest -svra
	@-pkill surreal
	@rm .db_conf

serve: ## serve docs for local dev
	@$(BIN)python -m mkdocs serve

killdb: ## stop the database
	@-pkill surreal
	@echo "SurrealDB Killed"

pcm: ## run precommit
	@$(BIN)pre-commit run

help:
	@awk -F ':|##' \
				'/^[^\t].+?:.*?##/ {\
					printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
				 }' $(MAKEFILE_LIST)
