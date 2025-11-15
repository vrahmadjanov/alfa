"""
Serializers для управления бизнесом
"""
from rest_framework import serializers
from users.models import Business

class BusinessSerializer(serializers.ModelSerializer):
    """
    Serializer для информации о бизнесе
    """
    class Meta:
        model = Business
        fields = ['id', 'name', 'business_type', 'description', 'status', 
                  'email', 'city', 'created_at']
        read_only_fields = ['id', 'created_at']