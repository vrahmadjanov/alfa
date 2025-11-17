import apiClient from './client';

// Класс для API ошибок
class ApiError extends Error {
  constructor(errors) {
    super('API Error');
    this.name = 'ApiError';
    this.errors = errors;
  }
}

function extractErrors(error) {
  if (error instanceof ApiError) {
    return error.errors;
  }
  if (error.response?.data?.errors) {
    return error.response.data.errors;
  }
  if (error.response?.data?.message) {
    return { general: error.response.data.message };
  }
  return { general: 'Произошла ошибка. Попробуйте снова.' };
}

// Получить список диалогов
export async function fetchConversations(params = {}) {
  try {
    const response = await apiClient.get('/chat/conversations/', { params });
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data || [];
  } catch (error) {
    throw extractErrors(error);
  }
}

// Создать новый диалог
export async function createConversation(payload) {
  try {
    const response = await apiClient.post('/chat/conversations/', payload);
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Получить детали диалога с сообщениями
export async function fetchConversation(conversationId) {
  try {
    const response = await apiClient.get(`/chat/conversations/${conversationId}/`);
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Отправить сообщение в диалог
export async function sendMessage(conversationId, content, model = null) {
  try {
    const payload = { content };
    if (model) {
      payload.model = model;
    }
    
    const response = await apiClient.post(
      `/chat/conversations/${conversationId}/messages/`,
      payload
    );
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Обновить диалог
export async function updateConversation(conversationId, payload) {
  try {
    const response = await apiClient.patch(
      `/chat/conversations/${conversationId}/`,
      payload
    );
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Архивировать диалог
export async function archiveConversation(conversationId) {
  try {
    const response = await apiClient.delete(`/chat/conversations/${conversationId}/`);
    const { success, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return true;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Получить статистику по диалогам
export async function fetchChatStats(businessId = null) {
  try {
    const params = {};
    if (businessId) {
      params.business = businessId;
    }
    
    const response = await apiClient.get('/chat/stats/', { params });
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

// Проверить статус обработки сообщения
export async function checkMessageStatus(conversationId, messageId) {
  try {
    const response = await apiClient.get(
      `/chat/conversations/${conversationId}/messages/${messageId}/status/`
    );
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}
