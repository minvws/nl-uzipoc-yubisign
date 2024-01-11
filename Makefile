venv: .venv/make_venv_complete ## Create virtual environment
.venv/make_venv_complete:
	python3 -m venv .venv
	. .venv/bin/activate && ${env} pip install -U pip
	. .venv/bin/activate && ${env} pip install -U pip-tools
	. .venv/bin/activate && ${env} pip install -Ur requirements.txt
	touch .venv/make_venv_complete

pip-compile: ## synchronizes the .venv with the state of requirements.txt
	. .venv/bin/activate && ${env} python3 -m piptools compile requirements.in

pip-sync: ## synchronizes the .venv with the state of requirements.txt
	. .venv/bin/activate && ${env} python3 -m piptools sync requirements.txt
run:
	. .venv/bin/activate && ${env} python3 -m app.wizard

lint: venv  ## Do basic linting
	@. .venv/bin/activate && ${env} python3 -m pylint app
	@. .venv/bin/activate && ${env} python3 -m black --check app

check-types: venv ## Check for type issues with mypy
	@. .venv/bin/activate && ${env} python3 -m mypy --check app tests

fix:
	@. .venv/bin/activate && ${env} python3 -m black app 
