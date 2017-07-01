from bs4 import BeautifulSoup
from urllib.request import urlopen,HTTPError, Request, FancyURLopener
import re
import time
from details import db


class Item:

    def __init__(self, asin, name, price, availability, least_price):
        self.item_asin = asin
        self.name = name
        self.cur_price = price
        self.availability = availability
        self.least_price = least_price

class Wishlist:

    def __init__(self, wishlist_id, email, name, num_of_items):

        self.wishlist_id = wishlist_id
        self.email = email
        self.name = name
        self.num_of_items = num_of_items

# agent = {'User-Agent': 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'}

class AppURLopener(FancyURLopener):
    version = "Mozilla/5.0"

def get_url(url, limit):
    # print(limit)
    html = None
    # page = AppURLopener()
    try:
        html = urlopen(url)
    except Exception as e:
        print(e)
        if limit == 0:
            return None
        time.sleep(2)
        get_url(url, limit-1)
    # finally:
    return html


def get_all_items(base_url, page, all_items):
    url = base_url + str(page)
    html = get_url(url, 3)
    if html is None:
        return -1
    bs_obj = BeautifulSoup(html, "html.parser", from_encoding="UTF-8")
    pat = "/gp/aw/d/([A-Z0-9]+)"
    bs_obj = bs_obj.find("form", {"method": "post"})
    count = 0
    found = 0
    for each in bs_obj.find_all('a', {"href": re.compile(r'/gp/aw/d')}):
        found += 1
        item_id = re.search(pat, each.attrs['href']).group(1)
        item_price = each.nextSibling.next.next.strip()
        item_name = each.text

        if item_id in all_items:
            count += 1
        else:
            is_avail = False
            present = re.search('Currently unavailable', item_price, flags=re.IGNORECASE)

            if item_price and not present:
                price = item_price.split(' ')[-1]
                item_price = float(''.join(price.split(',')))
                is_avail = True
            else:
                item_price = None

            new_item = Item(asin=item_id, name=item_name, price=item_price, availability=is_avail, least_price=item_price)
            all_items[item_id] = new_item

        # print(all_items[item_id].item_id, all_items[item_id].item_name, all_items[item_id].item_price)
    if found == count:
        return -1
    else:
        return 1

def get_wishlist_id(url):
    # url = AppURLopener()
    page = get_url(url, 3)
    # print("page = ", page)
    wl_id = None
    pat = "www.amazon.in/registry/wishlist/(.*?)/"
    if page:
        actual_url = page.geturl()
        res = re.search(pat, actual_url)
        if res:
            ans = res.group(1)
            if ans:
                wl_id = ans
    return wl_id


def core(wishlist_id):
    base_url = "https://www.amazon.in/gp/aw/ls/"
    
    url = base_url + wishlist_id + '?p='
    all_items = {}
    page = 1
    while get_all_items(url, page, all_items) != -1:
        # time.sleep(1)
        page += 1

    # print()
    # print(len(all_items))
    return all_items
