# mc-aybolit.ru — автотесты (Python + Playwright + Pytest)

## Установка
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

## Запуск
```bash
pytest -v
```

## Переменные окружения
- `BASE_URL` (по умолчанию `https://mc-aybolit.ru`)
- `LK_URL` (по умолчанию `https://lk.mc-aybolit.ru`)
- `HEADLESS=0` — запуск с UI

## Примечания
Тесты написаны устойчиво (role/text/url) и местами содержат soft-логики:
- некоторые проверки могут быть `skip/xfail`, если на сайте нет соответствующего функционала
  или есть внешние скрипты, генерирующие ошибки в консоли.
