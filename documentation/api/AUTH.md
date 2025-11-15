# API Аутентификации - Документация

### 1. Регистрация нового пользователя

**POST** `/api/auth/register/`

Создает нового пользователя и возвращает JWT токены.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123",
  "password_confirm": "secure_password123",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Пользователь успешно зарегистрирован",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Иван",
      "last_name": "Иванов",
      "is_email_verified": false,
      "date_joined": "2024-01-15T10:30:00Z"
    }
  },
  "errors": null
}
```

**Validation:**
- Email должен быть уникальным и валидным
- Пароли должны совпадать
- Пароль должен соответствовать требованиям безопасности Django

---

### 2. Авторизация пользователя

**POST** `/api/auth/login/`

Аутентифицирует пользователя и возвращает JWT токены.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Вход выполнен успешно",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Иван",
      "last_name": "Иванов",
      "is_email_verified": false,
      "date_joined": "2024-01-15T10:30:00Z"
    }
  },
  "errors": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Ошибка авторизации",
  "data": null,
  "errors": {
    "email": "Неверный email или пароль"
  }
}
```

---

### 3. Выход из системы

**POST** `/api/auth/logout/`

Добавляет refresh token в blacklist (делает его невалидным).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Вы успешно вышли из системы",
  "data": null,
  "errors": null
}
```

**Error Response (400 Bad Request):**
```json
{
  "success": false,
  "message": "Невалидный или истекший токен",
  "data": null,
  "errors": {
    "refresh": "Token is invalid or expired"
  }
}
```

---

### 4. Обновление access токена

**POST** `/api/auth/token/refresh/`

Обновляет access token используя refresh token.

**Request Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 5. Проверка токена

**GET** `/api/auth/verify/`

Проверяет валидность access токена и возвращает информацию о пользователе.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Токен валиден",
  "data": {
    "valid": true,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "first_name": "Иван",
      "last_name": "Иванов",
      "is_email_verified": false,
      "date_joined": "2024-01-15T10:30:00Z"
    }
  },
  "errors": null
}
```

---

### 6. Получить текущего пользователя

**GET** `/api/auth/me/`

Возвращает полную информацию о текущем аутентифицированном пользователе, включая связанные бизнесы.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Профиль пользователя получен",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "is_email_verified": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "businesses": [
      {
        "id": 1,
        "name": "Кофейня Эспрессо",
        "business_type": "cafe",
        "description": "Уютная кофейня в центре города",
        "status": "active",
        "email": "espresso@example.com",
        "city": "Москва",
        "created_at": "2024-01-10T12:00:00Z"
      }
    ]
  },
  "errors": null
}
```

---

### 7. Обновить профиль пользователя

**PATCH** `/api/auth/me/`

Обновляет информацию текущего пользователя.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Новое имя",
  "last_name": "Новая фамилия"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Профиль успешно обновлен",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "Новое имя",
    "last_name": "Новая фамилия",
    "is_email_verified": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "businesses": []
  },
  "errors": null
}
```

---

### Примеры с cURL

```bash
# Регистрация
curl -X POST http://localhost/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "secure_password123",
    "password_confirm": "secure_password123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Логин
curl -X POST http://localhost/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "secure_password123"
  }'

# Получить профиль
curl -X GET http://localhost/api/auth/me/ \
  -H "Authorization: Bearer <your_access_token>"

# Обновить токен
curl -X POST http://localhost/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'

# Выход
curl -X POST http://localhost/api/auth/logout/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```