# Chat API - Документация

## Обзор

API для взаимодействия с AI ассистентом для бизнеса. Позволяет создавать диалоги, отправлять сообщения и получать ответы от AI.

## Base URL

```
http://localhost/api/chat/
```

**Все endpoints требуют аутентификации через JWT token.**

## Настройка OpenRouter API

Для работы чата с AI необходимо настроить OpenRouter API:

1. Пройти регистрацию в Open Router [openrouter.ai](https://openrouter.ai/)
2. Получить API ключ в разделе [Keys](https://openrouter.ai/keys)
3. Добавить в `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

# Основная модель (опционально, по умолчанию используется первая из списка)
OPENROUTER_MODEL=qwen/qwen3-30b-a3b:free

OPENROUTER_SITE_URL=http://localhost
OPENROUTER_SITE_NAME=Alfa
```

[Полный список моделей на OpenRouter](https://openrouter.ai/models)

### Множественные LLM модели

Система автоматически использует бесплатные модели с приоритетами. Если одна модель недоступна (rate limit, timeout), система автоматически переключается на следующую:

  1. `qwen/qwen3-30b-a3b:free`,
  2. `qwen/qwen3-14b:free`,
  3. `qwen/qwen3-235b-a22b:free`,
  4. `tngtech/deepseek-r1t-chimera:free`,
  5. `mistralai/mistral-small-3.1-24b-instruct:free`,
  6. `google/gemma-3-4b-it:free`,
  7. `google/gemini-2.0-flash-exp:free`,
  8. `qwen/qwen-2.5-72b-instruct:free`,
  9. `mistralai/mistral-nemo:free`,
  10. `nousresearch/hermes-3-llama-3.1-405b:free`,

**Преимущества:**
- **Высокая доступность** - если одна модель перегружена, система переключается на другую
- **Прозрачность** - в метаданных указывается, какая модель ответила и сколько попыток было сделано
- **Автоматическое восстановление** - не требует вмешательства пользователя

**Настройка:** Список моделей можно изменить в `alfa/settings.py` в переменной `OPENROUTER_MODELS`.

Подробнее см. [документацию по LLM интеграции](../dev/LLM_SETUP.md)

---

### 1. Создать новый диалог

**POST** `/api/chat/conversations/`

Создает новый диалог с AI ассистентом. Можно указать категорию и бизнес-контекст.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "category": "marketing",
  "business": 1,
  "first_message": "Привет! Нужна помощь с маркетинговой стратегией для моей кофейни"
}
```

**Поля:**
- `category` (опционально) - Категория диалога: `general`, `legal`, `marketing`, `finance`, `hr`, `operations`
- `business` (опционально) - ID бизнеса, в контексте которого ведется диалог
- `first_message` (опционально) - Первое сообщение пользователя для автоматической генерации заголовка

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Диалог успешно создан",
  "data": {
    "id": 1,
    "title": "Привет! Нужна помощь с маркетинговой стратегией...",
    "category": "marketing",
    "status": "active",
    "business": {
      "id": 1,
      "name": "Кофейня Эспрессо"
    },
    "messages_count": 1,
    "last_message_at": "2025-11-15T10:30:00Z",
    "created_at": "2025-11-15T10:30:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
  },
  "errors": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Ошибка валидации данных",
  "data": null,
  "errors": {
    "business": "Вы можете привязать только свой бизнес"
  }
}
```

---

### 2. Получить список диалогов

**GET** `/api/chat/conversations/`

Возвращает список всех диалогов текущего пользователя с возможностью фильтрации.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status` (опционально) - Фильтр по статусу: `active`, `archived`, `completed`
- `category` (опционально) - Фильтр по категории: `general`, `legal`, `marketing`, `finance`, `hr`, `operations`
- `business` (опционально) - Фильтр по ID бизнеса

**Examples:**
```
GET /api/chat/conversations/
GET /api/chat/conversations/?status=active
GET /api/chat/conversations/?category=marketing
GET /api/chat/conversations/?business=1
GET /api/chat/conversations/?status=active&category=legal
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Найдено диалогов: 3",
  "data": [
    {
      "id": 1,
      "title": "Маркетинговая стратегия для кофейни",
      "category": "marketing",
      "status": "active",
      "business": {
        "id": 1,
        "name": "Кофейня Эспрессо"
      },
      "messages_count": 12,
      "last_message_at": "2025-11-15T10:30:00Z",
      "created_at": "2025-11-14T09:00:00Z",
      "updated_at": "2025-11-15T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Юридические вопросы по найму",
      "category": "legal",
      "status": "active",
      "business": null,
      "messages_count": 5,
      "last_message_at": "2025-11-14T15:20:00Z",
      "created_at": "2025-11-14T14:00:00Z",
      "updated_at": "2025-11-14T15:20:00Z"
    }
  ],
  "errors": null
}
```

---

### 3. Получить детали диалога

**GET** `/api/chat/conversations/{id}/`

Возвращает детальную информацию о конкретном диалоге, включая все сообщения.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Диалог получен",
  "data": {
    "id": 1,
    "title": "Маркетинговая стратегия для кофейни",
    "category": "marketing",
    "status": "active",
    "business": {
      "id": 1,
      "name": "Кофейня Эспрессо"
    },
    "messages_count": 3,
    "last_message_at": "2025-11-15T10:30:00Z",
    "created_at": "2025-11-15T09:00:00Z",
    "updated_at": "2025-11-15T10:30:00Z",
    "messages": [
      {
        "id": 1,
        "role": "user",
        "content": "Привет! Нужна помощь с маркетинговой стратегией",
        "created_at": "2025-11-15T09:00:00Z"
      },
      {
        "id": 2,
        "role": "assistant",
        "content": "Здравствуйте! Я помогу вам с маркетинговой стратегией...",
        "model": "gpt-4",
        "tokens_used": 150,
        "response_time": 2.5,
        "created_at": "2025-11-15T09:00:15Z"
      },
      {
        "id": 3,
        "role": "user",
        "content": "Какие каналы продвижения посоветуешь?",
        "created_at": "2025-11-15T10:30:00Z"
      }
    ]
  },
  "errors": null
}
```

**Error Response (404 Not Found):**
```json
{
  "success": false,
  "message": "Ресурс не найден",
  "data": null,
  "errors": {
    "detail": "Диалог не найден"
  }
}
```

---

### 4. Обновить диалог

**PATCH** `/api/chat/conversations/{id}/`

Обновляет информацию о диалоге (заголовок, категория, статус).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "title": "Новый заголовок диалога",
  "category": "finance",
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Диалог успешно обновлен",
  "data": {
    "id": 1,
    "title": "Новый заголовок диалога",
    "category": "finance",
    "status": "completed",
    "business": null,
    "messages_count": 12,
    "last_message_at": "2025-11-15T10:30:00Z",
    "created_at": "2025-11-14T09:00:00Z",
    "updated_at": "2025-11-15T11:00:00Z"
  },
  "errors": null
}
```

---

### 5. Архивировать диалог

**DELETE** `/api/chat/conversations/{id}/`

Архивирует диалог (мягкое удаление). Диалог переводится в статус `archived`.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Диалог успешно архивирован",
  "data": null,
  "errors": null
}
```

