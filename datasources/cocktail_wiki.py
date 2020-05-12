import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import urllib.request
import json

PATH_COCKTAIL_IMGS = 'data/cocktails/'
PATH_DATA = 'data'

DESC_FIELDS = ['type', 'primary alcohol by volume', 'standard drinkware', 'served', 'preparation', 'standard garnish', \
               'timing', 'iba official cocktail', 'ingredients', 'alcohol by volume']


def get_img_url(tbl):
    imgs = [td.find('img') for td in tbl.find_all('td')]
    if imgs[0]:
        if 'srcset' in imgs[0].attrs:
            return imgs[0]['srcset'].split(',')[-1].strip().split()[0]
        else:
            return imgs[0]['src'].strip().split()[0]
    return


def save_img(url, img_path):
    image_url = "https:" + url
    urllib.request.urlretrieve(image_url, img_path)


def format_data(desc_dict, fields=DESC_FIELDS):
    if len(desc_dict) > 0:
        for n in desc_dict:
            if n in ['commonly used ingredients', 'main ingredients',
                     'ingredients as listed at cocktaildb', 'iba specifiedingredients']:
                desc_dict['ingredients'] = desc_dict.pop(n)

        if 'iba official cocktail' in desc_dict:
            desc_dict['iba official cocktail'] = 1
        else:
            desc_dict['iba official cocktail'] = 0
        to_delete = [k for k in desc_dict.keys() if k not in fields]
        for k in to_delete:
            del desc_dict[k]
    return desc_dict


def get_cocktail_info(urls, path=PATH_COCKTAIL_IMGS):
    cocktail_data = defaultdict(dict)
    cocktail_img_paths = {}
    for name, url in urls.items():
        cocktail_url = "https://en.wikipedia.org" + url
        response = requests.get(cocktail_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tbl = soup.find("table", {"class": "infobox"})
        if tbl:
            list_of_table_rows = [th.text.lower() for th in tbl.find_all('th')]
            list_of_table_contents = [td.text for td in tbl.find_all('td')]
            table_data = dict(zip(list_of_table_rows, list_of_table_contents))
            table_data['photo'] = get_img_url(tbl)
            if table_data['photo']:
                img_path = path + name.replace(' ', '_') + '.JPG'
                save_img(table_data['photo'], img_path)
                cocktail_img_paths[name] = img_path
            cocktail_data[name] = format_data(table_data)
    return cocktail_data, cocktail_img_paths


if __name__ == '__main__':
    cocktail_urls = json.load(open(PATH_DATA+'/cocktails_wiki_urls.json'))
    cocktail_recipes, cocktail_imgs = get_cocktail_info(cocktail_urls)
    json.dump(cocktail_recipes, open(PATH_DATA+'/recipes.json', 'w'))
