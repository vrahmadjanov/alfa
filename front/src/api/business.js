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

export async function fetchBusinesses() {
  try {
    const response = await apiClient.get('/businesses/');
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data || [];
  } catch (error) {
    throw extractErrors(error);
  }
}

export async function createBusiness(payload) {
  try {
    const response = await apiClient.post('/businesses/', payload);
    const { success, data, errors } = response.data;

    if (!success) {
      throw new ApiError(errors || { general: response.data.message });
    }

    return data;
  } catch (error) {
    throw extractErrors(error);
  }
}


