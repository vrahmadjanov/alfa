import React, { useState, useMemo, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { fetchBusinesses } from '../api/business';
import './AppLayout.css';

function AppLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [businesses, setBusinesses] = useState([]);
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

  useEffect(() => {
    loadBusinesses();
  }, []);

  const loadBusinesses = async () => {
    try {
      const data = await fetchBusinesses();
      setBusinesses(data || []);
    } catch (error) {
      console.error('Error loading businesses:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_user');
    navigate('/login');
  };

  const navItems = [
    { label: 'Главная', to: '/dashboard' }
    // В дальнейшем сюда добавятся чат, настройки и др.
  ];

  const pageTitle = useMemo(() => {
    if (location.pathname.startsWith('/dashboard')) {
      return 'Главная';
    }
    if (location.pathname.startsWith('/business/')) {
      const businessId = parseInt(location.pathname.split('/')[2], 10);
      const business = businesses.find(b => b.id === businessId);
      return business ? business.name : 'Бизнес';
    }
    return 'Alfa Бизнес ассистент';
  }, [location.pathname, businesses]);

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
          
          {businesses.length > 0 && (
            <>
              <div className="app-sidebar-divider" />
              <div className="app-sidebar-section-title">Ваши бизнесы</div>
              {businesses.map((business) => (
                <NavLink
                  key={business.id}
                  to={`/business/${business.id}`}
                  className={({ isActive }) =>
                    `app-sidebar-link app-sidebar-link--business ${isActive ? 'app-sidebar-link--active' : ''}`
                  }
                  onClick={() => setSidebarOpen(false)}
                >
                  {business.name}
                </NavLink>
              ))}
            </>
          )}
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


