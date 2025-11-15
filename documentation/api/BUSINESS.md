# Business API - Документация

## Обзор

API для управления бизнесами. Позволяет владельцам создавать, просматривать, редактировать и архивировать свои бизнесы.

## Base URL

```
http://localhost/api/businesses/
```

**Все endpoints требуют аутентификации через JWT token.**

---

### 1. Создать бизнес

**POST** `/api/businesses/`

Создает новый бизнес для текущего пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Моя Кофейня",
  "business_type": "cafe",
  "description": "Уютная кофейня в центре города",
  "email": "cafe@example.com",
  "city": "Москва"
}
```

**Поля:**
- `name` (обязательно) - Название бизнеса
- `business_type` (обязательно) - Тип бизнеса: `cafe`, `restaurant`, `beauty_salon`, `barbershop`, `retail`, `fitness`, `services`, `other`
- `description` (опционально) - Описание бизнеса
- `email` (опционально) - Email бизнеса
- `city` (опционально) - Город

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Бизнес 'Моя Кофейня' успешно создан",
  "data": {
    "id": 1,
    "name": "Моя Кофейня",
    "business_type": "cafe",
    "description": "Уютная кофейня в центре города",
    "status": "active",
    "email": "cafe@example.com",
    "city": "Москва",
    "owner_email": "user@example.com",
    "owner_name": "Иван Иванов",
    "profile": {
      "employees_count": 1,
      "business_context": "",
      "ai_preferences": {},
      "updated_at": "2025-11-15T10:30:00Z"
    },
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
    "name": "У вас уже есть бизнес с таким названием"
  }
}
```

---

### 2. Получить список бизнесов

**GET** `/api/businesses/`

Возвращает список всех бизнесов текущего пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Найдено бизнесов: 2",
  "data": [
    {
      "id": 1,
      "name": "Кофейня Эспрессо",
      "business_type": "cafe",
      "description": "Уютная кофейня",
      "status": "active",
      "email": "espresso@example.com",
      "city": "Москва",
      "owner_email": "user@example.com",
      "created_at": "2025-11-15T10:30:00Z",
      "updated_at": "2025-11-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Салон Красоты",
      "business_type": "beauty_salon",
      "description": "Современный салон",
      "status": "active",
      "email": "salon@example.com",
      "city": "Москва",
      "owner_email": "user@example.com",
      "created_at": "2025-11-15T10:30:00Z",
      "updated_at": "2025-11-15T10:30:00Z"
    }
  ],
  "errors": null
}
```

---

### 3. Получить детали бизнеса

**GET** `/api/businesses/{id}/`

Возвращает детальную информацию о конкретном бизнесе, включая профиль.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Информация о бизнесе получена",
  "data": {
    "id": 1,
    "name": "Кофейня Эспрессо",
    "business_type": "cafe",
    "description": "Уютная кофейня в центре города",
    "status": "active",
    "email": "espresso@example.com",
    "city": "Москва",
    "owner_email": "user@example.com",
    "owner_name": "Иван Иванов",
    "profile": {
      "employees_count": 5,
      "business_context": "Кофейня специализируется на specialty coffee",
      "ai_preferences": {
        "tone": "friendly",
        "language": "ru"
      },
      "updated_at": "2025-11-15T10:30:00Z"
    },
    "created_at": "2025-11-15T10:30:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
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
    "detail": "Запрашиваемый ресурс не существует"
  }
}
```

---

### 4. Обновить бизнес

**PATCH** `/api/businesses/{id}/`

Обновляет информацию о бизнесе. Можно обновить любое из полей частично.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Новое название",
  "description": "Обновленное описание",
  "city": "Санкт-Петербург"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Бизнес 'Новое название' успешно обновлен",
  "data": {
    "id": 1,
    "name": "Новое название",
    "business_type": "cafe",
    "description": "Обновленное описание",
    "status": "active",
    "email": "espresso@example.com",
    "city": "Санкт-Петербург",
    "owner_email": "user@example.com",
    "owner_name": "Иван Иванов",
    "profile": { ... },
    "created_at": "2025-11-15T10:30:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
  },
  "errors": null
}
```

---

### 5. Архивировать бизнес

**DELETE** `/api/businesses/{id}/`

Архивирует бизнес (мягкое удаление). Бизнес не удаляется из базы, а переводится в статус `archived`.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Бизнес 'Кофейня Эспрессо' успешно архивирован",
  "data": null,
  "errors": null
}
```

