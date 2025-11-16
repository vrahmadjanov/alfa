import apiClient from './client';

// Класс для API ошибок
class ApiError extends Error {
  constructor(errors) {
    super('API Error');
    this.name = 'ApiError';
    this.errors = errors;
  }
}

// Вспомогательная функция для извлечения ошибок из стандартного ответа API
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

export async function loginRequest(formData) {
  try {
    const response = await apiClient.post('/auth/login/', formData);
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    if (data?.access) {
      localStorage.setItem('access_token', data.access);
    }
    if (data?.refresh) {
      localStorage.setItem('refresh_token', data.refresh);
    }
    if (data?.user) {
      localStorage.setItem('current_user', JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}

export async function registerRequest(formData) {
  try {
    const response = await apiClient.post('/auth/register/', formData);
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}


