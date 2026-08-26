# Электронное согласие — Begemotik

Клиент открывает форму (GitHub Pages) → заполняет данные → рисует подпись →
бэкенд генерирует DOCX и PDF по единому шаблону, загружает **оба** файла на
Google Drive, а клиенту сразу отдаёт на скачивание **только PDF**.

---

## Архитектура

```
frontend/                        # GitHub Pages (статика)
  index.html
  style.css
  script.js
  config.js                      # BACKEND_URL — адрес бэкенда

backend/                         # FastAPI (Docker, деплой на Railway)
  app/
    main.py                      # FastAPI app, CORS, эндпоинт /api/v1/agreements
    config.py                    # Pydantic settings (.env)
    models.py                    # Pydantic-модель запроса (валидация полей)
    docgen.py                    # Заполнение DOCX-шаблона (docxtpl) → PDF (LibreOffice)
    drive.py                     # Загрузка DOCX+PDF на Google Drive
    templates/
      begemotik_template.docx    # Единственный шаблон согласия
  Dockerfile
  requirements.txt
  .env.example
```

Один шаблон `begemotik_template.docx` используется для всех согласий —
никакой логики выбора шаблона по типу процедуры нет.

---

## Быстрый старт (локально)

### 1. Переменные окружения

```bash
cp backend/.env.example backend/.env
# Заполните GOOGLE_DRIVE_FOLDER_ID и OAuth-креды (client_id/secret/refresh_token)
```

### 2. Бэкенд

**С Docker (рекомендуется — уже включает LibreOffice):**

```bash
cd backend
docker build -t begemotik-backend .
docker run --env-file .env -p 8000:8000 begemotik-backend
```

**Без Docker (нужен установленный LibreOffice):**

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Фронтенд

```bash
cd frontend
python -m http.server 5500
# → http://localhost:5500
```

Убедитесь, что в `frontend/config.js` указан верный `BACKEND_URL`
(например, `http://localhost:8000` для локальной разработки).

---

## Настройка Google Drive

1. В [Google Cloud Console](https://console.cloud.google.com/) создайте проект и включите **Google Drive API**.
2. Создайте **OAuth Client ID** типа **Web Application**.
3. Получите `refresh_token` для аккаунта, в чей Drive нужно загружать файлы.
4. Скопируйте ID папки из URL: `https://drive.google.com/drive/folders/<FOLDER_ID>`.
5. Заполните в `backend/.env`:
   ```env
   GOOGLE_DRIVE_FOLDER_ID=<FOLDER_ID>
   GOOGLE_OAUTH_CLIENT_ID=<CLIENT_ID>
   GOOGLE_OAUTH_CLIENT_SECRET=<CLIENT_SECRET>
   GOOGLE_OAUTH_REFRESH_TOKEN=<REFRESH_TOKEN>
   ```

Если OAuth-креды не заданы, загрузка на Drive просто пропускается (пишется
warning в лог) — генерация и скачивание PDF клиентом при этом всё равно
работают.

---

## Деплой

**Бэкенд (Railway):** Root Directory — `backend`. Railway сам найдёт
`Dockerfile` (см. `railway.json`). Не забудьте задать переменные окружения
в настройках сервиса.

**Фронтенд (GitHub Pages):** автодеплой через `.github/workflows/pages.yml`
из папки `/frontend` при пуше в `main`. Не забудьте прописать актуальный
`BACKEND_URL` в `frontend/config.js` и добавить URL Pages в `CORS_ORIGINS`
на бэкенде.

---

## Проверка end-to-end

1. Открыть форму → заполнить данные пациента → поставить подпись → нажать «Подписать».
2. Бэкенд генерирует DOCX → конвертирует в PDF → загружает оба файла на Google Drive.
3. Браузер сразу скачивает PDF на телефон.

Проверить, что бэкенд жив:
```bash
curl https://<your-app>.up.railway.app/health
# {"status":"ok"}
```

---

## Известные ограничения

- Нет базы данных — вся история только в Google Drive.
- Нет аутентификации пользователей.
- LibreOffice в Docker-образе увеличивает его размер (~400 MB) и время холодного старта.
- При большом числе одновременных запросов возможна очередь на LibreOffice —
  для масштабирования нужен отдельный воркер/очередь задач.
