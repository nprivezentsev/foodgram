# Фудграм (Foodgram)

## Описание

Фудграм — это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и формировать список покупок для выбранных блюд.

Основные возможности:
* Управление рецептами: добавление, просмотр, обновление, удаление.
* Подписки на авторов.
* Добавление рецептов в избранное.
* Формирование и скачивание списка покупок в формате PDF.

Что было сделано в ходе работы над проектом:
* Создан собственный API-сервис на базе проекта Django.
* Подключено SPA к бэкенду на Django через API.
* Создано, развёрнуто и запущено на сервере мультиконтейнерное приложение.
* Закреплены на практике основы DevOps, включая CI/CD.

Использованные инструменты и технологии:
* Python
* Django
* Django ORM
* Django REST Framework
* Djoser
* PostgreSQL
* Docker, Docker Compose
* GitHub, GitHub Actions
* ReportLab (для генерации PDF)
* JSON
* YAML
* Nginx
* Gunicorn
* Postman

## Установка

Проект разворачивается с использованием Docker. Чтобы запустить его на локальной машине, выполните следующие шаги:

1. Склонируйте репозиторий:

    ~~~bash
    git clone https://github.com/nprivezentsev/foodgram.git
    ~~~

2. Создайте файл .env в корне проекта и заполните его следующими данными:

    ~~~makefile
    SECRET_KEY=<секретный-ключ>
    DEBUG=False
    ALLOWED_HOSTS=localhost,127.0.0.1
    CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    POSTGRES_DB=foodgram
    POSTGRES_USER=foodgram
    POSTGRES_PASSWORD=<пароль-базы-данных>
    ~~~

3. Запустите Docker Compose:

    ~~~bash
    docker compose up -d
    ~~~

4. Выполните миграции:

    ~~~bash
    docker compose exec backend python manage.py migrate
    ~~~

5. Соберите статику:

    ~~~bash
    docker compose exec backend python manage.py collectstatic
    ~~~

6. Создайте суперпользователя для доступа к административной панели:

    ~~~bash
    docker compose exec backend python manage.py createsuperuser
    ~~~

Проект будет доступен по адресу: http://localhost:8000/

## Автор

Бэкенд разработал: Николай Привезенцев

Для связи: [github.com/nprivezentsev](https://github.com/nprivezentsev)