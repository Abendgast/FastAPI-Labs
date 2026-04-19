# Деплой API (безкоштовно + домен `abd.pp.ua`)

Хост: **Render** (безкартки на старті, є безкоштовний Web Service, кастомний домен безкоштовно). Мінус: сервіс «засинає» після простою — для заліку зазвичай ок.

## 1. Код у GitHub

- Репозиторій з цим проєктом (або лише папка `samostiyna_robota` у великому репо — тоді крок 3).
- Переконайся, що `.venv` **не** в коміті (у `.gitignore`).

## 2. Render

1. Зайди на https://render.com → Sign up (можна через GitHub).
2. **New +** → **Web Service** → підключи репозиторій.
3. Налаштування:
   - **Name**: будь-яке (наприклад `abd-api`).
   - **Region**: найближча до тебе.
   - **Branch**: `main` / `master` — яка у тебе.
   - **Root Directory**: `samostiyna_robota` (якщо репо в корені FastAPI; якщо залив лише цю папку в окремий репо — залиш **порожнім**).
   - **Runtime**: Python 3.
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. **Create Web Service**. Дочекайся зеленого деплою — відкрий виданий URL, перевір `/` і `/docs`.

## 3. Свій піддомен на `abd.pp.ua`

Приклад: `api.abd.pp.ua` → твій сервіс на Render.

1. У Render: **Settings** → **Custom Domains** → **Add** → введи `api.abd.pp.ua` (або інший піддомен).
2. Render покаже, що додати в DNS (зазвичай **CNAME**: ім’я `api` → значення типу `твій-сервіс.onrender.com`).
3. У панелі де керуєш **abd.pp.ua** (NIC / реєстратор) — розділ DNS: додай цей **CNAME**. Збережи, зачекай 5–30 хв (іноді довше).
4. У Render натисни **Verify** — коли пройде, HTTPS підтягнеться сам.

Кореневий домен `abd.pp.ua` без піддомена на Render повісити складніше (потрібен окремий A/ALIAS у DNS). Для заліку достатньо **`api.abd.pp.ua`** або подібного.

## 4. Якщо треба «своє» API з лаб

Заміни вміст `main.py` на імпорт свого додатку **без** MongoDB на хості, або додай зовнішню БД (Atlas тощо) — це вже зайва морока; для обов’язкової мінімалки достатньо цього робочого API.

## Локальна перевірка

З папки `samostiyna_robota`:

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Відкрий http://127.0.0.1:8000/docs
