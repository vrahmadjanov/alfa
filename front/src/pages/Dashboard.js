import React, { useEffect, useState } from 'react';
import { fetchBusinesses, createBusiness } from '../api/business';
import './Dashboard.css';

function Dashboard() {
  const [businesses, setBusinesses] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errors, setErrors] = useState({});
  const [createForm, setCreateForm] = useState({
    name: '',
    business_type: 'cafe',
    city: '',
    description: ''
  });

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

  const handleCreateChange = (e) => {
    const { name, value } = e.target;
    setCreateForm((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setErrors({});

    try {
      const created = await createBusiness(createForm);
      setBusinesses((prev) => [created, ...prev]);
      setCreateForm({
        name: '',
        business_type: 'cafe',
        city: '',
        description: ''
      });
    } catch (apiErrors) {
      setErrors(apiErrors);
    }
  };

  return (
    <div className="dashboard-main">
        <section className="dashboard-column dashboard-column-left">
          <h2 className="dashboard-section-title">Создать бизнес</h2>
          <form className="dashboard-form" onSubmit={handleCreateSubmit}>
            {errors.general && (
              <div className="dashboard-error">
                {errors.general}
              </div>
            )}
            <div className="form-group">
              <label htmlFor="name">Название бизнеса</label>
              <input
                id="name"
                name="name"
                type="text"
                value={createForm.name}
                onChange={handleCreateChange}
                placeholder="Кофейня Эспрессо"
                required
              />
              {errors.name && <span className="error-text">{errors.name}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="business_type">Тип бизнеса</label>
              <select
                id="business_type"
                name="business_type"
                value={createForm.business_type}
                onChange={handleCreateChange}
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
              <label htmlFor="city">Город</label>
              <input
                id="city"
                name="city"
                type="text"
                value={createForm.city}
                onChange={handleCreateChange}
                placeholder="Москва"
              />
            </div>
            <div className="form-group">
              <label htmlFor="description">Краткое описание</label>
              <textarea
                id="description"
                name="description"
                rows="3"
                value={createForm.description}
                onChange={handleCreateChange}
                placeholder="Уютная кофейня рядом с офисным кварталом"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block">
              Создать бизнес
            </button>
          </form>
        </section>

        <section className="dashboard-column dashboard-column-right">
          <h2 className="dashboard-section-title">Ваши бизнесы</h2>
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
                </article>
              ))}
            </div>
          )}
        </section>
    </div>
  );
}

export default Dashboard;


