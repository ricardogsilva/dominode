
build:
	@docker-compose build

up:
	@docker-compose up -d

down:
	@docker-compose down

printenv:
	@docker inspect dominode_django_1 | jq '.[0].Config.Env | join("\n")' -r

runserver:
	@docker-compose exec django manage.py runserver 0.0.0.0:6001

logs:
	@docker-compose logs -f $(or ${SERVICE},django)

shell:
	@docker-compose exec $(or ${SERVICE},django) /bin/sh

collectstatic:
	@docker-compose exec django ./manage.py collectstatic --noinput
