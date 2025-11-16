import React, { useState } from 'react';
import Modal from './Modal';
import './BusinessModal.css';

function BusinessModal({ isOpen, onClose, onCreate, errors: externalErrors }) {
  const [formData, setFormData] = useState({
    name: '',
    business_type: 'cafe',
    city: '',
    description: ''
  });
  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    
    try {
      await onCreate(formData);
      // Очищаем форму после успешного создания
      setFormData({
        name: '',
        business_type: 'cafe',
        city: '',
        description: ''
      });
      onClose();
    } catch (apiErrors) {
      setErrors(apiErrors);
    }
  };

  const modalFooter = (
    <>
      <button type="button" className="btn btn-secondary" onClick={onClose}>
        Отмена
      </button>
      <button type="submit" form="business-form" className="btn btn-primary">
        Создать бизнес
      </button>
    </>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Создать бизнес"
      size="medium"
      footer={modalFooter}
    >
      <form id="business-form" onSubmit={handleSubmit}>
        {(errors.general || externalErrors?.general) && (
          <div className="modal-error">
            {errors.general || externalErrors.general}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="name">Название бизнеса</label>
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
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
            value={formData.business_type}
            onChange={handleChange}
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
            value={formData.city}
            onChange={handleChange}
            placeholder="Москва"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Краткое описание</label>
          <textarea
            id="description"
            name="description"
            rows="3"
            value={formData.description}
            onChange={handleChange}
            placeholder="Уютная кофейня рядом с офисным кварталом"
          />
        </div>
      </form>
    </Modal>
  );
}

export default BusinessModal;

