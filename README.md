### Oписание
В проекте Yatube можно выкладывать посты, комментировать и следить за любимыми авторами с помошью пописки.

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Impossible14/hw05_final.git
```

```
cd hm05_final/
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:
```
cd yatube/
```

```
python manage.py migrate
```

Запустить тесты и проверить работоспособность сайта:

```
python manage.py test
```

Запустить проект:

```
python manage.py runserver
```