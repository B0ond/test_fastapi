# FastAPI + PostgreSQL + Docker

Пример приложения на FastAPI с использованием
 PostgreSQL в качестве базы данных. Проект упакован в Docker-контейнеры для удобства запуска.

## Описание

Проект включает:
- FastAPI как веб-фреймворк.
- PostgreSQL как базу данных.
- SQLAlchemy для работы с базой данных.
- Docker для контейнеризации.

## Требования

Для запуска проекта вам понадобится:
- [Docker](https://www.docker.com/products/docker-desktop/)

## Установка и запуск

1. **Скачать образ из докерхаба:**
- docker pull b0ond/test_fastapi-app:latest
2. **Клонируйте репозиторий с гитхаба в любую папку:**
- git clone https://github.com/B0ond/test_fastapi.git
3. **переходите в папку с проектом:**
- cd test_fastapi
4. **Запускаете:**
- docker-compose up