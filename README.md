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

- `GET /api/trips?date=2026-10-01&page=1&page_size=10` — страница поездок за день;
- `POST /api/trips` — добавить поездку;
- `GET /api/summary?date=2026-10-01` — дневная сводка.

Ответ списка поездок содержит `items`, `total`, `page`, `page_size` и `total_pages`.

Ответ `POST /api/trips` содержит `created`: `true` для новой поездки и `false`, если такой `id` уже существует.

API возвращает `409 Conflict`, если новая поездка пересекается по времени с уже сохранённой поездкой. Интервалы, где новая поездка начинается ровно в момент окончания предыдущей, разрешены.

## Тесты

```powershell
pytest
```

Тесты бизнес-логики будут добавлены отдельным этапом.
