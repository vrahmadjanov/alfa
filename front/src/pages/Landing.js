import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiEdit3, FiShield, FiShare2, FiFileText } from 'react-icons/fi';
import { FaGithub } from 'react-icons/fa';
import heroImage from '../assets/images/hero.jpeg';
import './Landing.css';

function Landing() {
  const navigate = useNavigate();

  // Динамическая "печать" текста проблем владельца бизнеса
  const problemLines = [
    '09:02  Клиент пишет в WhatsApp: "Кофе был холодным, верните деньги".',
    '09:05  Поставщик просит подтвердить новый прайс и объем поставки.',
    '09:11  Приходит письмо из налоговой: нужен пояснительный ответ за 3 дня.',
    '09:18  Бариста спрашивает, можно ли поменять смены на выходных.',
    '09:25  Вы вспоминаете, что в будние дни снова пустой зал до обеда.',
    '',
    'Вопрос: где взять время и экспертизу, чтобы на всё ответить правильно?'
  ];

  const fullProblemText = problemLines.join('\n');
  const [typedProblemText, setTypedProblemText] = useState('');

  useEffect(() => {
    let index = 0;
    const speed = 25; // скорость "печати" в мс на символ

    const interval = setInterval(() => {
      index += 1;
      setTypedProblemText(fullProblemText.slice(0, index));

      if (index >= fullProblemText.length) {
        clearInterval(interval);
      }
    }, speed);

    return () => clearInterval(interval);
  }, [fullProblemText]);

  const heroStyle = {
    backgroundImage: `linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.75) 100%), url(${heroImage})`
  };

  return (
    <div className="landing">
      {/* Hero Section */}
      <header id="top" className="hero" style={heroStyle}>
        <div className="hero-content">
          <h1 className="hero-title">
            <span className="hero-brand">Alfa</span>{' '}
            <span className="highlight">Бизнес Ассистент</span>
          </h1>
          <p className="hero-subtitle">
            Умный карманный советник для владельца малого бизнеса
          </p>
          <p className="hero-description">
            Получайте профессиональные советы по маркетингу, финансам, юридическим вопросам 
            и управлению персоналом прямо здесь и сейчас — без консультантов и траты часов на поиск
          </p>
          <div className="hero-buttons">
            <button 
              className="btn btn-primary btn-lg"
              onClick={() => navigate('/register')}
            >
              Начать бесплатно
            </button>
            <button 
              className="btn btn-secondary btn-lg"
              onClick={() => navigate('/login')}
            >
              Войти
            </button>
          </div>
        </div>
      </header>

      {/* Problem Section */}
      <section id="problem" className="section problem-section">
        <div className="container">
          <h2 className="section-title">Один обычный день владельца бизнеса</h2>
          <div className="problem-terminal">
            <div className="problem-terminal-header">
              <span className="problem-dot problem-dot--red" />
              <span className="problem-dot problem-dot--yellow" />
              <span className="problem-dot problem-dot--green" />
              <span className="problem-terminal-title">coffeeshop.log</span>
            </div>
            <pre className="problem-terminal-body">
              {typedProblemText}
              <span className="problem-caret">▋</span>
            </pre>
            <p className="problem-terminal-footer">
              Alfa не заменит людей, но поможет вам отвечать на такие запросы быстро и по делу — как если бы у вас был свой юрист, маркетолог и финансист.
            </p>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section id="solution" className="section solution-section">
        <div className="container">
          <h2 className="section-title">Решение: Alfa Ассистент</h2>
          <p className="section-subtitle">
            Представьте: вы в кофейне, между клиентами достаете телефон и за 2 минуты:
          </p>
          <div className="solutions-grid">
            <div className="solution-card">
              <div className="solution-icon solution-icon--answer">
                <FiEdit3 />
              </div>
              <h3>Получаете готовый ответ</h3>
              <p>Профессиональный текст для поставщика с учетом контекста вашего бизнеса</p>
            </div>
            <div className="solution-card">
              <div className="solution-icon solution-icon--legal">
                <FiShield />
              </div>
              <h3>Юридическая помощь</h3>
              <p>Узнаете как правильно ответить налоговой со ссылками на законы</p>
            </div>
            <div className="solution-card">
              <div className="solution-icon solution-icon--social">
                <FiShare2 />
              </div>
              <h3>Контент для соцсетей</h3>
              <p>Генерируете пост для соцсетей про акцию под вашу аудиторию</p>
            </div>
            <div className="solution-card">
              <div className="solution-icon solution-icon--docs">
                <FiFileText />
              </div>
              <h3>Документы и шаблоны</h3>
              <p>Получаете шаблон трудового договора для нового сотрудника</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="why-alfa" className="section features-section">
        <div className="container">
          <h2 className="section-title">Почему Alfa?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-number">1</div>
              <h3>В контексте вашего бизнеса</h3>
              <p>Помнит, что у вас кофейня "Эспрессо" на Пушкина, 5</p>
              <p>Знает ваш средний чек (350₽), количество клиентов (80/день)</p>
              <p>Учитывает прошлые акции, которые сработали/не сработали</p>
            </div>
            <div className="feature-card">
              <div className="feature-number">2</div>
              <h3>Говорит на языке бизнеса</h3>
              <p>Не абстрактные советы, а конкретика:</p>
              <p className="feature-example">
                "Добавьте QR-код на чеки для отзывов. Каждый 10-й отзыв = бесплатный кофе"
              </p>
            </div>
            <div className="feature-card">
              <div className="feature-number">3</div>
              <h3>Учится на вашем опыте</h3>
              <p>Запоминает что сработало, что нет</p>
              <p>Адаптирует советы под специфику бизнеса</p>
              <p>Предупреждает о повторяющихся ошибках</p>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section id="use-cases" className="section use-cases-section">
        <div className="container">
          <h2 className="section-title">Реальные сценарии использования</h2>
          <div className="use-cases">
            <div className="use-case">
              <div className="use-case-header">
                <span className="use-case-badge">Маркетинг</span>
                <h3>Привлечь клиентов в мертвые дни</h3>
              </div>
              <div className="use-case-dialog">
                <div className="message user">
                  <strong>Вы:</strong> Понедельник-среда пусто. Что делать?
                </div>
                <div className="message assistant">
                  <strong>Alfa:</strong> Анализирую ваши данные:<br/>
                  - Пн-Ср: 45 клиентов/день (vs 80 в Пт-Вс)<br/>
                  - Основная аудитория: офисные 25-35 лет<br/><br/>
                  
                  <strong>Предлагаю акцию 'Кофе-брейк по средам':</strong><br/>
                  1. Бизнес-ланч: кофе + десерт = 400₽ (экономия 100₽)<br/>
                  2. Таргет в Instagram на офисы в радиусе 500м<br/>
                  3. Текст: 'Среда — маленькая пятница'<br/><br/>
                  
                  Прогноз: +20-30 клиентов/день = +7,000-10,000₽ дополнительно в неделю
                </div>
              </div>
            </div>

            <div className="use-case">
              <div className="use-case-header">
                <span className="use-case-badge legal">Юридические вопросы</span>
                <h3>Конфликт с клиентом</h3>
              </div>
              <div className="use-case-dialog">
                <div className="message user">
                  <strong>Вы:</strong> Клиент требует возврат за "остывший кофе"
                </div>
                <div className="message assistant">
                  <strong>Alfa:</strong> По закону о ЗПП (ст. 25), возврат продуктов питания 
                  после их использования не предусмотрен.<br/><br/>
                  
                  Однако для сохранения репутации:<br/><br/>
                  
                  <strong>Вариант 1 (мягкий):</strong> Предложите заменить кофе бесплатно<br/>
                  <strong>Вариант 2 (жесткий):</strong> 'К сожалению, по законодательству РФ...'<br/><br/>
                  
                  Рекомендую вариант 1 - вы потеряете 150₽, но сохраните клиента.
                </div>
              </div>
            </div>

            <div className="use-case">
              <div className="use-case-header">
                <span className="use-case-badge finance">Финансы</span>
                <h3>Проверка здоровья бизнеса</h3>
              </div>
              <div className="use-case-dialog">
                <div className="message user">
                  <strong>Вы:</strong> Все норм с деньгами?
                </div>
                <div className="message assistant">
                  <strong>Alfa:</strong> Анализирую ваши данные за 3 месяца:<br/><br/>
                  
                  <strong>Выручка:</strong><br/>
                  - Сентябрь: 420,000₽<br/>
                  - Октябрь: 460,000₽ (+9.5%)<br/>
                  - Ноябрь: 440,000₽ (-4.3%)<br/><br/>
                  
                  <strong className="warning">ВНИМАНИЕ:</strong><br/>
                  - Расходы выросли на 12% (из-за нового баристы)<br/>
                  - Прибыль упала с 120к до 95к<br/><br/>
                  
                  <strong>Рекомендации:</strong><br/>
                  1. Сократите закупки сиропов на 15% (продается плохо)<br/>
                  2. Поднимите цену на капучино до 200₽ (сейчас 180₽)<br/>
                  3. Запустите программу лояльности<br/><br/>
                  
                  Прогноз: +25,000₽ чистой прибыли к январю
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA / About Project Section */}
      <section id="about-project" className="section cta-section">
        <div className="container">
          <h2 className="cta-title">Зачем был сделан этот проект</h2>
          <p className="cta-subtitle">
            Alfa Бизнес Ассистент родился как ответ на задачу хакатона: помочь владельцу малого бизнеса
            получить быстрые и осмысленные решения вместо бесконечных поисков и разрозненных советов.
          </p>

          <div className="hackathon-grid">
            <div className="hackathon-card">
              <h3>Фокус на владельце бизнеса</h3>
              <p>
                В TASK.md было отдельно подчеркнуто: продукт делается для человека, который совмещает роли
                директора, маркетолога, финансового и HR-менеджера одновременно.
              </p>
              <ul>
                <li>понятный onboarding и авторизация</li>
                <li>простое управление своим бизнесом</li>
                <li>минимум «айтишных» терминов в интерфейсе</li>
              </ul>
            </div>

            <div className="hackathon-card">
              <h3>Ключевые части TASK.md</h3>
              <ul>
                <li>API аутентификации на JWT с кастомным пользователем</li>
                <li>CRUD для бизнесов владельца (мульти-бизнес)</li>
                <li>Чат с AI-помощником, учитывающим контекст бизнеса</li>
                <li>Интеграция с LLM через OpenRouter и fallback по моделям</li>
                <li>Документация и тесты для основных сценариев</li>
              </ul>
            </div>

            <div className="hackathon-card">
              <h3>Что реализовано в этой версии</h3>
              <ul>
                <li>единый API с стандартизированными ответами</li>
                <li>многошаговый чат с историей и категорией диалога</li>
                <li>fallback по нескольким бесплатным LLM для устойчивости</li>
                <li>первый фронтенд: лендинг, регистрация и логин</li>
              </ul>
            </div>

            <div className="hackathon-card">
              <h3>Что можно развивать дальше</h3>
              <ul>
                <li>личный кабинет с аналитикой по бизнесам</li>
                <li>визуализация показателей выручки и прибыли</li>
                <li>шаблоны готовых сценариев (маркетинг, финансы, HR)</li>
                <li>поддержка командной работы внутри бизнеса</li>
              </ul>
            </div>
          </div>

          <div className="hackathon-actions">
            <button
              className="btn github-btn"
              onClick={() =>
                window.open('https://github.com/vrahmadjanov/alfa', '_blank', 'noreferrer')
              }
            >
              <FaGithub className="github-icon" />
              <span>На GitHub</span>
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <h3>Alfa Business Assistant</h3>
              <p>AI-помощник для владельцев малого бизнеса</p>
            </div>
            <div className="footer-section">
              <h4>Навигация</h4>
              <ul>
                <li><a href="#top">Главная</a></li>
                <li><a href="#problem">Проблема</a></li>
                <li><a href="#solution">Решение</a></li>
                <li><a href="#why-alfa">Почему Alfa</a></li>
                <li><a href="#use-cases">Кейсы</a></li>
                <li><a href="#about-project">О проекте</a></li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Исходный код</h4>
              <ul>
                <li>
                  <a
                    href="https://github.com/vrahmadjanov/alfa"
                    target="_blank"
                    rel="noreferrer"
                  >
                    github.com/vrahmadjanov/alfa
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 Альфа Хак. Права не защищены.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Landing;

