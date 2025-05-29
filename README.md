# Foodgram - Продуктовый помощник

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://docker.com)

## Содержание
1. [Описание](#описание)
2. [Технологии](#технологии)
3. [Запуск с Docker](#запуск-с-docker)
4. [Доступные эндпоинты](#доступные-эндпоинты)

---

## Описание
Foodgram - это "Продуктовый помощник" для публикации рецептов. Пользователи могут:
- Создавать и публиковать рецепты
- Подписываться на авторов
- Добавлять рецепты в избранное
- Формировать список покупок

---

## Технологии
- **Backend**: Django REST Framework
- **Frontend**: React (собранный статикой)
- **База данных**: PostgreSQL
- **Контейнеризация**: Docker
- **CI/CD**: GitHub Actions

---

## Запуск с Docker

### 1. Клонируйте репозиторий
```bash
git clone git@github.com:BokGosha/foodgram-st.git
cd foodgram-st/infra
```

### 2. Настройте переменные окружения
Создайте файл .env в папке infra по примеру:

```python
# PostgreSQL
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key
```

### 3. Запустите контейнеры
```bash
docker-compose up -d --build
```

### 4. Создайте суперпользователя
```bash
docker-compose exec foodgram-back python manage.py createsuperuser
```

---

### Доступные эндпоинты

После запуска API будет доступно по адресу: http://localhost/api/

Основные эндпоинты:

* api/users/ - Управление пользователями
* api/recipes/ - Работа с рецептами
* api/ingredients/ - Ингредиенты

Документация API: http://localhost/api/docs/

---

Приложение доступно по адресу: http://localhost
