.PHONY: run up down build logs restart shell migrate makemigrations createsuperuser collectstatic db-shell db-reset test

# Запустить приложение (фронт + бэк + БД)
run:
	docker-compose -f docker-compose.dev.yml up

# Запустить в фоновом режиме
up:
	docker-compose -f docker-compose.dev.yml up -d

# Остановить приложение
down:
	docker-compose -f docker-compose.dev.yml down

# Остановить и удалить все данные (включая БД)
down-volumes:
	docker-compose -f docker-compose.dev.yml down -v

# Пересобрать образы и запустить
build:
	docker-compose -f docker-compose.dev.yml up --build

# Просмотр логов
logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Перезапустить приложение
restart:
	docker-compose -f docker-compose.dev.yml restart

# Войти в shell Django
shell:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py shell

sh:
	docker-compose -f docker-compose.dev.yml exec backend sh
# Применить миграции
migrate:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py migrate

# Создать миграции
makemigrations:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py makemigrations

# Создать суперпользователя
createsuperuser:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser

# Собрать статические файлы
collectstatic:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py collectstatic --noinput

# Войти в PostgreSQL shell
db-shell:
	docker-compose -f docker-compose.dev.yml exec db psql -U postgres -d alfa

# Сбросить базу данных (удалить все данные)
db-reset:
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose -f docker-compose.dev.yml up -d db
	@echo "Ожидание запуска БД..."
	@sleep 5
	docker-compose -f docker-compose.dev.yml up -d backend

# Запустить тесты
test:
	docker-compose -f docker-compose.dev.yml exec backend python manage.py test -v 2

