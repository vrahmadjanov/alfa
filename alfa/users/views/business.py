"""
Views для управления бизнесами
"""
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from users.models import Business, BusinessProfile
from users.serializers import (
    BusinessSerializer,
    BusinessCreateSerializer,
    BusinessUpdateSerializer,
    BusinessDetailSerializer,
    BusinessProfileSerializer
)
from users.utils.api_response import APIResponse, format_serializer_errors


class BusinessListCreateView(generics.ListCreateAPIView):
    """
    API endpoint для списка бизнесов и создания нового
    
    GET /api/businesses/
    Response:
    {
        "success": true,
        "message": "Список бизнесов получен",
        "data": [
            {
                "id": 1,
                "name": "Кофейня Эспрессо",
                "business_type": "cafe",
                ...
            }
        ]
    }
    
    POST /api/businesses/
    {
        "name": "Моя Кофейня",
        "business_type": "cafe",
        "description": "Уютная кофейня",
        "email": "cafe@example.com",
        "city": "Москва"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращаем только бизнесы текущего пользователя"""
        return Business.objects.filter(owner=self.request.user).select_related('owner')
    
    def get_serializer_class(self):
        """Используем разные serializers для GET и POST"""
        if self.request.method == 'POST':
            return BusinessCreateSerializer
        return BusinessSerializer
    
    def list(self, request, *args, **kwargs):
        """Переопределяем GET для стандартизированного ответа"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message=f"Найдено бизнесов: {len(serializer.data)}"
        )
    
    def create(self, request, *args, **kwargs):
        """Переопределяем POST для стандартизированного ответа"""
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        business = serializer.save()
        
        # Возвращаем детальную информацию о созданном бизнесе
        detail_serializer = BusinessDetailSerializer(business)
        
        return APIResponse.created(
            data=detail_serializer.data,
            message=f"Бизнес '{business.name}' успешно создан"
        )


class BusinessDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint для работы с конкретным бизнесом
    
    GET /api/businesses/{id}/
    PATCH /api/businesses/{id}/
    DELETE /api/businesses/{id}/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращаем только бизнесы текущего пользователя"""
        return Business.objects.filter(owner=self.request.user).select_related('owner', 'profile')
    
    def get_serializer_class(self):
        """Используем разные serializers для разных методов"""
        if self.request.method in ['PUT', 'PATCH']:
            return BusinessUpdateSerializer
        return BusinessDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """GET - получение детальной информации о бизнесе"""
        instance = self.get_object()
        serializer = BusinessDetailSerializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message="Информация о бизнесе получена"
        )
    
    def update(self, request, *args, **kwargs):
        """PATCH/PUT - обновление информации о бизнесе"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        self.perform_update(serializer)
        
        # Возвращаем детальную информацию
        detail_serializer = BusinessDetailSerializer(instance)
        
        return APIResponse.success(
            data=detail_serializer.data,
            message=f"Бизнес '{instance.name}' успешно обновлен"
        )
    
    def destroy(self, request, *args, **kwargs):
        """DELETE - архивирование бизнеса (мягкое удаление)"""
        instance = self.get_object()
        business_name = instance.name
        
        # Вместо удаления - архивируем
        instance.status = Business.Status.ARCHIVED
        instance.save()
        
        return APIResponse.success(
            message=f"Бизнес '{business_name}' успешно архивирован"
        )


class BusinessProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    API endpoint для работы с профилем бизнеса
    
    GET /api/businesses/{id}/profile/
    PATCH /api/businesses/{id}/profile/
    """
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Получаем профиль бизнеса текущего пользователя"""
        business_id = self.kwargs.get('pk')
        business = get_object_or_404(
            Business,
            id=business_id,
            owner=self.request.user
        )
        
        # Создаем профиль если его нет
        profile, created = BusinessProfile.objects.get_or_create(business=business)
        return profile
    
    def retrieve(self, request, *args, **kwargs):
        """GET - получение профиля бизнеса"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return APIResponse.success(
            data=serializer.data,
            message="Профиль бизнеса получен"
        )
    
    def update(self, request, *args, **kwargs):
        """PATCH/PUT - обновление профиля бизнеса"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return APIResponse.validation_error(
                errors=format_serializer_errors(serializer.errors),
                message="Ошибка валидации данных"
            )
        
        self.perform_update(serializer)
        
        return APIResponse.success(
            data=serializer.data,
            message="Профиль бизнеса успешно обновлен"
        )


class BusinessStatsView(APIView):
    """
    API endpoint для получения статистики по бизнесу
    
    GET /api/businesses/{id}/stats/
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        """Получение статистики бизнеса"""
        business = get_object_or_404(
            Business,
            id=pk,
            owner=request.user
        )
        
        # Получаем последние метрики
        latest_metrics = business.metrics.order_by('-date').first()
        
        stats = {
            'business_id': business.id,
            'business_name': business.name,
            'total_metrics_records': business.metrics.count(),
            'latest_metrics': None
        }
        
        if latest_metrics:
            stats['latest_metrics'] = {
                'date': latest_metrics.date,
                'period_type': latest_metrics.period_type,
                'revenue': str(latest_metrics.revenue),
                'expenses': str(latest_metrics.expenses),
                'profit': str(latest_metrics.profit),
                'customers_count': latest_metrics.customers_count,
                'transactions_count': latest_metrics.transactions_count,
                'avg_check': str(latest_metrics.avg_check) if latest_metrics.avg_check else None,
            }
        
        return APIResponse.success(
            data=stats,
            message="Статистика бизнеса получена"
        )

