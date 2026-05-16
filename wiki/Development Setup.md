# Інструкція з підготовки середовища розробки: Space Data SOA Platform

Цей документ допоможе вам налаштувати проект з нуля, враховуючи сервіс-орієнтовану архітектуру (SOA) та використання Python і Kotlin.

## 1. Системні вимоги (Що потрібно встановити)

Оскільки проект використовує різні технології, вам знадобляться наступні інструменти:

### Основні інструменти:
*   **Git**: Для керування версіями. [Завантажити](https://git-scm.com/)
*   **Docker & Docker Desktop**: Обов'язково для запуску баз даних та контейнеризації сервісів. [Завантажити](https://www.docker.com/products/docker-desktop/)
*   **Visual Studio Code** або **PyCharm** + **IntelliJ IDEA**: Найкращі IDE для Python та Kotlin відповідно.

### Для Backend (Python):
*   **Python 3.10+**: [Завантажити](https://www.python.org/downloads/)
*   **pip**: (Зазвичай йде в комплекті з Python).

### Для Backend (Kotlin):
*   **JDK 17 або 21**: (Рекомендовано Amazon Corretto або OpenJDK).
*   **Gradle**: (Вбудований у проекти IntelliJ IDEA, але можна мати і системний).

### Для Frontend (Клієнтська частина):
*   Буде використовуватись **Kotlin** (наприклад, Compose Multiplatform для Desktop/Web) або **Python** (Streamlit, Flet).
*   Спеціальні інструменти (як Node.js) не потрібні.

---

## 2. Структура проекту

Створимо структуру, яка відповідає принципам SOA. Кожен сервіс — це окрема папка зі своєю логікою та залежностями.

```text
space-data-soa-platform/
├── services/
│   ├── satellite-tracker/      # Kotlin (Ktor/Spring)
│   ├── astro-objects/         # Python (FastAPI)
│   ├── space-weather/         # Python (FastAPI)
│   ├── mission-data/          # Python (FastAPI)
│   └── user-service/          # Python (FastAPI)
├── frontend/                  # Kotlin (Compose) або Python клієнт
├── infrastructure/
│   ├── docker-compose.yml     # Спільні бази даних та проксі
│   └── nginx/                 # API Gateway конфігурація
├── wiki/                      # Документація (вже є)
└── README.md
```

---

## 3. Крок 1: Ініціалізація структури папок

Відкрийте термінал у папці проекту та виконайте:

```powershell
mkdir services, frontend, infrastructure
mkdir services/satellite-tracker, services/astro-objects, services/space-weather, services/mission-data, services/user-service
```

---

## 4. Крок 2: Налаштування Docker (Інфраструктура)

Створимо файл `infrastructure/docker-compose.yml`, щоб підняти базу даних PostgreSQL з розширенням TimescaleDB.

1. Перейдіть в `infrastructure/`.
2. Створіть файл `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: timescale/timescaledb:latest-pg15
    container_name: space-data-db
    environment:
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=admin_pass
      - POSTGRES_DB=spacedata
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

**Запуск:** `docker-compose up -d` (виконати в папці `infrastructure`).

---

## 5. Крок 3: Налаштування Python-сервісів (Автоматизовано)

Щоб не налаштовувати кожен сервіс вручну, використовуйте готовий скрипт автоматизації. Він створить віртуальні середовища, файли залежностей та базовий код для всіх сервісів одночасно.

1. Відкрийте термінал у корені проекту.
2. Запустіть скрипт:
   ```powershell
   .\setup_services.ps1
   ```

Це налаштує наступні сервіси:
*   `astro-objects`
*   `space-weather`
*   `mission-data`
*   `user-service`

### Як працювати з сервісом після налаштування:
1. Зайдіть у папку сервісу: `cd services/space-weather`
2. Активуйте середовище: `.\venv\Scripts\activate`
3. Запустіть сервер: `uvicorn main:app --reload --port 8001` (змінюйте порт для кожного сервісу).


---

## 6. Крок 4: Налаштування Kotlin-сервісу (satellite-tracker)

Найпростіший спосіб почати — використати [Ktor Starter](https://start.ktor.io/) або створити новий проект в IntelliJ IDEA.

1. Відкрийте IntelliJ IDEA.
2. New Project -> Kotlin Multiplatform або Ktor.
3. Оберіть Gradle (Kotlin DSL).
4. Додайте залежності для:
   - Ktor Server
   - Routing, Serialization (JSON)
   - Exposed (для роботи з БД)

---

## 7. Крок 5: Отримання API ключів

Для роботи сервісів вам потрібно зареєструватися на наступних ресурсах:

1. **NASA API**: [api.nasa.gov](https://api.nasa.gov/) (Отримайте безкоштовний ключ).
2. **Space-Track**: [space-track.org](https://www.space-track.org/) (Для даних супутників).
3. **NOAA SWPC**: (Зазвичай не потребує ключа для базових даних, але перевірте документацію).

Зберігайте ці ключі у файлі `.env` у кожному сервісі (не додавайте їх в Git!).

---

## Наступні кроки

1. Запустіть Docker з базою даних.
2. Створіть "Hello World" на FastAPI у сервісі `space-weather`.
3. Спробуйте зробити перший запит до NASA API за допомогою бібліотеки `requests`.
