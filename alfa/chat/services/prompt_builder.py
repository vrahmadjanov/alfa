"""
Построение промптов для AI ассистента с учетом контекста бизнеса
"""
from typing import List, Dict, Optional
from chat.models import Conversation, Message
from users.models import Business


class PromptBuilder:
    """
    Класс для построения промптов с контекстом
    """
    
    # Системные промпты по категориям
    SYSTEM_PROMPTS = {
        'general': """Ты - опытный бизнес-консультант, помогающий владельцам малого и среднего бизнеса. 
Давай практичные, применимые советы. Будь дружелюбным, но профессиональным.""",
        
        'legal': """Ты - юридический консультант, специализирующийся на малом бизнесе. 
Давай общую информацию о законодательстве, но всегда рекомендуй консультироваться с профессиональным юристом для конкретных случаев.
ВАЖНО: Ты не даешь юридических заключений, только общую информацию.""",
        
        'marketing': """Ты - маркетолог-эксперт, помогающий малому бизнесу с продвижением.
Давай конкретные, применимые рекомендации по маркетингу с учетом ограниченного бюджета.
Фокусируйся на digital-маркетинге и локальном продвижении.""",
        
        'finance': """Ты - финансовый консультант для малого бизнеса.
Помогай с планированием бюджета, оптимизацией расходов, ценообразованием.
Давай практичные советы по управлению финансами.""",
        
        'hr': """Ты - HR-консультант для малого бизнеса.
Помогай с наймом, управлением персоналом, мотивацией команды.
Учитывай специфику малого бизнеса где владелец часто сам является HR.""",
        
        'operations': """Ты - консультант по операционному управлению бизнесом.
Помогай с процессами, организацией работы, повышением эффективности.
Давай практичные советы, применимые для малого бизнеса."""
    }
    
    @classmethod
    def build_system_prompt(cls, conversation: Conversation) -> str:
        """
        Построение системного промпта с учетом категории и бизнеса
        """
        # Базовый промпт по категории
        base_prompt = cls.SYSTEM_PROMPTS.get(
            conversation.category,
            cls.SYSTEM_PROMPTS['general']
        )
        
        # Если есть привязка к бизнесу, добавляем контекст
        if conversation.business:
            business = conversation.business
            business_context = cls._build_business_context(business)
            
            system_prompt = f"""{base_prompt}

КОНТЕКСТ БИЗНЕСА:
{business_context}

При ответах учитывай этот контекст и давай персонализированные рекомендации."""
            
            return system_prompt
        
        return base_prompt
    
    @classmethod
    def _build_business_context(cls, business: Business) -> str:
        """
        Построение контекста бизнеса для промпта
        """
        context_parts = []
        
        # Основная информация
        context_parts.append(f"Название: {business.name}")
        context_parts.append(f"Тип: {business.get_business_type_display()}")
        
        if business.city:
            context_parts.append(f"Город: {business.city}")
        
        if business.description:
            context_parts.append(f"Описание: {business.description}")
        
        # Информация из профиля
        if hasattr(business, 'profile'):
            profile = business.profile
            
            if profile.employees_count:
                context_parts.append(f"Количество сотрудников: {profile.employees_count}")
            
            if profile.business_context:
                context_parts.append(f"\nДополнительная информация:\n{profile.business_context}")
            
            # AI предпочтения
            if profile.ai_preferences:
                prefs = profile.ai_preferences
                
                if 'tone' in prefs:
                    tone_map = {
                        'friendly': 'дружелюбный',
                        'professional': 'профессиональный',
                        'casual': 'неформальный'
                    }
                    tone = tone_map.get(prefs['tone'], prefs['tone'])
                    context_parts.append(f"\nТон общения: {tone}")
        
        return "\n".join(context_parts)
    
    @classmethod
    def build_messages_history(cls, conversation: Conversation, limit: int = 10) -> List[Dict[str, str]]:
        """
        Построение истории сообщений для контекста
        
        Args:
            conversation: Диалог
            limit: Максимальное количество последних сообщений (по умолчанию 10)
        
        Returns:
            Список сообщений в формате OpenAI
        """
        messages = []
        
        # Добавляем системный промпт
        system_prompt = cls.build_system_prompt(conversation)
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Добавляем историю сообщений (последние N)
        history = conversation.messages.order_by('-created_at')[:limit]
        history = reversed(list(history))  # От старых к новым
        
        for msg in history:
            # Пропускаем системные сообщения
            if msg.role == Message.Role.SYSTEM:
                continue
            
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return messages
    
    @classmethod
    def format_error_response(cls, error_type: str) -> str:
        """
        Формирование дружелюбного ответа при ошибке LLM
        """
        error_responses = {
            'rate_limit': "Извините, сейчас слишком много запросов. Попробуйте через минуту.",
            'api_error': "Извините, произошла техническая ошибка. Попробуйте еще раз через несколько секунд.",
            'timeout': "Извините, запрос занял слишком много времени. Попробуйте переформулировать вопрос более кратко.",
            'invalid_request': "Извините, не удалось обработать ваш запрос. Попробуйте переформулировать.",
            'default': "Извините, не удалось получить ответ. Попробуйте еще раз."
        }
        
        return error_responses.get(error_type, error_responses['default'])

