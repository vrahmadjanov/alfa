import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchBusinesses, updateBusiness, archiveBusiness } from '../api/business';
import Chat from '../components/Chat';
import Modal from '../components/Modal';
import { 
  IoChatbubblesOutline, 
  IoMailOutline, 
  IoSparklesOutline, 
  IoTimeOutline,
  IoLocationOutline,
  IoBusinessOutline,
  IoCalendarOutline,
  IoPersonOutline,
  IoPeopleOutline,
  IoCreateOutline,
  IoTrashOutline
} from 'react-icons/io5';
import './Business.css';

function Business() {
  const { businessId } = useParams();
  const navigate = useNavigate();
  const [business, setBusiness] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isArchiveModalOpen, setIsArchiveModalOpen] = useState(false);

  useEffect(() => {
    loadBusiness();
  }, [businessId]);

  const loadBusiness = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const allBusinesses = await fetchBusinesses();
      setBusinesses(allBusinesses);
      
      const foundBusiness = allBusinesses.find(b => b.id === parseInt(businessId, 10));
      
      if (!foundBusiness) {
        setError('Бизнес не найден');
      } else {
        setBusiness(foundBusiness);
      }
    } catch (err) {
      setError('Ошибка при загрузке данных бизнеса');
      console.error('Error loading business:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleConversationCreated = (conversation) => {
    setCurrentConversation(conversation?.id || null);
  };

  const handleArchive = async () => {
    try {
      await archiveBusiness(businessId);
      navigate('/dashboard');
    } catch (error) {
      console.error('Error archiving business:', error);
      alert('Ошибка при архивировании бизнеса');
    }
  };

  const handleUpdate = async (formData) => {
    try {
      const updatedBusiness = await updateBusiness(businessId, formData);
      setBusiness(updatedBusiness);
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Error updating business:', error);
      alert('Ошибка при обновлении бизнеса');
    }
  };

  if (isLoading) {
    return (
      <div className="business-page">
        <div className="business-loading">Загрузка...</div>
      </div>
    );
  }

  if (error || !business) {
    return (
      <div className="business-page">
        <div className="business-error">
          <h2>{error || 'Бизнес не найден'}</h2>
          <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
            Вернуться к дашборду
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="business-page">
      <div className="business-main">
        <section className="business-column business-column-left">
          <Chat 
            businesses={businesses}
            currentConversation={currentConversation}
            onConversationCreated={handleConversationCreated}
            initialBusinessId={business.id}
          />
        </section>

        <section className="business-column business-column-right">
          <div className="business-info-card">
            <div className="business-card-header">
              <h2 className="business-card-title">Основная информация</h2>
              <span className={`business-badge business-badge--${business.status}`}>
                {business.status === 'active' ? 'Активен' : 'Неактивен'}
              </span>
            </div>
            
            <div className="business-info-grid">
              <div className="business-info-item">
                <div className="business-info-icon">
                  <IoBusinessOutline />
                </div>
                <div className="business-info-content">
                  <span className="business-info-label">Тип бизнеса</span>
                  <span className="business-info-value">{getBusinessTypeName(business.business_type)}</span>
                </div>
              </div>

              {business.city && (
                <div className="business-info-item">
                  <div className="business-info-icon">
                    <IoLocationOutline />
                  </div>
                  <div className="business-info-content">
                    <span className="business-info-label">Город</span>
                    <span className="business-info-value">{business.city}</span>
                  </div>
                </div>
              )}

              {business.owner_name && (
                <div className="business-info-item">
                  <div className="business-info-icon">
                    <IoPersonOutline />
                  </div>
                  <div className="business-info-content">
                    <span className="business-info-label">Владелец</span>
                    <span className="business-info-value">{business.owner_name}</span>
                  </div>
                </div>
              )}

              {business.profile?.employees_count && (
                <div className="business-info-item">
                  <div className="business-info-icon">
                    <IoPeopleOutline />
                  </div>
                  <div className="business-info-content">
                    <span className="business-info-label">Сотрудников</span>
                    <span className="business-info-value">{business.profile.employees_count}</span>
                  </div>
                </div>
              )}

              {business.email && (
                <div className="business-info-item">
                  <div className="business-info-icon">
                    <IoMailOutline />
                  </div>
                  <div className="business-info-content">
                    <span className="business-info-label">Email</span>
                    <span className="business-info-value">{business.email}</span>
                  </div>
                </div>
              )}

              <div className="business-info-item">
                <div className="business-info-icon">
                  <IoCalendarOutline />
                </div>
                <div className="business-info-content">
                  <span className="business-info-label">Создан</span>
                  <span className="business-info-value">
                    {new Date(business.created_at).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric'
                    })}
                  </span>
                </div>
              </div>
            </div>

            {business.description && (
              <div className="business-description-section">
                <h3 className="business-description-title">Описание</h3>
                <p className="business-description">{business.description}</p>
              </div>
            )}

            <div className="business-actions">
              <button 
                className="btn btn-primary"
                onClick={() => setIsEditModalOpen(true)}
              >
                <IoCreateOutline />
                <span>Редактировать</span>
              </button>
              <button 
                className="btn btn-danger"
                onClick={() => setIsArchiveModalOpen(true)}
              >
                <IoTrashOutline />
                <span>Архивировать</span>
              </button>
            </div>
          </div>
        </section>
      </div>

      <div className="business-analytics">
        <h2 className="business-section-title">Статистика и показатели</h2>
        <div className="business-stats">
          <div className="business-stat-card">
            <div className="business-stat-icon">
              <IoChatbubblesOutline />
            </div>
            <div className="business-stat-content">
              <span className="business-stat-label">Диалогов</span>
              <span className="business-stat-value">0</span>
            </div>
          </div>
          <div className="business-stat-card">
            <div className="business-stat-icon">
              <IoMailOutline />
            </div>
            <div className="business-stat-content">
              <span className="business-stat-label">Сообщений</span>
              <span className="business-stat-value">0</span>
            </div>
          </div>
          <div className="business-stat-card">
            <div className="business-stat-icon">
              <IoSparklesOutline />
            </div>
            <div className="business-stat-content">
              <span className="business-stat-label">Токенов использовано</span>
              <span className="business-stat-value">0</span>
            </div>
          </div>
          <div className="business-stat-card">
            <div className="business-stat-icon">
              <IoTimeOutline />
            </div>
            <div className="business-stat-content">
              <span className="business-stat-label">Последняя активность</span>
              <span className="business-stat-value business-stat-value--small">Нет данных</span>
            </div>
          </div>
        </div>
      </div>

      {/* Модальное окно редактирования */}
      {isEditModalOpen && (
        <EditBusinessModal
          business={business}
          onClose={() => setIsEditModalOpen(false)}
          onUpdate={handleUpdate}
        />
      )}

      {/* Модальное окно подтверждения архивирования */}
      {isArchiveModalOpen && (
        <ArchiveConfirmModal
          businessName={business.name}
          onClose={() => setIsArchiveModalOpen(false)}
          onConfirm={handleArchive}
        />
      )}
    </div>
  );
}