---

### 6. Получить список сообщений

**GET** `/api/chat/conversations/{conversation_id}/messages/`

Возвращает список всех сообщений в диалоге.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Найдено сообщений: 12",
  "data": [
    {
      "id": 1,
      "role": "user",
      "content": "Привет! Нужна помощь с маркетингом",
      "created_at": "2025-11-15T09:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Здравствуйте! Я помогу вам с маркетинговой стратегией...",
      "model": "deepseek/deepseek-r1:free",
      "tokens_used": 150,
      "response_time": 2.5,
      "created_at": "2025-11-15T09:00:15Z"
    }
  ],
  "errors": null
}
```

---

### 7. Отправить сообщение

**POST** `/api/chat/conversations/{conversation_id}/messages/`

Отправляет сообщение в диалог и получает ответ от AI ассистента.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "content": "Какую социальную сеть лучше использовать для продвижения кофейни?"
}
```

**Validation:**
- `content` не может быть пустым
- Максимальная длина: 4000 символов

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Сообщение отправлено",
  "data": {
    "user_message": {
      "id": 10,
      "role": "user",
      "content": "Какую социальную сеть лучше использовать для продвижения кофейни?",
      "created_at": "2025-11-15T10:30:00Z"
    },
    "assistant_message": {
      "id": 11,
      "role": "assistant",
      "content": "Для продвижения кофейни наиболее эффективными будут Instagram и ВКонтакте. Instagram отлично подходит для визуального контента - фото напитков, интерьера, процесса приготовления кофе. ВКонтакте позволяет создать сообщество и делать таргетированную рекламу на локальную аудиторию. Также рекомендую использовать Telegram для программы лояльности и специальных предложений.",
      "model": "google/gemini-2.0-flash-exp",
      "tokens_used": 180,
      "response_time": 3.2,
      "created_at": "2025-11-15T10:30:03Z",
      "metadata": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "attempted_models": 1,
        "fallback_used": false
      }
    }
  },
  "errors": null
}
```

**Важно:** 
- Ответ от AI генерируется в реальном времени через OpenRouter API
- Система автоматически пробует до 10 различных моделей при ошибках
- Время ответа обычно составляет 30-60 секунд (зависит от модели и сложности запроса)
- При использовании fallback время может увеличиться до нескольких минут

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Ошибка валидации данных",
  "data": null,
  "errors": {
    "content": ["Сообщение не может быть пустым"]
  }
}
```

