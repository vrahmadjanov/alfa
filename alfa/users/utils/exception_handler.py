"""
Кастомный обработчик исключений для DRF
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated, PermissionDenied
from rest_framework import status
from django.http import Http404

from users.utils.api_response import APIResponse, format_serializer_errors


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для единообразных ответов API
    
    Args:
        exc: Исключение
        context: Контекст запроса
    
    Returns:
        Response: Стандартизированный ответ об ошибке
    """
    # Получаем стандартный ответ DRF
    response = exception_handler(exc, context)
    
    if response is not None:
        # Определяем тип ошибки и формируем соответствующий ответ
        
        if isinstance(exc, ValidationError):
            # Ошибки валидации
            errors = format_serializer_errors(response.data)
            return APIResponse.validation_error(
                errors=errors,
                message="Ошибка валидации данных"
            )
        
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            # Ошибки аутентификации
            error_message = str(exc.detail) if hasattr(exc, 'detail') else "Требуется аутентификация"
            return APIResponse.unauthorized(
                message=error_message,
                errors={"detail": error_message}
            )
        
        elif isinstance(exc, PermissionDenied):
            # Ошибки прав доступа
            error_message = str(exc.detail) if hasattr(exc, 'detail') else "Недостаточно прав"
            return APIResponse.forbidden(
                message=error_message,
                errors={"detail": error_message}
            )
        
        elif isinstance(exc, Http404):
            # Ресурс не найден
            return APIResponse.not_found(
                message="Ресурс не найден",
                errors={"detail": "Запрашиваемый ресурс не существует"}
            )
        
        else:
            # Общая ошибка
            error_message = str(exc.detail) if hasattr(exc, 'detail') else "Произошла ошибка"
            
            # Форматируем ошибки если они есть
            errors = None
            if hasattr(exc, 'detail'):
                if isinstance(exc.detail, dict):
                    errors = format_serializer_errors(exc.detail)
                elif isinstance(exc.detail, list):
                    errors = {"detail": exc.detail}
                else:
                    errors = {"detail": str(exc.detail)}
            
            return APIResponse.error(
                message=error_message,
                errors=errors,
                status_code=response.status_code
            )
    
    # Если response is None, значит это необработанное исключение
    # Возвращаем generic server error
    return APIResponse.server_error(
        message="Внутренняя ошибка сервера",
        errors={"detail": str(exc)}
    )

