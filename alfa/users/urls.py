"""
URL маршруты для аутентификации и управления пользователями
"""
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    VerifyTokenView,
    BusinessListCreateView,
    BusinessDetailView,
    BusinessProfileUpdateView,
    BusinessStatsView
)

app_name = 'users'

# Authentication endpoints
auth_patterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', VerifyTokenView.as_view(), name='verify_token'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]

# Business endpoints
business_patterns = [
    path('', BusinessListCreateView.as_view(), name='business_list_create'),
    path('<int:pk>/', BusinessDetailView.as_view(), name='business_detail'),
    path('<int:pk>/profile/', BusinessProfileUpdateView.as_view(), name='business_profile'),
    path('<int:pk>/stats/', BusinessStatsView.as_view(), name='business_stats'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('businesses/', include(business_patterns)),
]

