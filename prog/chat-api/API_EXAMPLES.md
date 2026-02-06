# API Examples

Примеры запросов к Chat API для тестирования с помощью curl или HTTPie.

## Prerequisites

Убедитесь, что приложение запущено:
```bash
docker-compose up
```

API доступен по адресу: http://localhost:8000

---

## 1. Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "service": "chat-api"
}
```

---

## 2. Создать чат

```bash
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "General Discussion"}'
```

**Ожидаемый ответ (201):**
```json
{
  "id": 1,
  "title": "General Discussion",
  "created_at": "2026-02-04T10:30:00.123456Z"
}
```

---

## 3. Создать сообщение

```bash
# Замените {chat_id} на ID созданного чата
curl -X POST http://localhost:8000/chats/1/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, this is my first message!"}'
```

**Ожидаемый ответ (201):**
```json
{
  "id": 1,
  "chat_id": 1,
  "text": "Hello, this is my first message!",
  "created_at": "2026-02-04T10:31:00.123456Z"
}
```

---

## 4. Получить чат с сообщениями

```bash
# Без параметров (по умолчанию limit=20, offset=0)
curl http://localhost:8000/chats/1

# С пагинацией
curl "http://localhost:8000/chats/1?limit=10&offset=0"
```

**Ожидаемый ответ (200):**
```json
{
  "id": 1,
  "title": "General Discussion",
  "created_at": "2026-02-04T10:30:00.123456Z",
  "messages": [
    {
      "id": 1,
      "chat_id": 1,
      "text": "Hello, this is my first message!",
      "created_at": "2026-02-04T10:31:00.123456Z"
    }
  ]
}
```

---

## 5. Удалить чат

```bash
curl -X DELETE http://localhost:8000/chats/1
```

**Ожидаемый ответ (204):**
```
No Content (пустое тело ответа)
```

---

## Тестовые сценарии

### Сценарий 1: Создание чата с несколькими сообщениями

```bash
# 1. Создаём чат
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Project Planning"}')

CHAT_ID=$(echo $CHAT_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

# 2. Создаём несколько сообщений
curl -X POST http://localhost:8000/chats/$CHAT_ID/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Lets discuss the roadmap"}'

curl -X POST http://localhost:8000/chats/$CHAT_ID/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Q1 priorities: API development"}'

curl -X POST http://localhost:8000/chats/$CHAT_ID/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Q2 priorities: Testing and deployment"}'

# 3. Получаем чат со всеми сообщениями
curl http://localhost:8000/chats/$CHAT_ID
```

---

### Сценарий 2: Тестирование валидации

```bash
# Пустой title (должен вернуть 422)
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'

# Title только из пробелов (должен вернуть 422)
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "   "}'

# Слишком длинный title (201 символ, должен вернуть 422)
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "'"$(printf 'a%.0s' {1..201})"'"}'

# Сообщение в несуществующий чат (должен вернуть 404)
curl -X POST http://localhost:8000/chats/99999/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "This should fail"}'
```

---

### Сценарий 3: Тестирование trimming

```bash
# Title с пробелами по краям (должны обрезаться)
curl -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "   Trimmed Title   "}'
# Ожидается: "title": "Trimmed Title"

# Text с пробелами (должны обрезаться)
curl -X POST http://localhost:8000/chats/1/messages/ \
  -H "Content-Type: application/json" \
  -d '{"text": "   Trimmed Message   "}'
# Ожидается: "text": "Trimmed Message"
```

---

### Сценарий 4: Тестирование пагинации

```bash
# Создаём чат
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Pagination Test"}')

CHAT_ID=$(echo $CHAT_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

# Создаём 25 сообщений
for i in {1..25}; do
  curl -s -X POST http://localhost:8000/chats/$CHAT_ID/messages/ \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Message $i\"}" > /dev/null
done

# Получаем первые 10 сообщений (самые новые)
curl "http://localhost:8000/chats/$CHAT_ID?limit=10&offset=0"

# Получаем следующие 10 сообщений
curl "http://localhost:8000/chats/$CHAT_ID?limit=10&offset=10"

# Получаем последние 5 сообщений
curl "http://localhost:8000/chats/$CHAT_ID?limit=5&offset=20"
```

---

### Сценарий 5: Тестирование каскадного удаления

```bash
# 1. Создаём чат
CHAT_RESPONSE=$(curl -s -X POST http://localhost:8000/chats/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Delete Test"}')

CHAT_ID=$(echo $CHAT_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

# 2. Создаём сообщения
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/chats/$CHAT_ID/messages/ \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"Message $i\"}" > /dev/null
done

# 3. Проверяем, что чат существует
curl http://localhost:8000/chats/$CHAT_ID

# 4. Удаляем чат
curl -X DELETE http://localhost:8000/chats/$CHAT_ID

# 5. Проверяем, что чат больше не существует (должен вернуть 404)
curl http://localhost:8000/chats/$CHAT_ID
```

---

## HTTPie Examples

Если вы используете [HTTPie](https://httpie.io/):

```bash
# Создать чат
http POST localhost:8000/chats/ title="General Discussion"

# Создать сообщение
http POST localhost:8000/chats/1/messages/ text="Hello, world!"

# Получить чат
http GET localhost:8000/chats/1

# Получить чат с пагинацией
http GET localhost:8000/chats/1 limit==10 offset==0

# Удалить чат
http DELETE localhost:8000/chats/1
```

---

## Swagger UI

Для интерактивного тестирования откройте Swagger UI:

http://localhost:8000/docs

Там вы можете выполнять запросы прямо из браузера и видеть схемы запросов/ответов.
