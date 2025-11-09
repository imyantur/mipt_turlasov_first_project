"""
Модуль для парсинга данных о книгах с сайта Books to Scrape.
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def get_book_data(book_url: str) -> dict:
    """
    Извлекает данные о книге с указанной страницы сайта Books to Scrape.
    
    Args:
        book_url (str): URL страницы книги для парсинга.
        
    Returns:
        dict: Словарь с данными о книге, включающий:
            - title: название книги
            - price: цена
            - rating: рейтинг (количество звезд)
            - availability: количество в наличии
            - description: описание книги
            - product_info: словарь с дополнительной информацией из таблицы
              Product Information (UPC, Product Type, Price (excl. tax) и т.д.)
    """
    try:
        response = requests.get(book_url, timeout=15)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.Timeout as e:
        raise Exception(f"Таймаут при загрузке страницы: {e}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при загрузке страницы: {e}")
    
    title_elem = soup.find('h1')
    if title_elem and title_elem.text:
        title = title_elem.text.strip()
    else:
        title = 'Нет названия'
    
    price_elem = soup.find('p', class_='price_color')
    if price_elem and price_elem.text:
        price = price_elem.text.strip()
    else:
        price = 'Нет цены'
    
    rating = 0
    rating_elem = soup.find('p', class_='star-rating')
    if rating_elem and 'class' in rating_elem.attrs:
        rating_classes = rating_elem['class']
        rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
        for class_name in rating_classes:
            if class_name in rating_map:
                rating = rating_map[class_name]
                break
    
    availability = 'Нет информации'
    availability_elem = soup.find('p', class_='instock availability')
    if not availability_elem:
        availability_elem = soup.find('p', class_='availability')
    if not availability_elem:
        availability_classes = ['instock', 'availability']
        for class_name in availability_classes:
            availability_elem = soup.find('p', class_=class_name)
            if availability_elem:
                break
    if availability_elem and availability_elem.text:
        availability = availability_elem.text.strip()
    
    description = ''
    try:
        product_description = soup.find('div', id='product_description')
        if product_description:
            description_tag = product_description.find_next_sibling('p')
            if description_tag and description_tag.text:
                description = description_tag.text.strip()
    except Exception:
        pass
    
    product_info = {}
    try:
        table = soup.find('table', class_='table table-striped')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                th = row.find('th')
                td = row.find('td')
                if th and td and th.text and td.text:
                    key = th.text.strip()
                    value = td.text.strip()
                    if key and value:
                        product_info[key] = value
    except Exception:
        pass
    
    return {
        'title': title,
        'price': price,
        'rating': rating,
        'availability': availability,
        'description': description,
        'product_info': product_info,
        'url': book_url
    }


def scrape_books(is_save: bool = False) -> list:
    """
    Собирает данные обо всех книгах со всех страниц каталога Books to Scrape.
    
    Проходит по всем страницам каталога (page-1.html, page-2.html и т.д.),
    находит ссылки на книги и извлекает данные о каждой книге.
    
    Args:
        is_save (bool): Если True, сохраняет результаты в файл books_data.txt.
                        По умолчанию False.
        
    Returns:
        list: Список словарей с данными о всех книгах.
    """
    base_url = 'http://books.toscrape.com/'
    catalogue_url = 'http://books.toscrape.com/catalogue/'
    all_books = []
    page = 1
    
    while True:
        if page == 1:
            page_url = base_url
        else:
            page_url = f'{catalogue_url}page-{page}.html'
        
        try:
            response = requests.get(page_url, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            
            books_on_page = soup.find_all('article', class_='product_pod')
            
            if not books_on_page:
                break
            
            for book_article in books_on_page:
                h3_tag = book_article.find('h3')
                if not h3_tag:
                    continue
                link_tag = h3_tag.find('a')
                if link_tag and 'href' in link_tag.attrs:
                    book_relative_url = link_tag['href']
                    book_full_url = urljoin(page_url, book_relative_url)
                    
                    max_retries = 5
                    for attempt in range(max_retries):
                        try:
                            book_data = get_book_data(book_full_url)
                            all_books.append(book_data)
                            try:
                                print(f"Собрана книга: {book_data['title']}")
                            except UnicodeEncodeError:
                                print(f"Собрана книга: {book_data['title'].encode('ascii', 'ignore').decode('ascii')}")
                            break
                        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 2
                                print(f"Попытка {attempt + 1}/{max_retries} не удалась для {book_full_url.split('/')[-2]}, повтор через {wait_time} сек...")
                                time.sleep(wait_time)
                                continue
                            else:
                                print(f"Не удалось загрузить книгу после {max_retries} попыток: {book_full_url.split('/')[-2]}")
                        except Exception as e:
                            error_msg = str(e)
                            if 'Timeout' in error_msg or 'timeout' in error_msg:
                                if attempt < max_retries - 1:
                                    wait_time = (attempt + 1) * 2
                                    print(f"Таймаут при загрузке {book_full_url.split('/')[-2]}, повтор через {wait_time} сек...")
                                    time.sleep(wait_time)
                                    continue
                                else:
                                    print(f"Таймаут после {max_retries} попыток: {book_full_url.split('/')[-2]}")
                            else:
                                print(f"Ошибка при парсинге книги {book_full_url.split('/')[-2]}: {error_msg}")
                            break
            
            page += 1
            time.sleep(0.5)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                break
            else:
                print(f"HTTP ошибка при обработке страницы {page}: {e}")
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            print(f"Ошибка соединения при обработке страницы {page}: {e}")
            print(f"Повторная попытка через 3 секунды...")
            time.sleep(3)
            continue
        except Exception as e:
            print(f"Ошибка при обработке страницы {page}: {e}")
            break
    
    if is_save:
        os.makedirs('artifacts', exist_ok=True)
        file_path = 'artifacts/books_data.txt'
        with open(file_path, 'w', encoding='utf-8') as f:
            for book in all_books:
                f.write(f"Название: {book['title']}\n")
                f.write(f"Цена: {book['price']}\n")
                f.write(f"Рейтинг: {book['rating']} звезд\n")
                f.write(f"В наличии: {book['availability']}\n")
                f.write(f"Описание: {book['description']}\n")
                f.write(f"URL: {book['url']}\n")
                f.write("Дополнительная информация:\n")
                for key, value in book['product_info'].items():
                    f.write(f"  {key}: {value}\n")
                f.write("\n" + "="*80 + "\n\n")
        print(f"\nДанные сохранены в файл {file_path}")
    
    return all_books

