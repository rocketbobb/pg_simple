project=pg_simple
envfile=config/local/${project}env

.PHONY: tests api venv clean initialize clean-pyc clean-env clean-tests docker-run docker-run-only docker-from-quay

${project}-env/bin/activate: requirements.txt
	test -d ${project}-env || virtualenv ${project}-env
	. ${project}-env/bin/activate; pip install -r requirements.txt
	touch ${project}-env/bin/activate

venv: ${project}-env/bin/activate

init-venv:
	pyinitenv ${project}

#initialize: venv
#	. ${project}-env/bin/activate; python ?? initialize --config=${config}

#api: venv
#	. ${project}-env/bin/activate; python ?? api

api-request:
	chmod +x tests/test_api.sh
	chmod +x ${envfile}.sh
	. ${envfile}.sh; ./tests/test_api.sh

test: venv
	. ${project}-env/bin/activate; python ??? test

	. ${project}-env/bin/activate; py.test

docker-run:
	docker build -t ${project} .

	docker run --env-file=${envfile} ${project}

docker-run-only:
	docker run --env-file=${envfile} ${project}

clean-tests:
	rm -rf .pytest_cache
	rm -r test/model/test/
	mkdir test/model/test
	touch test/model/test/.gitkeep

clean-env:
	rm -r ${project}-env

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	rm -rf .pytest_cache

clean: clean-tests clean-env clean-pyc