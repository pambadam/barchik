import requests
import re
from bs4 import BeautifulSoup
import json

URL = "https://en.wikipedia.org/wiki/List_of_cocktails"
ALLOWED = re.compile('/wiki/')
NOT_ALLOWED = re.compile('History|List|:|drinks|#')
END_BLOCK = "Other"
PATH_DATA = 'data'


def check_pattern(url, allowed=ALLOWED, not_allowed=NOT_ALLOWED):
    return bool(url is not None and allowed.match(url) and not not_allowed.search(url))


def get_id(soup, header_name):
    for h in soup.find_all('h2'):
        if h.find_all(class_='mw-headline')[0].text == header_name:
            return h.find_all(class_='mw-headline')[0].get('id')


def find_prev_url(soup, header_name):
    header_id = get_id(soup, header_name)
    end_block = soup.find(id=header_id)
    prev_url = end_block.find_next('h2').find_previous('a').get('href')
    return prev_url


def get_list_items(soup):
    li_items = []
    for i in soup.find_all('li'):
        if i.find('a') is not None and check_pattern(i.find('a').get('href')):
            li_items.append(i.find('a'))
    return li_items


def get_urls(url=URL, header=END_BLOCK):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    soup = soup.find(id='content')
    _ = soup.find(id='toc').extract()

    cocktails = get_list_items(soup)
    cocktail_urls = {}
    last_url = find_prev_url(soup, header)
    for cocktail in cocktails:
        if cocktail.get('href') not in cocktail_urls.values():
            cocktail_urls[cocktail.string] = cocktail.get('href')
        if cocktail.get('href') == last_url:
            break
    return cocktail_urls


if __name__ == '__main__':
    cocktails_wiki_urls = get_urls()
    json.dump(cocktails_wiki_urls, open(PATH_DATA+'/cocktails_wiki_urls.json', 'w'))