---

### 8. Получить статистику по диалогам

**GET** `/api/chat/stats/`

Возвращает общую статистику по всем диалогам пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Статистика получена",
  "data": {
    "total_conversations": 15,
    "active_conversations": 8,
    "archived_conversations": 5,
    "completed_conversations": 2,
    "total_messages": 247,
    "by_category": {
      "general": {
        "count": 5,
        "percentage": 33.3
      },
      "marketing": {
        "count": 6,
        "percentage": 40.0
      },
      "legal": {
        "count": 2,
        "percentage": 13.3
      },
      "finance": {
        "count": 2,
        "percentage": 13.3
      }
    },
    "by_business": [
      {
        "business_id": 1,
        "business_name": "Кофейня Эспрессо",
        "conversations_count": 8
      },
      {
        "business_id": 2,
        "business_name": "Салон Красоты",
        "conversations_count": 3
      }
    ]
  },
  "errors": null
}
```

---

## Категории диалогов (category)

- `general` - Общее (по умолчанию)
- `legal` - Юридическая консультация
- `marketing` - Маркетинг
- `finance` - Финансы
- `hr` - Управление персоналом
- `operations` - Операционные вопросы

## Статусы диалогов (status)

- `active` - Активен (по умолчанию)
- `archived` - Архивирован
- `completed` - Завершен

## Роли сообщений (role)

- `user` - Сообщение пользователя
- `assistant` - Ответ AI ассистента
- `system` - Системное сообщение

---

## Примеры использования

### Создание нового диалога с первым сообщением

```bash
curl -X POST http://localhost/api/chat/conversations/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "marketing",
    "business": 1,
    "first_message": "Привет! Нужна помощь с SMM стратегией"
  }'
```

### Получение списка активных диалогов по маркетингу

```bash
curl -X GET "http://localhost/api/chat/conversations/?status=active&category=marketing" \
  -H "Authorization: Bearer <access_token>"
```

### Получение списка сообщений

```bash
curl -X GET http://localhost/api/chat/conversations/1/messages/ \
  -H "Authorization: Bearer <access_token>"
```

### Отправка сообщения и получение ответа от AI

```bash
curl -X POST http://localhost/api/chat/conversations/1/messages/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Какой бюджет нужен на рекламу в Instagram?"
  }'
```

### Получение детальной информации о диалоге (включая все сообщения)

```bash
curl -X GET http://localhost/api/chat/conversations/1/ \
  -H "Authorization: Bearer <access_token>"
```

### Архивирование диалога

```bash
curl -X DELETE http://localhost/api/chat/conversations/1/ \
  -H "Authorization: Bearer <access_token>"
```

### Получение статистики

```bash
curl -X GET http://localhost/api/chat/stats/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Обработка ошибок LLM и Fallback механизм

