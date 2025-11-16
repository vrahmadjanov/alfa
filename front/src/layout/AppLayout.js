import React, { useState, useMemo } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import './AppLayout.css';

function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const currentUser = useMemo(() => {
    try {
      const raw = localStorage.getItem('current_user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    navigate('/login');
  };

  const navItems = [
    { label: 'Мои бизнесы', to: '/dashboard' }
    // В дальнейшем сюда добавятся чат, настройки и др.
  ];

  const pageTitle = useMemo(() => {
    if (location.pathname.startsWith('/dashboard')) {
      return 'Мои бизнесы';
    }
    return 'Alfa Бизнес ассистент';
  }, [location.pathname]);

  const handleBackdropClick = (e) => {
    // Закрываем меню только если клик был по backdrop, а не по самому меню
    if (e.target === e.currentTarget) {
      setSidebarOpen(false);
    }
  };

  return (
    <div className="app-shell">
      <aside 
        className={`app-sidebar ${sidebarOpen ? 'app-sidebar--open' : ''}`}
        onClick={handleBackdropClick}
      >
        <div className="app-sidebar-content">
          <div className="app-sidebar-header">
            <span className="app-sidebar-header-logo" onClick={() => navigate('/')}>Alfa</span>
            <button 
              className="app-sidebar-close"
              onClick={() => setSidebarOpen(false)}
              aria-label="Закрыть меню"
            >
              <span />
              <span />
            </button>
          </div>
        <nav className="app-sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `app-sidebar-link ${isActive ? 'app-sidebar-link--active' : ''}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

          <div className="app-sidebar-footer">
            {currentUser?.email && (
              <div className="app-sidebar-user">
                <span className="app-sidebar-user-label">Аккаунт</span>
                <span className="app-sidebar-user-email">{currentUser.email}</span>
              </div>
            )}
            <button className="btn btn-secondary app-sidebar-logout" onClick={handleLogout}>
              Выйти
            </button>
          </div>
        </div>
      </aside>

      <div className="app-main">
        <header className="app-header">
          <div className="app-header-title">
            <h1>{pageTitle}</h1>
          </div>
          <button
            className={`app-header-burger ${sidebarOpen ? 'app-header-burger--open' : ''}`}
            onClick={() => setSidebarOpen((open) => !open)}
            aria-label={sidebarOpen ? "Закрыть меню" : "Открыть меню"}
          >
            <span />
            <span />
            <span />
          </button>
        </header>

        <main className="app-content">
          {children}
        </main>
      </div>
    </div>
  );
}

export default AppLayout;


