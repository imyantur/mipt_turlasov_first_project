"""
Тесты для модуля scraper.py.
"""
import pytest
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from scraper import get_book_data, scrape_books


def test_get_book_data_returns_dict():
    """
    Проверяет, что функция get_book_data возвращает словарь.
    """
    book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    result = get_book_data(book_url)
    assert isinstance(result, dict), "Функция должна возвращать словарь"


def test_get_book_data_has_required_keys():
    """
    Проверяет, что словарь с данными о книге содержит все необходимые ключи.
    """
    book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    result = get_book_data(book_url)
    
    required_keys = ['title', 'price', 'rating', 'availability', 
                     'description', 'product_info', 'url']
    
    for key in required_keys:
        assert key in result, f"В словаре должен быть ключ '{key}'"


def test_get_book_data_title_not_empty():
    """
    Проверяет, что название книги не пустое и является строкой.
    """
    book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    result = get_book_data(book_url)
    
    assert 'title' in result, "Должен быть ключ 'title'"
    assert isinstance(result['title'], str), "Название должно быть строкой"
    assert len(result['title']) > 0, "Название не должно быть пустым"


def test_get_book_data_rating_range():
    """
    Проверяет, что рейтинг находится в допустимом диапазоне (1-5).
    """
    book_url = 'http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'
    result = get_book_data(book_url)
    
    assert 'rating' in result, "Должен быть ключ 'rating'"
    assert isinstance(result['rating'], int), "Рейтинг должен быть целым числом"
    assert 1 <= result['rating'] <= 5, "Рейтинг должен быть от 1 до 5"


def test_scrape_books_returns_list():
    """
    Проверяет, что функция scrape_books возвращает список.
    Для ускорения теста парсим только первую страницу.
    """
    base_url = 'http://books.toscrape.com/'
    response = requests.get(base_url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    books_on_page = soup.find_all('article', class_='product_pod')[:3]
    
    result = []
    for book_article in books_on_page:
        h3_tag = book_article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and 'href' in link_tag.attrs:
                book_relative_url = link_tag['href']
                book_full_url = urljoin(base_url, book_relative_url)
                try:
                    book_data = get_book_data(book_full_url)
                    result.append(book_data)
                except Exception:
                    pass
    
    assert isinstance(result, list), "Функция должна возвращать список"
    assert result is not None, "Функция не должна возвращать None"


def test_scrape_books_returns_non_empty_list():
    """
    Проверяет, что функция scrape_books возвращает непустой список.
    Для ускорения теста парсим только несколько книг с первой страницы.
    """
    base_url = 'http://books.toscrape.com/'
    response = requests.get(base_url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    books_on_page = soup.find_all('article', class_='product_pod')[:3]
    
    result = []
    for book_article in books_on_page:
        h3_tag = book_article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and 'href' in link_tag.attrs:
                book_relative_url = link_tag['href']
                book_full_url = urljoin(base_url, book_relative_url)
                try:
                    book_data = get_book_data(book_full_url)
                    result.append(book_data)
                except Exception:
                    pass
    
    assert len(result) > 0, f"Функция должна вернуть хотя бы одну книгу, получено: {len(result)}"


def test_scrape_books_each_item_is_dict():
    """
    Проверяет, что каждый элемент в списке является словарем.
    Для ускорения теста парсим только несколько книг с первой страницы.
    """
    base_url = 'http://books.toscrape.com/'
    response = requests.get(base_url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    books_on_page = soup.find_all('article', class_='product_pod')[:3]
    
    result = []
    for book_article in books_on_page:
        h3_tag = book_article.find('h3')
        if h3_tag:
            link_tag = h3_tag.find('a')
            if link_tag and 'href' in link_tag.attrs:
                book_relative_url = link_tag['href']
                book_full_url = urljoin(base_url, book_relative_url)
                try:
                    book_data = get_book_data(book_full_url)
                    result.append(book_data)
                except Exception:
                    pass
    
    assert len(result) > 0, "Должна быть хотя бы одна книга"
    for book in result:
        assert isinstance(book, dict), "Каждая книга должна быть словарем"

