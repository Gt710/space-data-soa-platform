# Space Data SOA Platform 🌌

**Space Data SOA Platform** — це сучасна сервіс-орієнтована платформа для збору, обробки та візуалізації космічних даних. Проект об'єднує потужність Kotlin та гнучкість Python для створення масштабованої системи мікросервісів.

## 🚀 Основні можливості
- **Satellite Tracker**: Відстеження супутників у реальному часі (Kotlin/Ktor).
- **Space Weather**: Моніторинг космічної погоди та подій NASA (Python/FastAPI).
- **Astro Objects**: База даних астероїдів та навколоземних об'єктів (Python/FastAPI).
- **Mission Data**: Дані про космічні місії та запуски.
- **Infrastructure**: Контейнеризована база даних TimescaleDB для часових рядів.

## 🛠 Технологічний стек
- **Мови**: Kotlin, Python 3.11+.
- **Фреймворки**: Ktor (Kotlin), FastAPI (Python).
- **База даних**: PostgreSQL + TimescaleDB (Docker).
- **Інструментарій**: Docker, Gradle, Virtualenv.

## 📂 Структура проекту
- `services/`: Мікросервіси системи.
- `infrastructure/`: Конфігурація Docker та бази даних.
- `frontend/`: (В розробці) Клієнтська частина.
- `wiki/`: Детальна документація з налаштування.

## 🚦 Швидкий старт

### 1. Підготовка інфраструктури
Переконайтеся, що у вас встановлений Docker, та запустіть базу даних:
```bash
cd infrastructure
docker-compose up -d
```

### 2. Налаштування змінних оточення
Створіть файл `.env` у корені (або скопіюйте в кожен сервіс) з наступними ключами:
```env
NASA_API_KEY=ваш_ключ
SPACE_TRACK_USER=ваш_email
SPACE_TRACK_PASSWORD=ваш_пароль
```

### 3. Запуск сервісів

#### Kotlin (Satellite Tracker):
```powershell
cd services/satellite-tracker
.\gradlew.bat run
```

#### Python (наприклад, Space Weather):
```powershell
cd services/space-weather
.\venv\Scripts\activate
uvicorn main:app --reload --port 8001
```

### 📡 Тестування API
- **Space Weather (8001)**:
    - `GET /`: Статус сервісу.
    - `GET /nasa-test`: Тестовий запит до NASA API та збереження в БД.
    - `GET /events`: Список всіх збережених подій.
- **Satellite Tracker (8080)**:
    - `GET /`: Статус сервісу.
    - `GET /satellites`: Список супутників з БД.
    - `GET /add-test`: Додавання тестового супутника (ISS).

## 📝 Документація
Детальні інструкції з розгортання та розробки можна знайти у папці [wiki/](./wiki/Development%20Setup.md).

---
*Розроблено для ентузіастів космосу та SOA архітектури.*
