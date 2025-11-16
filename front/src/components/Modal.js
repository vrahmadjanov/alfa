import React from 'react';
import { IoCloseOutline } from 'react-icons/io5';
import './Modal.css';

/**
 * Базовый компонент модального окна
 * @param {boolean} isOpen - Управление видимостью модального окна
 * @param {function} onClose - Функция закрытия модального окна
 * @param {string} title - Заголовок модального окна
 * @param {ReactNode} children - Содержимое модального окна
 * @param {ReactNode} footer - Кнопки действий (опционально)
 * @param {string} size - Размер модального окна: 'small', 'medium', 'large'
 */
function Modal({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  footer,
  size = 'medium' 
}) {
  if (!isOpen) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="modal-overlay" onClick={handleBackdropClick}>
      <div 
        className={`modal-container modal-container--${size}`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h2 className="modal-title">{title}</h2>
          <button 
            className="modal-close" 
            onClick={onClose}
            aria-label="Закрыть"
          >
            <IoCloseOutline />
          </button>
        </div>

        <div className="modal-body">
          {children}
        </div>

        {footer && (
          <div className="modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

export default Modal;

