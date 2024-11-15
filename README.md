# Фудграм (Foodgram)

## Описание

Фудграм — это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и формировать список покупок для выбранных блюд.

Основные возможности:
* Управление рецептами: добавление, просмотр, обновление, удаление.
* Подписки на авторов.
* Добавление рецептов в избранное.
* Формирование и скачивание списка покупок в формате PDF.

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

## Примеры запросов

### Получение списка рецептов

Запрос: GET /api/recipes/

Ответ:

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 5,
            "ingredients": [
                {
                    "id": 5,
                    "name": "2",
                    "measurement_unit": "2",
                    "amount": 20
                }
            ],
            "tags": [
                {
                    "id": 2,
                    "name": "2",
                    "slug": "2"
                }
            ],
            "image": "http://127.0.0.1:8000/media/recipe_images/b8272318-9319-4bb2-aff1-ed753ace714a.png",
            "name": "Варёное нечто",
            "text": "Варить 20 минут",
            "cooking_time": 25,
            "author": {
                "email": "vivanov@yandex.ru",
                "id": 26,
                "username": "vasya.ivanov",
                "first_name": "Вася",
                "last_name": "Иванов",
                "is_subscribed": false,
                "avatar": null
            },
            "is_favorited": false,
            "is_in_shopping_cart": false
        }
    ]
}
```

### Подписка на автора

Запрос: POST /api/users/28/subscribe/

Ответ:

```json
{
    "email": "gramzikov@yetanothermail.ru",
    "id": 28,
    "username": "gramzikov",
    "first_name": "Гордон",
    "last_name": "Рамзиков",
    "is_subscribed": true,
    "recipes": [],
    "recipes_count": 0,
    "avatar": null
}
```

### Скачивание списка покупок

Запрос: GET /api/recipes/download_shopping_cart/

Ответ: PDF-файл с перечнем ингредиентов.

## Использованные технологии

* Python
* Django
* Django REST Framework
* Djoser
* PostgreSQL
* Docker, Docker Compose
* ReportLab (для генерации PDF)

## Автор

Бэкенд проекта разработан Николаем Привезенцевым.

Для связи: [github.com/nprivezentsev](https://github.com/nprivezentsev)