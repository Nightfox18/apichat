# 📝 Шпаргалка команд

## Основные команды Docker

```bash
# Запуск (сборка + старт)
docker-compose up --build

# Запуск в фоне
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Остановка с удалением volumes (БД)
docker-compose down -v

# Перезапуск
docker-compose restart

# Пересборка
docker-compose build --no-cache
```

---

## Команды для работы с приложением

```bash
# Запуск тестов
docker-compose exec app pytest -v

# Тесты с покрытием
docker-compose exec app pytest --cov=app --cov-report=html

# Применить миграции
docker-compose exec app alembic upgrade head

# Откатить миграцию
docker-compose exec app alembic downgrade -1

# Создать новую миграцию
docker-compose exec app alembic revision --autogenerate -m "description"

# Python shell в контейнере
docker-compose exec app python

# Bash shell в контейнере
docker-compose exec app bash
```

---

## Команды для работы с БД

```bash
# Подключение к PostgreSQL
docker-compose exec db psql -U chatuser -d chatdb

# Список таблиц
docker-compose exec db psql -U chatuser -d chatdb -c "\dt"

# Просмотр данных
docker-compose exec db psql -U chatuser -d chatdb -c "SELECT * FROM chats;"
docker-compose exec db psql -U chatuser -d chatdb -c "SELECT * FROM messages;"

# Создание дампа БД
docker-compose exec db pg_dump -U chatuser chatdb > dump.sql

# Восстановление из дампа
docker-compose exec -T db psql -U chatuser chatdb < dump.sql
```

---

## Тестирование API (curl)

```bash
# Health check
curl http://localhost:8000/health

# Создать чат
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'

# Создать сообщение
curl -X POST http://localhost:8000/chats/1/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello!"}'

# Получить чат
curl http://localhost:8000/chats/1

# Получить чат с пагинацией
curl "http://localhost:8000/chats/1?limit=10&offset=0"

# Удалить чат
curl -X DELETE http://localhost:8000/chats/1
```

---

## Makefile команды (если используете)

```bash
# Показать справку
make help

# Собрать образы
make build

# Запустить сервисы
make up

# Остановить сервисы
make down

# Просмотр логов
make logs

# Запустить тесты
make test

# Тесты с покрытием
make test-cov

# Применить миграции
make migrate

# Создать миграцию
make migrate-create MESSAGE="description"

# Python shell
make shell

# PostgreSQL shell
make db-shell

# Очистка
make clean

# Перезапуск
make restart

# Пересборка и перезапуск
make rebuild
```

---

## Отладка

```bash
# Просмотр логов только приложения
docker-compose logs -f app

# Просмотр логов только БД
docker-compose logs -f db

# Проверка статуса контейнеров
docker-compose ps

# Информация о контейнере
docker-compose exec app env

# Проверка переменных окружения
docker-compose exec app printenv | grep DATABASE

# Проверка подключения к БД
docker-compose exec app python -c "from app.database import engine; import asyncio; asyncio.run(engine.connect())"
```

---

## Полезные SQL запросы

```sql
-- Подключиться к БД
\c chatdb

-- Список таблиц
\dt

-- Описание таблицы
\d chats
\d messages

-- Статистика
SELECT 
  (SELECT COUNT(*) FROM chats) as total_chats,
  (SELECT COUNT(*) FROM messages) as total_messages;

-- Топ 5 чатов с наибольшим количеством сообщений
SELECT 
  c.id, 
  c.title, 
  COUNT(m.id) as message_count
FROM chats c
LEFT JOIN messages m ON c.id = m.chat_id
GROUP BY c.id, c.title
ORDER BY message_count DESC
LIMIT 5;

-- Последние 10 сообщений
SELECT 
  m.id,
  c.title as chat_title,
  m.text,
  m.created_at
FROM messages m
JOIN chats c ON m.chat_id = c.id
ORDER BY m.created_at DESC
LIMIT 10;

-- Очистить все данные (осторожно!)
TRUNCATE TABLE messages, chats RESTART IDENTITY CASCADE;
```

---

## Локальная разработка (без Docker)

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Запустить PostgreSQL локально
# (или использовать docker-compose для только БД)
docker-compose up db

# Применить миграции
alembic upgrade head

# Запустить приложение
uvicorn app.main:app --reload

# Запустить тесты локально
pytest -v
```

---

## Быстрые проверки

```bash
# Проверка, что приложение отвечает
curl -f http://localhost:8000/health || echo "App не отвечает!"

# Проверка, что БД доступна
docker-compose exec db pg_isready -U chatuser

# Проверка версии Python в контейнере
docker-compose exec app python --version

# Проверка установленных пакетов
docker-compose exec app pip list

# Количество строк кода
find app -name "*.py" | xargs wc -l
```

---

## Очистка и сброс

```bash
# Полная очистка (контейнеры + volumes + образы)
docker-compose down -v --rmi all

# Удалить только volumes
docker-compose down -v

# Пересоздать БД с нуля
docker-compose down -v
docker-compose up --build

# Очистить кэш pytest
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +
```
