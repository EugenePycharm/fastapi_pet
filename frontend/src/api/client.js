// API клиент для работы с backend
const API_BASE_URL = '/api/v1';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  setToken(token, refreshToken) {
    this.token = token;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', token);
    localStorage.setItem('refresh_token', refreshToken);
  }

  clearToken() {
    this.token = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Токен истёк, пробуем обновить
        await this.refreshAccessToken();
        // Повторяем запрос с новым токеном
        headers['Authorization'] = `Bearer ${this.token}`;
        const retryResponse = await fetch(url, { ...config, headers });
        return this.handleResponse(retryResponse);
      }

      return this.handleResponse(response);
    } catch (error) {
      throw new Error(error.message || 'Ошибка сети');
    }
  }

  async handleResponse(response) {
    if (response.status === 204) {
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Ошибка запроса');
    }

    return data;
  }

  async refreshAccessToken() {
    if (!this.refreshToken) {
      throw new Error('Нет refresh токена');
    }

    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: this.refreshToken }),
    });

    if (!response.ok) {
      this.clearToken();
      throw new Error('Не удалось обновить токен');
    }

    const data = await response.json();
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  // Auth endpoints
  async register(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });
    return this.handleResponse(response);
  }

  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    const data = await this.handleResponse(response);
    this.setToken(data.access_token, data.refresh_token);
    return data;
  }

  async getMe() {
    return this.request('/auth/me');
  }

  async logout() {
    this.clearToken();
  }

  // Chats endpoints
  async getChats(limit = 20, offset = 0) {
    return this.request(`/chats?limit=${limit}&offset=${offset}`);
  }

  async createChat(title) {
    return this.request('/chats', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async getChat(chatId) {
    return this.request(`/chats/${chatId}`);
  }

  async deleteChat(chatId) {
    return this.request(`/chats/${chatId}`, {
      method: 'DELETE',
    });
  }

  async sendMessage(chatId, content, role = 'user') {
    return this.request(`/chats/${chatId}/message`, {
      method: 'POST',
      body: JSON.stringify({ role, content }),
    });
  }

  async sendMessageStream(chatId, content, role = 'user', onChunk) {
    const url = `${API_BASE_URL}/chats/${chatId}/message/stream`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
      },
      body: JSON.stringify({ role, content }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || error.message || 'Ошибка отправки сообщения');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let fullContent = '';

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Декодируем чанк с сохранением буфера для неполных данных
        buffer += decoder.decode(value, { stream: true });
        
        // Разделяем по линиям SSE
        const lines = buffer.split('\n');
        
        // Последняя линия может быть неполной, сохраняем её в буфере
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmedLine.slice(6));

              if (data.type === 'chunk') {
                fullContent += data.content;
                // Вызываем callback для каждого чанка
                onChunk(data.content, data.timestamp);
              } else if (data.type === 'done') {
                return fullContent;
              } else if (data.type === 'error') {
                throw new Error(data.message);
              }
            } catch (parseError) {
              // Игнорируем ошибки парсинга JSON для неполных данных
              console.warn('Parse error:', parseError);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }

    return fullContent;
  }

  // Settings endpoints
  async getSettings() {
    return this.request('/settings');
  }

  async updateSettings(settingsData) {
    return this.request('/settings', {
      method: 'PUT',
      body: JSON.stringify(settingsData),
    });
  }

  async testApiKey(apiKey) {
    return this.request('/settings/test-api-key', {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey }),
    });
  }
}

export const apiClient = new ApiClient();
export default apiClient;
