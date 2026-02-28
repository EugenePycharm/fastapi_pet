# Docker Commands

## Быстрый старт

```bash
# Запустить PostgreSQL
docker-compose up -d

# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f postgres

# Остановить
docker-compose down
```

## Команды

| Команда | Описание |
|---------|----------|
| `docker-compose up -d` | Запуск PostgreSQL в фоне |
| `docker-compose down` | Остановка и удаление контейнеров |
| `docker-compose down -v` | Остановка + удаление volumes (все данные БД!) |
| `docker-compose logs -f` | Просмотр логов |
| `docker-compose restart` | Перезапуск |
| `docker-compose exec postgres psql -U $DB_USER -d $DB_NAME` | Подключение к БД |

## Применение миграций

```bash
# После запуска Docker примените миграции
uv run alembic upgrade head
```

## Сброс базы данных

⚠️ **Внимание:** Удалит все данные!

```bash
docker-compose down -v
docker-compose up -d
uv run alembic upgrade head
```

## Подключение к БД из приложения

Данные автоматически берутся из `.env`:
- `DB_HOST=localhost`
- `DB_PORT=5432` (или ваш порт)
- `DB_NAME=...`
- `DB_USER=...`
- `DB_PASSWORD=...`
