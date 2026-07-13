// 🔧 Центральная конфигурация всех API-эндпоинтов
const API_CONFIG = {
  BASE_URL: 'http://127.0.0.1:8000',

  endpoints: {

    login: {
      url: '/api/auth/login',
      method: 'POST',
      handler: 'handleLoginResponse',
      needs: ['login', 'password']
    },
    registration: {
      url: '/api/auth/registration',
      method: 'POST',
      handler: 'handleRegistrationResponse',
      needs: ['login', 'password']
    },
    googleUrl: {
      url: '/api/auth/google/url',
    },
    // 🔥 Эндпоинт для колбэка (обмен кода на сессию)
    googleCallback: {
      url: '/api/auth/google/callback',
      method: 'POST',
      handler: 'handleGoogleCallbackResponse',
      needs: ['code']
    }

  }

};