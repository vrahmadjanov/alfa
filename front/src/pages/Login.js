import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginRequest } from '../api/auth';
import heroImage from '../assets/images/hero.jpeg';
import './Auth.css';

function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    try {
      await loginRequest(formData);
      setIsLoading(false);
      navigate('/dashboard');
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
          <h2 className="auth-title">Вход в систему</h2>
          <p className="auth-subtitle">
            Добро пожаловать! Войдите в свой аккаунт
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
          </div>

          <div className="form-footer">
            <label className="checkbox-label">
              <input type="checkbox" />
              <span>Запомнить меня</span>
            </label>
            <Link to="/forgot-password" className="link">
              Забыли пароль?
            </Link>
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={isLoading}
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Нет аккаунта?{' '}
            <Link to="/register" className="link">
              Зарегистрироваться
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

export default Login;

