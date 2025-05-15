### Описание
Shasdes of Flavor — это приложение для обмена рецептами, где пользователи могут публиковать свои рецепты, подписываться на других пользователей и добавлять рецепты в избранное. Проект позволяет сохранять рецепты в списке покупок и загружать список необходимых ингредиентов для приготовления рецептов из корзины в удобном формате.

### Технологии и инструменты
![Nginx](https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white) 
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) 
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) 
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) 
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white) 
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white) 
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) 
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white) 
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?style=for-the-badge&logo=gunicorn&logoColor=white) 
![Redoc](https://img.shields.io/badge/redoc-%23Clojure.svg?style=for-the-badge&logo=redoc&logoColor=white) 

### Подготовка к запуску проекта
- Перед запуском проекта необходимо создать файл .env с настройками окружения. В корне проекта имеется пример: .env.example. Создайте .env на основе него и разместите:
  - для локального запуска: в папке local_runserver/, рядом с docker-compose.local.yml
  - для продакшн-запуска: в папке infra, там же где и docker-compose.production.yml

- Убедитесь, что у вас установлен и запущен docker

### Для локального запуска проекта с Docker:
  - Убедитесь, что Docker запущен
  - Перейдите в папку local_runserver/
  - Запустите локальные контейнеры (backend + frontend + nginx + PostgreSQL)
    ```bash
    docker compose -f docker-compose.local.yml up -dc
    ```
  - Откройте проект в браузере по адресу http://localhost:8001/

### Деплой на удалённый сервер через GitHub Actions: подогнать файл foodgram/.github/workflows/main.yml под свой удалённый сервер:
  - Убедитесь, что Docker установлен и запущен на сервере
    ```bash
    sudo systemctl status docker
    ```
  - Создайте .env файл на сервере. Он должен находиться в папке foodgram/ — в той же директории, куда GitHub Actions копирует docker-compose.production.yml. Пример файла см. в .env.example.
  - Настройте GitHub Secrets в репозитории:
    - HOST — IP-адрес удалённого сервера
    - USER — SSH-пользователь
    - SSH_KEY — приватный ключ
    - SSH_PASSPHRASE — (если есть)
    - DOCKER_USERNAME, DOCKER_PASSWORD
  - становить и настроить nginx сервер. Он должен проксировать запросы с вашего домена/IP на порт 8001, который слушает контейнер Nginx из проекта.
  - Деплой выполняется автоматически при пуше в ветку main. GitHub actions выполнит всю работу разместив на вашем удаленном сервере docker сеть из 3 контейнеров: postgresql, backend и nginx контейнеры. Frontend контейнер собирает своё приложение и передает в папку frontend на 1 уровень выше папки с compose файлом.
### 📌 Важно:
.env файл должен быть расположен рядом с docker-compose.production.yml — в папке infra/ (локально) и ~/foodgram/ (на сервере). Иначе переменные окружения не будут найдены.

## Документация API
По адресу http://localhost/api/docs/ вы можете найти спецификацию API.


Проект разработан Келесидисом Александром. GitHub: [Keleseth](https://github.com/Keleseth)
