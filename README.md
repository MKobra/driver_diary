# Driver Diary

Дневник смен водителя: FastAPI-сервер, JSON-хранилище поездок и веб-клиент на HTML, CSS и JavaScript.

## Запуск

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска health-проверка доступна по адресу `http://127.0.0.1:8000/api/health`.

Веб-клиент доступен по адресу `http://127.0.0.1:8000/`.

Основные API:

- `GET /api/trips?date=2026-10-01` — поездки за день;
- `POST /api/trips` — добавить поездку;
- `GET /api/summary?date=2026-10-01` — дневная сводка.

## Тесты

```powershell
pytest
```

Тесты бизнес-логики будут добавлены отдельным этапом.
