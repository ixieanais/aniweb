<div align="center">

<img width="140" height="140" src="docs/logo.png" alt="logo">

# Aniweb

Aniweb - персональное веб-приложение для стриминга аниме с русской озвучкой.

![](https://img.shields.io/github/stars/ixieanais/aniweb)
![](https://img.shields.io/github/issues/ixieanais/aniweb)
![](https://img.shields.io/github/forks/ixieanais/aniweb)

[English](README.md) | Russian

</div>

# О проекте

Aniweb - персональный стриминговый сайт для просмотра аниме с русской озвучкой от [AniLiberty](https://aniliberty.top/). Для получения информации об аниме используется API от AniLiberty. Интерфейс сделан с любовью и специально для тех кто смотрел аниме на jut.su. Проект ориентирован на локальный или self-hosted запуск.

# Функции

* **Внешние API**: использует [AniLiberty API](https://api.anilibria.app/api/docs/v1/) для получения информации
* **Главная страница**: показывает последние обновлённые релизы и релизы, которые стоят в очереди на просмотр
* **Каталог релизов**: в каталоге можно найти интересное аниме по фильтрам
* **Поиск вверху страницы**: ищет аниме по запросу
* **Избранные релизы**: вы можете добавить выбранный релиз в избранное. Чтобы увидеть все избранные релизы, зайдите в избранное на верхней панели
* **Плеер**: вместо обычного плеера в HTML используется удобный и простой Plyr.js
* **Поддержка для телефонов**: Пока что очень плохая поддержка, но на половину она существует
* **Отмеченные просмотренные эпизоды**: когда вы досматриваете эпизод релиза, то текущая серия помечается как просмотренная

# Технологический стек

**Backend**:

* Python
* FastAPI
* uvicorn
* Jinja2
* SQLite

**Frontend**:

* HTML
* CSS
* JavaScript
* HLS.js
* Plyr.js

# Установка

Требования: Python 3.11+

```bash
git clone https://github.com/ixieanais/aniweb.git
cd aniweb

pip install -r requirements.txt
```

# Запуск

```bash
python main.py
```

# Вклад в проект

Если вы хотите сделать какой либо вклад в проект, то пожалуйста, я рад видеть любой интересный вклад в этот проект!

1. Форкните репозиторий
2. Создайте ветку
3. Зафиксируйте изменения
4. Отправьте в ветку
5. Откройте Pull Request

# Лицензия

Авторские права © 2025 [ixieanais](https://github.com/ixieanais).<br>
Aniweb под [MIT](https://choosealicense.com/licenses/mit) лицензированием.