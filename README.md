# Books Scraper

Проект для автоматического сбора данных о книгах с сайта [Books to Scrape](http://books.toscrape.com).

## Цель проекта

Разработать систему для автоматического парсинга информации о книгах со всех страниц каталога сайта Books to Scrape. Система включает:
- Парсинг данных о книгах (название, цена, рейтинг, описание и т.д.)
- Автоматический ежедневный запуск задачи по расписанию
- Сохранение результатов в текстовый файл
- Написание и запуск юнит-тестов

## Используемые библиотеки

- `requests` - для выполнения HTTP-запросов
- `beautifulsoup4` - для парсинга HTML-страниц
- `schedule` - для автоматизации запуска задач по расписанию
- `pytest` - для написания и запуска тестов

## Инструкции по запуску

### Установка зависимостей

```bash
pip install -r requirements.txt
```

### Запуск парсинга

#### Парсинг одной книги

```python
from scraper import get_book_data

book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
book_data = get_book_data(book_url)
print(book_data)
```

#### Парсинг всех книг

```python
from scraper import scrape_books

# Парсинг без сохранения в файл
books = scrape_books(is_save=False)

# Парсинг с сохранением в файл books_data.txt
books = scrape_books(is_save=True)
```

#### Автоматический запуск по расписанию

Для настройки автоматического запуска каждый день в 19:00 используйте следующий код:

```python
import schedule
import time
from scraper import scrape_books

def run_scheduled_scraping():
    print(f"Запуск сбора данных в {time.strftime('%Y-%m-%d %H:%M:%S')}")
    scrape_books(is_save=True)
    print(f"Сбор данных завершен в {time.strftime('%Y-%m-%d %H:%M:%S')}")

# Настройка расписания
schedule.every().day.at("19:00").do(run_scheduled_scraping)

# Бесконечный цикл для проверки расписания
while True:
    schedule.run_pending()
    time.sleep(60)  # Проверяем расписание каждую минуту
```

### Запуск тестов

```bash
pytest tests/test_scraper.py
```

Или для более подробного вывода:

```bash
pytest tests/test_scraper.py -v
```

## Структура проекта

```
books_scraper/
├── artifacts/
│   └── books_data.txt          # Результаты парсинга
├── notebooks/
│   └── HW_03_python_ds_2025.ipynb  # Jupyter notebook с заданиями
├── tests/
│   ├── __init__.py
│   └── test_scraper.py         # Тесты на pytest
├── scraper.py                   # Основной модуль парсера
├── README.md                    # Этот файл
├── requirements.txt             # Зависимости проекта
└── .gitignore                   # Игнорируемые файлы Git
```

## Описание функций

### `get_book_data(book_url: str) -> dict`

Извлекает данные о книге с указанной страницы.

**Параметры:**
- `book_url` (str): URL страницы книги

**Возвращает:**
- `dict`: Словарь с данными о книге (название, цена, рейтинг, описание и т.д.)

### `scrape_books(is_save: bool = False) -> list`

Собирает данные обо всех книгах со всех страниц каталога.

**Параметры:**
- `is_save` (bool): Если True, сохраняет результаты в файл `books_data.txt`

**Возвращает:**
- `list`: Список словарей с данными о всех книгах

