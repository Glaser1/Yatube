# Yatube

Социальная сеть для публикации блогов с возможностью регистрации, создания и
редактирования постов, просмотра страниц других авторов и подписки на них, а также
комментирования записей.

### Использованные технологии:
 Python 3.7, Django 2.2.16, Pytest, Pillow, sorl-thumbnail


### Установка:  

 Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Glaser1/yatube.git
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source venv/scripts/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```


### Документация:
  Доступна после запуска проекта по адресу: (https://127.0.0.1:8000/redoc/)