Система использует **интеллектуальный fallback механизм** для обеспечения высокой доступности:

### Как работает fallback

1. **Первая попытка** - система пытается использовать основную модель
2. **Автоматическое переключение** - при ошибке (rate limit, timeout) автоматически пробует следующую модель из списка
3. **До 10 попыток** - система пробует все доступные модели
4. **Успешный ответ** - как только модель отвечает, результат возвращается пользователю

### Пример успешного fallback

Когда первая модель недоступна, но вторая отвечает успешно:

```json
{
  "success": true,
  "message": "Сообщение отправлено",
  "data": {
    "user_message": { ... },
    "assistant_message": {
      "id": 11,
      "role": "assistant",
      "content": "Ваш вопрос о маркетинге...",
      "model": "qwen/qwen-2.5-72b-instruct",
      "tokens_used": 245,
      "response_time": 5.8,
      "metadata": {
        "temperature": 0.7,
        "max_tokens": 1000,
        "attempted_models": 2,
        "fallback_used": true
      }
    }
  }
}
```

**Обратите внимание:**
- `attempted_models: 2` - было сделано 2 попытки (первая не удалась, вторая успешна)
- `fallback_used: true` - использовался fallback механизм
- `model` - показывает, какая модель в итоге ответила

### Пример полного отказа всех моделей

Только когда **все** модели недоступны, система возвращает дружелюбное сообщение об ошибке:

```json
{
  "success": true,
  "message": "Сообщение отправлено",
  "data": {
    "user_message": { ... },
    "assistant_message": {
      "id": 11,
      "role": "assistant",
      "content": "Извините, сейчас слишком много запросов. Попробуйте через минуту.",
      "model": "error-fallback",
      "tokens_used": null,
      "response_time": 28.5,
      "metadata": {
        "error": true,
        "error_type": "rate_limit",
        "error_message": "Rate limit exceeded"
      }
    }
  }
}
```


---

## Бизнес-логика

### Создание диалогов
- Пользователь может создавать неограниченное количество диалогов
- При указании `business` диалог получает контекст этого бизнеса для AI
- `first_message` автоматически создает первое сообщение и генерирует заголовок
- Если заголовок не указан, он генерируется из первых 50 символов первого сообщения

### Контекст бизнеса
- Когда диалог привязан к бизнесу, AI ассистент получает дополнительный контекст:
  - Тип бизнеса
  - Описание
  - Информацию из `BusinessProfile.business_context`
  - Настройки AI из `BusinessProfile.ai_preferences`

### Ответы AI ассистента

- **Интеграция с OpenRouter API** - используется система из 10 бесплатных моделей с автоматическим fallback
- **Fallback модели** - при недоступности основной модели система автоматически пробует альтернативные модели
  
AI получает полный контекст:
- **Системный промпт** в зависимости от категории диалога (маркетинг, юридика, финансы и т.д.)
- **Историю последних 10 сообщений** диалога для понимания контекста
- **Информацию о бизнесе** (если диалог привязан к бизнесу):
  - Тип и название бизнеса
  - Описание и город
  - Количество сотрудников
  - Дополнительный контекст из `BusinessProfile.business_context`
  - Настройки тона общения из `BusinessProfile.ai_preferences`

### Метаданные сообщений

- `model` - название модели LLM, которая сгенерировала ответ (например, `google/gemini-2.0-flash-exp`)
- `tokens_used` - количество токенов, потраченных на генерацию
- `response_time` - время генерации ответа в секундах
- `metadata` - дополнительная информация:
  - `temperature` - параметр креативности (0.0-1.0)
  - `max_tokens` - максимальное количество токенов в ответе
  - `attempted_models` - сколько моделей было попробовано (1 = успешно с первой попытки)
  - `fallback_used` - был ли использован fallback механизм (true/false)
  - `error` - присутствует только при ошибках (true)
  - `error_type` - тип ошибки (только при ошибках)
  - `finish_reason` - причина завершения генерации (`stop`, `length`, и т.д.)

### Архивирование
- При удалении диалог не удаляется физически, а переводится в статус `archived`
- Все сообщения сохраняются
- Архивированные диалоги можно фильтровать через `?status=archived`

