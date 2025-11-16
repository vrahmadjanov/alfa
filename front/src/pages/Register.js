import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import heroImage from '../assets/images/hero.jpeg';
import './Auth.css';
import { registerRequest } from '../api/auth';

function Register() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Введите корректный email';
    }

    if (!formData.password) {
      newErrors.password = 'Пароль обязателен';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Пароль должен содержать минимум 8 символов';
    }

    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Пароли не совпадают';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      await registerRequest({
        email: formData.email,
        password: formData.password,
        password_confirm: formData.password_confirm
      });
      setIsLoading(false);
      navigate('/login');
    } catch (apiErrors) {
      setIsLoading(false);
      setErrors(apiErrors);
    }
  };

  const authBackgroundStyle = {
    backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.85) 100%), url(${heroImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center center',
    backgroundRepeat: 'no-repeat'
  };

  return (
    <div className="auth-page" style={authBackgroundStyle}>
      <div className="auth-container">
        <div className="auth-header">
          <h2 className="auth-title">Создать аккаунт</h2>
          <p className="auth-subtitle">
            Начните использовать AI-помощника уже сегодня
          </p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          {errors.general && (
            <div className="error-message general-error">
              {errors.general}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your@email.com"
              className={errors.email ? 'error' : ''}
              required
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
              className={errors.password ? 'error' : ''}
              required
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
            <div className="input-hint">
              Минимум 8 символов, включая буквы, цифры и спецсимволы
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="password_confirm">Подтвердите пароль</label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              placeholder="••••••••"
              className={errors.password_confirm ? 'error' : ''}
              required
            />
            {errors.password_confirm && (
              <span className="error-text">{errors.password_confirm}</span>
            )}
          </div>

          <div className="form-footer">
            <label className="checkbox-label">
              <input type="checkbox" required />
              <span>
                Я согласен с{' '}
                <a href="/terms" className="link">
                  условиями использования
                </a>{' '}
                и{' '}
                <a href="/privacy" className="link">
                  политикой конфиденциальности
                </a>
              </span>
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={isLoading}
          >
            {isLoading ? 'Регистрация...' : 'Создать аккаунт'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Уже есть аккаунт?{' '}
            <Link to="/login" className="link">
              Войти
            </Link>
          </p>
          <Link to="/" className="link">
            ← Вернуться на главную
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;