// Модальное окно для редактирования бизнеса
function EditBusinessModal({ business, onClose, onUpdate }) {
  const [formData, setFormData] = useState({
    name: business.name || '',
    business_type: business.business_type || '',
    city: business.city || '',
    email: business.email || '',
    description: business.description || ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onUpdate(formData);
  };

  const modalFooter = (
    <>
      <button type="button" className="btn btn-secondary" onClick={onClose}>
        Отмена
      </button>
      <button type="submit" form="edit-business-form" className="btn btn-primary">
        Сохранить
      </button>
    </>
  );

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Редактировать бизнес"
      size="medium"
      footer={modalFooter}
    >
      <form id="edit-business-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Название *</label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>

        <div className="form-group">
          <label>Тип бизнеса *</label>
          <select
            value={formData.business_type}
            onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
            required
          >
            <option value="cafe">Кафе / Кофейня</option>
            <option value="restaurant">Ресторан</option>
            <option value="beauty_salon">Салон красоты</option>
            <option value="barbershop">Барбершоп</option>
            <option value="retail">Магазин</option>
            <option value="fitness">Фитнес / Спорт</option>
            <option value="services">Услуги</option>
            <option value="other">Другое</option>
          </select>
        </div>

        <div className="form-group">
          <label>Город</label>
          <input
            type="text"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
        </div>

        <div className="form-group">
          <label>Описание</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows="4"
          />
        </div>
      </form>
    </Modal>
  );
}

// Модальное окно подтверждения архивирования
function ArchiveConfirmModal({ businessName, onClose, onConfirm }) {
  const modalFooter = (
    <>
      <button className="btn btn-secondary" onClick={onClose}>
        Отмена
      </button>
      <button className="btn btn-danger" onClick={onConfirm}>
        Архивировать
      </button>
    </>
  );

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title="Подтвердите архивирование"
      size="small"
      footer={modalFooter}
    >
      <div className="modal-content-text">
        <p>Вы уверены, что хотите архивировать бизнес <strong>"{businessName}"</strong>?</p>
        <p className="modal-warning">Архивированный бизнес можно будет восстановить позже.</p>
      </div>
    </Modal>
  );
}

function getBusinessTypeName(type) {
  const types = {
    cafe: 'Кафе',
    restaurant: 'Ресторан',
    shop: 'Магазин',
    service: 'Услуги',
    online: 'Онлайн-бизнес',
    other: 'Другое'
  };
  return types[type] || type;
}

export default Business;

