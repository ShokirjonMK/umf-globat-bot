ifneq (,$(wildcard ./.env))
	include .env
	export
	ENV_FILE_PARAM = --env-file .envs
endif


build:
	sudo docker-compose -f local.yml up -d --build --remove-orphans

up:
	sudo docker-compose -f local.yml up

down:
	sudo docker-compose -f local.yml down

down-v:
	sudo docker-compose -f local.yml down -v

logs:
	sudo docker-compose -f local.yml logs $(service)

migrations:
	sudo docker-compose -f local.yml run --rm django_app python manage.py makemigrations

migrate:
	sudo docker-compose -f local.yml run --rm django_app python manage.py migrate --no-input

superuser:
	sudo docker-compose -f local.yml run --rm django_app python manage.py createsuperuser

shell:
	sudo docker-compose -f local.yml run --rm django_app python manage.py shell_plus

backup:
	sudo docker-compose -f local.yml exec postgres backup

restore:
	sudo docker-compose -f local.yml exec postgres restore 

stop:
	sudo docker-compose -f local.yml stop
