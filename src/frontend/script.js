document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.tab');
  const form = document.getElementById('auth-form');
  const submitBtn = document.getElementById('submit-btn');
  const googleBtn = document.getElementById('google-btn');
  let currentMode = 'login';

  // 🔍 ПРОВЕРКА: мы на странице колбэка? (?code=...)
  const urlParams = new URLSearchParams(window.location.search);
  const authCode = urlParams.get('code');
  const error = urlParams.get('error');

  if (authCode) {
    // 🔥 Мы вернулись от Google с кодом → обмениваем его на сессию
    handleGoogleCallback(authCode);
    return;  // Прекращаем дальнейшее выполнение
  }

  if (error) {
    alert(`❌ Ошибка авторизации Google: ${error}`);
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  // 🔧 Автоподстановка логина после регистрации
  const loginFromReg = urlParams.get('login');
  if (loginFromReg) {
      document.getElementById('login').value = loginFromReg;
      document.querySelector('[data-mode="login"]')?.click();
  }

  // 🔧 Переключение вкладок
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentMode = tab.dataset.mode;
      submitBtn.textContent = currentMode === 'login' ? 'Войти' : 'Зарегистрироваться';
    });
  });

  // 🔧 Универсальная отправка запроса (для POST-запросов)
  async function sendRequest(endpointKey, formData) {
    const endpoint = API_CONFIG.endpoints[endpointKey];
    if (!endpoint) {
      console.error(`❌ Эндпоинт "${endpointKey}" не найден в конфиге`);
      throw new Error(`Endpoint "${endpointKey}" not configured`);
    }

    const payload = endpoint.needs
      ? Object.fromEntries(endpoint.needs.map(key => [key, formData[key]]))
      : formData;

    return await fetch(`${API_CONFIG.BASE_URL}${endpoint.url}`, {
      method: endpoint.method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      credentials: 'include'
    });
  }

  // 🔧 Обработчик успеха (для логина/регистрации)
  function handleSuccess(data, login, mode) {
    if (mode === 'login') {
      if (data.message === "User authenticated") {
        localStorage.setItem('userLogin', data.login || login);
        window.location.href = "dashboard.html";
        return true;
      }
      if (data.message === "User does not exist") {
        alert("⚠️ У вас нет аккаунта. Пожалуйста, зарегистрируйтесь.");
        switchMode('register');
        document.getElementById('login').value = login;
        return true;
      }
    }
    if (mode === 'register') {
      alert("✅ Вы успешно зарегистрировались! Теперь войдите.");
      window.location.href = `auth.html?login=${encodeURIComponent(login)}`;
      return true;
    }
    return false;
  }

  // 🔧 Обработчик ответа от Google callback
  function handleGoogleCallbackResponse(data, login) {
    if (data.message && data.message.includes("User authenticated")) {
      localStorage.setItem('userLogin', login);
      // 🔥 Очищаем код из URL, чтобы не отправлять повторно
      window.history.replaceState({}, document.title, '/auth.html');
      window.location.href = "dashboard.html";
      return true;
    }
    return false;
  }

  // 🔧 Переключение режима
  function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-mode="${mode}"]`)?.classList.add('active');
    submitBtn.textContent = mode === 'login' ? 'Войти' : 'Зарегистрироваться';
  }

  // 🔥 Обработка колбэка от Google (обмен кода на сессию)
  async function handleGoogleCallback(code) {
    console.log('🔑 Получен код от Google, обмениваем на сессию...');

    try {
      const response = await sendRequest('googleCallback', { code });
      const data = await response.json();

      if (response.ok) {
        const handled = handleGoogleCallbackResponse(data, data.login);
        if (!handled) {
          alert(data.message || "Вход через Google выполнен");
        }
      } else {
        const errorMsg = data.detail || data.message || "Ошибка авторизации";
        alert(`❌ Ошибка ${response.status}: ${errorMsg}`);
        window.history.replaceState({}, document.title, window.location.pathname);
      }
    } catch (err) {
      console.error('❌ Ошибка обмена кода:', err);
      alert('🌐 Не удалось завершить вход через Google');
    }
  }

  // 🔥 Обработчик клика по кнопке Google (УПРОЩЁННЫЙ!)
  if (googleBtn) {
    googleBtn.addEventListener('click', () => {
      // 🔥 Просто редиректим на бэкенд, который сам вернёт 302 на Google
      // Браузер автоматически последует за редиректом'
      window.location.href = `${API_CONFIG.BASE_URL}${API_CONFIG.endpoints["googleUrl"].url}`;
    });
  }

  // 🔧 Отправка формы (логин/регистрация)
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const login = document.getElementById('login').value.trim();
    const password = document.getElementById('password').value.trim();

    if (!login || !password) {
      alert('Заполните все поля');
      return;
    }

    const endpointKey = currentMode === 'login' ? 'login' : 'registration';

    try {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Загрузка...';

      const response = await sendRequest(endpointKey, { login, password });
      const data = await response.json();

      if (response.ok) {
        const handled = handleSuccess(data, login, currentMode);
        if (!handled) {
          alert(data.message || "Запрос выполнен успешно");
        }
      } else {
        const errorMsg = data.detail || data.message || "Произошла неизвестная ошибка";
        if (response.status === 409) {
          alert('🔴 Такой аккаунт уже есть! Пожалуйста, войдите.');
          switchMode('login');
          document.getElementById('login').value = login;
        } else {
          alert(`❌ Ошибка ${response.status}: ${errorMsg}`);
        }
      }
    } catch (err) {
      console.error('❌ Ошибка fetch:', err);
      alert("🌐 Ошибка соединения с сервером. Проверьте интернет или запущен ли бэкенд.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = currentMode === 'login' ? 'Войти' : 'Зарегистрироваться';
    }
  });
});