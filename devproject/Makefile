
# Re-install django-tornado
.PHONY: reset
reset:
	-yes y | pip uninstall --exists-action=w django-tornado
	pip install --exists-action=w --pre ../django_tornado/

.PHONY: run
run: reset
	cd dj; export DJANGO_DEBUG=''; ./manage.py collectstatic -l --noinput; ./manage.py run_tornado

.PHONY: rundbg
rundbg: reset
	cd dj; export DJANGO_DEBUG=True; ./manage.py run_tornado

