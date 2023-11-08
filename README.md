# Инструменты разработки (Мазепа Юлия)

- [API HeadHunter. Получение вакансий](\hw-1-head_hunter\hh.ipynb)

    Анализ вакансий ML и DS специалистов, полученных с сайта headhunter

- [FastAPI. Сервис ветеринарной клиники](main.py)

    API для ветеринарной клиники, реализованное на FastAPI + SQLAlchemy.

    Описание методов API:
    - `/post (POST)` - вспомогательный метод, фиксирующий временную метку запроса;
    - `/dog (GET)` - получение списка собак;
    - `/dog (POST)` - создание новой собаки;
    - `/dog/{pk} (GET)` - получение собаки по ключу;
    - `/dog/{pk} (POST)` - обновление информации о собаке по ключу;
