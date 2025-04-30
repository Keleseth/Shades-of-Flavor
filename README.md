### Описание
Shasdes of Flavor — это приложение для обмена рецептами, где пользователи могут публиковать свои рецепты, подписываться на других пользователей и добавлять рецепты в избранное. Проект позволяет сохранять рецепты в списке покупок и загружать список необходимых ингредиентов для приготовления рецептов из корзины в удобном формате.
ссылка на сайт - https://flavors.myvnc.com/

### Технологии и инструменты
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) \
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) \
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) \
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) \
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) \
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) \
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) \
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) \
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) \
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) \
![Redoc](https://img.shields.io/badge/redoc-%23Clojure.svg?style=for-the-badge&logo=redoc&logoColor=white) 

### Подготовка к запуску проекта
- Код проекта ожидает наличие .env файла со следующими переменными:
  - POSTGRES_DB — название базы данных, которая будет использоваться в проекте
  - POSTGRES_USER  — имя пользователя для подключения к базе данных
  - POSTGRES_PASSWORD — пароль для пользователя базы данных
  - DB_NAME — название базы данных, которое будет использоваться в настройках Django
  - DB_HOST — хост базы данных (обычно это название сервиса в Docker, например, db)
  - DB_PORT — порт, на котором доступна база данных (обычно 5432 для PostgreSQL)
  - DB_HOST_LOCAL — локальный хост базы данных (например, localhost для тестов на локальной машине)

  - SECRET_KEY — секретный ключ Django для криптографических операций

  - DEBUG_STATUS — статус режима отладки (например, True для включения или False для отключения)

  - ALLOWED_HOSTS — список доменов или IP-адресов, с которых разрешены запросы к бекэнду

  - LANGUAGE_CODE — код языка по умолчанию для проекта (например, ru-ru или en-us)
- Убедитесь, что у вас установлен и запущен docker
- Для локального запуска: 
  - установка зависимостей проекта из файла requirements.txt
  - выполнение миграций внутри контейнера с бэкэндом "docker compose exec backend python manage.py migrate" и создание суперпользователя "docker compose exec backend python manage.py createsuperuser"
  - сборка статики и копирование в папку связанную с docker volume:
    - sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
    - sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/

- Для запуска на удаленном сервере: подогнать файл foodgram/.github/workflows/main.yml под свою удаленный сервер:
  - Еще раз убедиться в том, что docker запущен на удаленном сервере "sudo systemctl status docker"
  - Гитхаб actions секреты (ssh ключ, ip удаленного сервера и юзер.)
  - Указать папку для копирования compose файла в workflows в директорию вашего удаленного сервера, например foodgram и разместить в этой же папке ваш .env файл
  - Установить и настроить nginx веб-сервер на вашем удаленном сервере на проксирование запросов по вашему домену/ip на порт 8001, который будет слушать Nginx контейнер проекта
  - Деплой происходит путем пуша в репозиторий в ветку main. GitHub actions выполнит всю работу разместив на вашем удаленном сервере docker сеть из 3 контейнеров: postgresql, backend и nginx контейнеры. Frontend контейнер собирает своё приложение и передает в папку frontend на 1 уровень выше папки с compose файлом.
- Перейти в директорию infra, и выполнить команду docker compose -f docker-compose.production.yml up
- #### Внимание! .env файл должен находиться в одной директории с compose файлом (в infra), или поменять настройки compose файла путь к .env файлу контейнеров.

## Документация API
По адресу http://localhost/api/docs/ вы можете найти спецификацию API.


Проект разработан Келесидисом Александром. GitHub: [Keleseth](https://github.com/Keleseth)
