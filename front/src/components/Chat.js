import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendMessage, createConversation, fetchConversation, fetchConversations } from '../api/chat';
import './Chat.css';

function Chat({ businesses, currentConversation, onConversationCreated, initialBusinessId }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedBusiness, setSelectedBusiness] = useState(initialBusinessId ? String(initialBusinessId) : '');
  const [selectedConversation, setSelectedConversation] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [conversations, setConversations] = useState([]);
  const [errors, setErrors] = useState({});
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Обновляем выбранный бизнес если изменился initialBusinessId
  useEffect(() => {
    if (initialBusinessId) {
      setSelectedBusiness(String(initialBusinessId));
    }
  }, [initialBusinessId]);
  
  // Список доступных моделей
  const availableModels = [
    { id: '', name: 'Модель' },
    { id: 'qwen/qwen3-30b-a3b:free', name: 'Qwen 3 30B' },
    { id: 'google/gemini-2.0-flash-exp:free', name: 'Google Gemini 2.0' },
    { id: 'mistralai/mistral-small-3.1-24b-instruct:free', name: 'Mistral Small 3.1' },
    { id: 'qwen/qwen-2.5-72b-instruct:free', name: 'Qwen 2.5 72B' },
  ];

  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      // Прокручиваем только контейнер с сообщениями, а не всю страницу
      messagesEndRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'nearest',  // Не прокручивать страницу, только контейнер
        inline: 'nearest'
      });
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  };

  // Прокручиваем только когда добавляется новое сообщение, а не при загрузке
  useEffect(() => {
    // Используем requestAnimationFrame для отложенной прокрутки после рендера
    if (messages.length > 0) {
      const timeoutId = setTimeout(() => {
        scrollToBottom();
      }, 100);
      return () => clearTimeout(timeoutId);
    }
  }, [messages.length]); // Зависимость только от длины массива

  useEffect(() => {
    adjustTextareaHeight();
  }, [inputValue]);

  useEffect(() => {
    if (currentConversation) {
      loadConversation(currentConversation);
      setSelectedConversation(String(currentConversation));
    }
  }, [currentConversation]);

  useEffect(() => {
    // Загружаем список диалогов
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const data = await fetchConversations({ status: 'active' });
      setConversations(data || []);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const handleConversationChange = async (conversationId) => {
    setSelectedConversation(conversationId);
    if (conversationId) {
      await loadConversation(conversationId);
      if (onConversationCreated) {
        onConversationCreated({ id: parseInt(conversationId, 10) });
      }
    } else {
      setMessages([]);
      if (onConversationCreated) {
        onConversationCreated(null);
      }
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const data = await fetchConversation(conversationId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setErrors({});
    setIsLoading(true);
    
    // Сбрасываем высоту textarea после отправки
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      let conversationId = currentConversation;

      // Если нет активного диалога, создаем новый
      if (!conversationId) {
        const payload = {
          first_message: userMessage,
          category: 'general'
        };
        
        if (selectedBusiness) {
          payload.business = parseInt(selectedBusiness, 10);
        }

        if (selectedModel) {
          payload.preferred_model = selectedModel;
        }

        const newConversation = await createConversation(payload);
        conversationId = newConversation.id;
        setSelectedConversation(String(conversationId));
        
        if (onConversationCreated) {
          onConversationCreated({ id: conversationId });
        }

        // Загружаем сообщения нового диалога
        await loadConversation(conversationId);
        // Обновляем список диалогов
        await loadConversations();
      } else {
        // Добавляем сообщение пользователя в UI
        const tempUserMessage = {
          id: Date.now(),
          role: 'user',
          content: userMessage,
          created_at: new Date().toISOString()
        };
        setMessages((prev) => [...prev, tempUserMessage]);

        // Отправляем сообщение (передаем модель, если выбрана)
        const response = await sendMessage(conversationId, userMessage, selectedModel || null);
        
        // Проверяем, что ответ ассистента не пустой
        const assistantContent = response.assistant_message?.content || '';
        
        if (!assistantContent.trim()) {
          // Если контент пустой, показываем ошибку
          setMessages((prev) => [
            ...prev.filter(m => m.id !== tempUserMessage.id),
            response.user_message,
            {
              ...response.assistant_message,
              content: 'Извините, произошла ошибка при генерации ответа. Попробуйте переформулировать вопрос или задать другой.',
              error: true
            }
          ]);
          setErrors({ general: 'Не удалось получить ответ от AI. Попробуйте еще раз.' });
        } else {
          // Обновляем сообщения с ответом от сервера
          setMessages((prev) => [
            ...prev.filter(m => m.id !== tempUserMessage.id),
            response.user_message,
            response.assistant_message
          ]);
        }
      }
    } catch (apiErrors) {
      setErrors(apiErrors);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2 className="chat-title">AI Ассистент</h2>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty">
            <p className="chat-empty-title">Здравствуйте! 👋</p>
            <p className="chat-empty-text">
              Я AI-ассистент для владельцев бизнеса. Задайте мне любой вопрос о маркетинге, финансах, юридических аспектах или управлении персоналом.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`chat-message chat-message--${message.role} ${message.error ? 'chat-message--error' : ''}`}
            >
              <div className="chat-message-content">
                {message.role === 'assistant' ? (
                  <ReactMarkdown>
                    {message.content || '(Пустой ответ)'}
                  </ReactMarkdown>
                ) : (
                  message.content || '(Пустой ответ)'
                )}
              </div>
              {message.role === 'assistant' && (
                <div className="chat-message-meta">
                  {message.model && (
                    <span className="chat-message-model">{message.model}</span>
                  )}
                  {message.response_time && (
                    <span className="chat-message-time">
                      {message.response_time.toFixed(1)}s
                    </span>
                  )}
                  {message.tokens_used && (
                    <span className="chat-message-tokens">
                      {message.tokens_used} токенов
                    </span>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="chat-message chat-message--assistant">
            <div className="chat-message-content">
              <div className="chat-typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-controls">
        <select
          className="chat-control-pill"
          value={selectedBusiness}
          onChange={(e) => setSelectedBusiness(e.target.value)}
          disabled={!!initialBusinessId}
        >
          {!initialBusinessId && <option value="">Бизнес</option>}
          {businesses.map((biz) => (
            <option key={biz.id} value={biz.id}>
              {biz.name}
            </option>
          ))}
        </select>

        <select
          className="chat-control-pill"
          value={selectedConversation}
          onChange={(e) => handleConversationChange(e.target.value)}
        >
          <option value="">Диалог</option>
          {conversations.map((conv) => (
            <option key={conv.id} value={conv.id}>
              {conv.title || `Диалог #${conv.id}`}
            </option>
          ))}
        </select>

        <select
          className="chat-control-pill"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          {availableModels.map((model) => (
            <option key={model.id} value={model.id}>
              {model.name}
            </option>
          ))}
        </select>
      </div>

      {errors.general && (
        <div className="chat-error">
          {errors.general}
        </div>
      )}

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <textarea
          ref={textareaRef}
          className="chat-input"
          placeholder="Напишите ваш вопрос..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          rows="1"
          disabled={isLoading}
        />
        <button
          type="submit"
          className="chat-submit"
          disabled={!inputValue.trim() || isLoading}
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </form>
    </div>
  );
}

export default Chat;

