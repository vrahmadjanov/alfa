import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchBusinesses, createBusiness } from '../api/business';
import Chat from '../components/Chat';
import BusinessModal from '../components/BusinessModal';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [businesses, setBusinesses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errors, setErrors] = useState({});
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentConversation, setCurrentConversation] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchBusinesses();
        setBusinesses(data);
        setIsLoading(false);
      } catch (apiErrors) {
        setErrors(apiErrors);
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const handleCreateBusiness = async (formData) => {
    try {
      const created = await createBusiness(formData);
      setBusinesses((prev) => [created, ...prev]);
      setIsModalOpen(false);
    } catch (apiErrors) {
      throw apiErrors;
    }
  };

  const handleConversationCreated = (conversation) => {
    setCurrentConversation(conversation.id);
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-main">
          <section className="dashboard-column dashboard-column-left">
            <Chat 
              businesses={businesses}
              currentConversation={currentConversation}
              onConversationCreated={handleConversationCreated}
            />
          </section>

          <section className="dashboard-column dashboard-column-right">
            <div className="dashboard-section-header">
            <h2 className="dashboard-section-title">Ваши бизнесы</h2>
              <button 
                className="btn-icon btn-icon-primary"
                onClick={() => setIsModalOpen(true)}
                aria-label="Добавить бизнес"
                title="Добавить бизнес"
              >
                +
              </button>
            </div>
            {isLoading ? (
              <p className="dashboard-muted">Загрузка бизнесов...</p>
            ) : businesses.length === 0 ? (
              <p className="dashboard-muted">
                У вас пока нет бизнесов. Создайте первый, чтобы AI ассистент понимал контекст.
              </p>
            ) : (
              <div className="business-list">
                {businesses.map((biz) => (
                  <article key={biz.id} className="business-card">
                    <div className="business-card-header">
                      <h3>{biz.name}</h3>
                      <span className={`business-status business-status--${biz.status || 'active'}`}>
                        {biz.status === 'archived'
                          ? 'Архивирован'
                          : biz.status === 'inactive'
                          ? 'Неактивен'
                          : 'Активен'}
                      </span>
                    </div>
                    <p className="business-type">
                      {biz.business_type === 'cafe' && 'Кафе / Кофейня'}
                      {biz.business_type === 'restaurant' && 'Ресторан'}
                      {biz.business_type === 'beauty_salon' && 'Салон красоты'}
                      {biz.business_type === 'barbershop' && 'Барбершоп'}
                      {biz.business_type === 'retail' && 'Магазин'}
                      {biz.business_type === 'fitness' && 'Фитнес / Спорт'}
                      {biz.business_type === 'services' && 'Услуги'}
                      {biz.business_type === 'other' && 'Другое'}
                    </p>
                    {biz.city && (
                      <p className="business-city">
                        Город: <span>{biz.city}</span>
                      </p>
                    )}
                    {biz.description && (
                      <p className="business-description">{biz.description}</p>
                    )}
                    <button 
                      className="btn btn-primary btn-sm business-card-button"
                      onClick={() => navigate(`/business/${biz.id}`)}
                    >
                      Перейти
                    </button>
                  </article>
                ))}
              </div>
            )}
          </section>

          <BusinessModal
            isOpen={isModalOpen}
            onClose={() => setIsModalOpen(false)}
            onCreate={handleCreateBusiness}
            errors={errors}
          />
      </div>
    </div>
  );
}

export default Dashboard;


