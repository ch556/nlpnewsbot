import requests
import json
import logging
from api_keys import world_news_key, wrldnews_api
from utils import decode_url
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def get_text(url):
    logging.info(f'Getting text for {url}')
    wn_url = f"https://api.apilayer.com/world_news/extract-news?url={url}&analyze={False}"
    headers = {
        "apikey": world_news_key
    }
    response = requests.request("GET", wn_url, headers=headers)

    if response.status_code == 200:
        result = response.text
        decoded_text = result.encode('utf-8').decode('unicode-escape')

        try:
            text_field = json.loads(decoded_text)["text"]
            return True, text_field
        except json.decoder.JSONDecodeError:
            logging.error('JSON decode error! Skipping article...')
            return True, 'Не получилось обработать эту статью'

    if response.status_code == 502:
        return False, 'Bad link!'
    else:
        logging.error(f'get_text response: {response.status_code}')
        return False, response.status_code


def parse_lenta():
    url = 'https://lenta.ru'
    response = requests.get(url)
    html_content = response.content

    soup = BeautifulSoup(html_content, 'html.parser')

    container = soup.find('div', class_=lambda x: 'last24' in x if x else False)

    if container:
        links = container.find_all('a')
        article_links = []
        for link in links:
            article_links.append(link['href'])
        return article_links
    else:
        return f'Error trying to get news from lenta.ru'


def get_news(amount=5):
    links = parse_lenta()
    news = []
    for link in links[:amount]:
        l = 'https://lenta.ru' + link
        news.append([l, get_text(l)[1]])
    return news


def collect_news(co):
    now = datetime.now()
    earliest_publish_date = now - timedelta(days=2)
    earliest_publish_date_str = earliest_publish_date.strftime('%Y-%m-%dT%H:%M:%S')
    url = f"https://api.worldnewsapi.com/search-news?source-countries={co}&language=ru&earliest-publish-date={earliest_publish_date_str}"
    api_key = wrldnews_api

    headers = {
        'x-api-key': api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        news = []
        for article in response.json()['news']:
            news.append([article['url'], article['text']])
        return news
    else:
        logging.error(f"Error: {response.status_code}")


