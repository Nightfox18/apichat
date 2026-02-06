# 🚀 Quick Start Guide

## Минимальная инструкция для запуска проекта

### 1. Запуск приложения (один шаг)

```bash
docker-compose up --build
```

Готово! API доступен по адресу: http://localhost:8000

### 2. Интерактивная документация

Откройте в браузере: http://localhost:8000/docs

Здесь можно протестировать все endpoints через Swagger UI.

### 3. Быстрое тестирование через curl

```bash
# Health check
curl http://localhost:8000/health

# Создать чат
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'

# Создать сообщение (замените 1 на ID чата)
curl -X POST http://localhost:8000/chats/1/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, World!"}'

# Получить чат с сообщениями
curl http://localhost:8000/chats/1

# Удалить чат
curl -X DELETE http://localhost:8000/chats/1
```

### 4. Запуск тестов

```bash
docker-compose exec app pytest -v
```

### 5. Остановка

```bash
docker-compose down
```

---

## Что реализовано

✅ FastAPI + PostgreSQL + SQLAlchemy 2.0 (async)  
✅ Все 4 endpoint'а из ТЗ  
✅ Валидация с trimming пробелов  
✅ Каскадное удаление (ON DELETE CASCADE)  
✅ Пагинация (limit + offset)  
✅ Сортировка сообщений DESC  
✅ Миграции Alembic  
✅ Docker + docker-compose  
✅ Тесты (pytest): 30+ тестов, покрытие всех endpoints и edge-cases  
✅ Логирование  
✅ Типизация  
✅ Модульная архитектура  

Полная документация: [README.md](README.md)