---

### 6. Получить профиль бизнеса

**GET** `/api/businesses/{id}/profile/`

Возвращает расширенный профиль бизнеса с настройками для AI.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Профиль бизнеса получен",
  "data": {
    "employees_count": 5,
    "business_context": "Кофейня специализируется на specialty coffee. Работаем с 8:00 до 22:00. Основная аудитория - офисные работники 25-45 лет.",
    "ai_preferences": {
      "tone": "friendly",
      "language": "ru",
      "response_style": "detailed"
    },
    "updated_at": "2025-11-15T10:30:00Z"
  },
  "errors": null
}
```

---

### 7. Обновить профиль бизнеса

**PATCH** `/api/businesses/{id}/profile/`

Обновляет профиль бизнеса.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "employees_count": 8,
  "business_context": "Расширенное описание для AI ассистента. Специализация, график работы, целевая аудитория.",
  "ai_preferences": {
    "tone": "professional",
    "language": "ru"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Профиль бизнеса успешно обновлен",
  "data": {
    "employees_count": 8,
    "business_context": "Расширенное описание для AI ассистента...",
    "ai_preferences": {
      "tone": "professional",
      "language": "ru"
    },
    "updated_at": "2025-11-15T10:30:00Z"
  },
  "errors": null
}
```

---

### 8. Получить статистику бизнеса

**GET** `/api/businesses/{id}/stats/`

Возвращает статистику и метрики бизнеса.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Статистика бизнеса получена",
  "data": {
    "business_id": 1,
    "business_name": "Кофейня Эспрессо",
    "total_metrics_records": 30,
    "latest_metrics": {
      "date": "2025-11-15T10:30:00Z",
      "period_type": "day",
      "revenue": "45000.00",
      "expenses": "18000.00",
      "profit": "27000.00",
      "customers_count": 120,
      "transactions_count": 150,
      "avg_check": "300.00"
    }
  },
  "errors": null
}
```

---

## Типы бизнеса (business_type)

`cafe` - Кафе/Кофейня
`restaurant` - Ресторан
`beauty_salon` - Салон красоты
`barbershop` - Барбершоп
`retail` - Магазин
`fitness` - Фитнес/Спорт
`services` - Услуги
`other` - Другое

## Статусы бизнеса (status)

`active` - Активен (по умолчанию)
`inactive` - Неактивен
`archived` - Архивирован

---

## Примеры использования

### Создание бизнеса

```bash
curl -X POST http://localhost/api/businesses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Моя Кофейня",
    "business_type": "cafe",
    "description": "Уютная кофейня",
    "city": "Москва"
  }'
```

### Получение списка

```bash
curl -X GET http://localhost/api/businesses/ \
  -H "Authorization: Bearer <access_token>"
```

### Обновление бизнеса

```bash
curl -X PATCH http://localhost/api/businesses/1/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Новое описание"
  }'
```

### Архивирование

```bash
curl -X DELETE http://localhost/api/businesses/1/ \
  -H "Authorization: Bearer <access_token>"
```

---

## Коды ошибок

- **400 Bad Request** - Ошибка валидации данных
- **401 Unauthorized** - Требуется аутентификация
- **403 Forbidden** - Нет прав доступа
- **404 Not Found** - Бизнес не найден или принадлежит другому пользователю

---

## Бизнес-логика

### Владение бизнесом
- Пользователь может создавать неограниченное количество бизнесов
- Пользователь видит только свои бизнесы
- Название бизнеса должно быть уникальным в рамках одного пользователя

### Профиль бизнеса
- Профиль создается автоматически при создании бизнеса
- Поле `business_context` используется для предоставления контекста AI ассистенту
- `ai_preferences` - JSON объект с настройками для AI (тон, стиль ответов и т.д.)

### Архивирование
- При удалении бизнес не удаляется физически, а переводится в статус `archived`
- Архивированные бизнесы не отображаются в списке по умолчанию
- Все связанные данные (метрики, профиль) сохраняются

