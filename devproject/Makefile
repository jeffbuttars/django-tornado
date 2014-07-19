
# SERVER_IP = localhost:8000
SERVER_IP = 172.18.61.66:8000
# Re-install django-tornado
.PHONY: reset
reset:
	-yes y | pip uninstall --exists-action=w django-tornado
	pip install --exists-action=w --pre --no-deps ../src/

.PHONY: run
run: reset
	cd dj; export DJANGO_DEBUG=''; ./manage.py collectstatic -l --noinput; ./manage.py run_tornado

.PHONY: rundbg
rundbg: reset
	cd dj; export DJANGO_DEBUG=True; ./manage.py run_tornado $(SERVER_IP)
