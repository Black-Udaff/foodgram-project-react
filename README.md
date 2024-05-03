[![Main foodgram workflow](https://github.com/Black-Udaff/foodgram-project-react/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/Black-Udaff/foodgram-project-react/actions/workflows/main.yml)

## Для ревью
```
Адрес: https://foodygram.webhop.me/

Админка: admin eqhn8eto

```



## Проект Foodgram

Foodgram — это кулинарный помощник, который предлагает обширную базу данных рецептов. Это место, где вы можете публиковать свои рецепты, сохранять любимые и формировать список покупок для выбранных блюд. Также доступна функция подписки на авторов, чьи рецепты вам особенно нравятся.

### Адрес проекта
Проект доступен для доступа по [ссылке](https://foodygram.webhop.me/).

### Документация API
Ознакомиться с документацией API, где подробно описаны возможные запросы и структура ответов, можно [здесь](https://foodygram.webhop.me/api/docs/).


### Функции сервиса:
- публикуйте и делитесь своими кулинарными рецептами
- просматривайте блюда, загруженные другими пользователями
- сохраняйте понравившиеся рецепты в своем личном избранном
- создавайте персональный список покупок, добавляя нужные рецепты в корзину
- отслеживайте активность и обновления друзей и коллег в сервисе

### Используемые технологии:
- Python
- Django
- Django Rest Framework
- Docker
- Gunicorn
- NGINX
- PostgreSQL
- Yandex Cloud
- Continuous Integration (CI)
- Continuous Deployment (CD)


### Развернуть проект на удаленном сервере:

1. Клонировать репозиторий(себе на локальную машину):
```
https://github.com/Black-Udaff/foodgram-project-react.git
```

2. Установить на сервере Docker, Docker Compose:

```
sudo apt install curl                                   # установка утилиты для скачивания файлов
curl -fsSL https://get.docker.com -o get-docker.sh      # скачать скрипт для установки
sh get-docker.sh                                        # запуск скрипта
sudo apt-get install docker-compose-plugin              # последняя версия docker compose
```

3. Скопировать на сервер файлы по пути foodgram/ docker-compose.production.yml и .env:
```
пример файла .env:

POSTGRES_USER=django_user
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432

```

```
scp docker-compose.production.yml .env username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

4. Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

```

5. Создать и запустить контейнеры Docker, выполнить команду на сервере
*(версии команд "docker compose" или "docker-compose" отличаются в зависимости от установленной версии Docker Compose):*
```
sudo docker compose -f docker-compose.production.ym up -d(предварительно нужно собрать все докер образы локально и запушить на Docker Hub или просто запушить проект на Git Hub )
```

- После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic
```

- Наполнить базу данных содержимым из файла ingredients.json:
```
sudo docker compose exec backend python manage.py import_data data/ingredients.json
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

### После каждого обновления репозитория (push в ветку master) будет происходить:

1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8)
2. Сборка и доставка докер-образов frontend , backend и nginx на Docker Hub
3. Разворачивание проекта на удаленном сервере
4. Отправка сообщения в Telegram в случае успеха

### Запуск проекта на локальной машине:

1. Клонировать репозиторий:
```
https://github.com/Black-Udaff/foodgram-project-react.git
```

2. В корне создать файл .env и заполнить своими данными :
```
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```

3. Создать и запустить контейнеры Docker, последовательно выполнить команды по созданию миграций, сбору статики, 
созданию суперпользователя, как указано выше.
```
docker-compose up --build
```


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost:6555/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost:6555/api/docs/)


### Автор backend'а:

Алексей Каземиренко (c) 2024
