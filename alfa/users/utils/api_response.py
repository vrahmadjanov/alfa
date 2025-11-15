"""
Стандартизированная обертка для API ответов
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """
    Стандартизированный формат ответа API
    
    Структура ответа:
    {
        "success": true/false,
        "message": "Описание результата",
        "data": {...},  # Данные ответа
        "errors": {...}  # Ошибки валидации (если есть)
    }
    """
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK, **kwargs):
        """
        Успешный ответ API
        
        Args:
            data: Данные для возврата
            message: Сообщение об успехе
            status_code: HTTP статус код
            **kwargs: Дополнительные поля для ответа
        
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "errors": None
        }
        
        # Добавляем дополнительные поля если есть
        response_data.update(kwargs)
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message="Error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST, data=None, **kwargs):
        """
        Ответ с ошибкой API
        
        Args:
            message: Сообщение об ошибке
            errors: Детали ошибок (словарь или список)
            status_code: HTTP статус код
            data: Данные (обычно None для ошибок)
            **kwargs: Дополнительные поля для ответа
        
        Returns:
            Response: DRF Response object
        """
        response_data = {
            "success": False,
            "message": message,
            "data": data,
            "errors": errors
        }
        
        # Добавляем дополнительные поля если есть
        response_data.update(kwargs)
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def created(data=None, message="Resource created successfully", **kwargs):
        """
        Ответ при успешном создании ресурса (201)
        """
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            **kwargs
        )
    
    @staticmethod
    def no_content(message="Operation successful", **kwargs):
        """
        Ответ без содержимого (204)
        """
        return APIResponse.success(
            data=None,
            message=message,
            status_code=status.HTTP_204_NO_CONTENT,
            **kwargs
        )
    
    @staticmethod
    def unauthorized(message="Authentication required", errors=None, **kwargs):
        """
        Ответ о необходимости аутентификации (401)
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_401_UNAUTHORIZED,
            **kwargs
        )
    
    @staticmethod
    def forbidden(message="Permission denied", errors=None, **kwargs):
        """
        Ответ о недостатке прав доступа (403)
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_403_FORBIDDEN,
            **kwargs
        )
    
    @staticmethod
    def not_found(message="Resource not found", errors=None, **kwargs):
        """
        Ответ о ненайденном ресурсе (404)
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_404_NOT_FOUND,
            **kwargs
        )
    
    @staticmethod
    def validation_error(errors, message="Validation failed", **kwargs):
        """
        Ответ с ошибками валидации (400)
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST,
            **kwargs
        )
    
    @staticmethod
    def server_error(message="Internal server error", errors=None, **kwargs):
        """
        Ответ о внутренней ошибке сервера (500)
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            **kwargs
        )


def format_serializer_errors(serializer_errors):
    """
    Форматирует ошибки DRF serializer в читаемый формат
    
    Args:
        serializer_errors: Словарь ошибок из serializer.errors
    
    Returns:
        dict: Отформатированные ошибки
    """
    formatted_errors = {}
    
    for field, errors in serializer_errors.items():
        if isinstance(errors, list):
            # Берем первое сообщение об ошибке для каждого поля
            formatted_errors[field] = errors[0] if errors else "Invalid value"
        else:
            formatted_errors[field] = str(errors)
    
    return formatted_errors

