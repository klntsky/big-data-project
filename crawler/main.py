#!/usr/bin/env python3

import requests
from http.cookies import SimpleCookie
import time
import random
import json
import os.path
import pickle

cookie_str = "" # Set me

assert cookie_str != ""

def build_url(page_number: int, category: str):
    return "https://www.upwork.com/ab/ats-aas/api/profile-search/profiles"\
        "?category_uid=" + category + \
        "&page=" + str(page_number)

# Load cookies

SESSION_FILE = 'session'

cookie = SimpleCookie()
cookie.load(cookie_str)
try:
    with open(SESSION_FILE, 'rb') as f:
        s = pickle.load(f)
    print('loaded from ', SESSION_FILE)
except BaseException as e:
    print(e)
    s = requests.Session()
    for key, morsel in cookie.items():
        s.cookies[key] = morsel.value
    print('created new session')

hdrs = {
"Host": "www.upwork.com",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Language": "en-US,en;q=0.5",
"Connection": "keep-alive",
"Upgrade-Insecure-Requests": "1",
"Pragma": "no-cache",
"Cache-Control": "no-cache",
"TE": "Trailers",
}

categories = {
    "531770282584862721": "Accounting and consulting",
    "531770282580668416": "Admin support",
    "531770282580668417": "Customer Service",
    "531770282580668420": "Data Science & Analytics",
    "531770282580668421": "Design & Creative",
    "531770282584862722": "Engineering & Architecture",
    "531770282580668419": "IT & Networking",
    "531770282584862723": "Legal",
    "531770282580668422": "Sales & Marketing",
    "531770282584862720": "Translation",
    "531770282580668418": "Web, Mobile & Software dev",
    "531770282580668423": "Writing",
}

def get_fname(cat_key: str, page_number: int):
    return 'out/' + cat_key + '-' + str(page_number) + '.json'

def getCookies(cookie_jar):
    cookie_dict = cookie_jar.get_dict()
    found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
    return ';'.join(found)

def save_session(sess):
    with open(SESSION_FILE, 'wb') as f:
        pickle.dump(sess, f)

def go():
    for cat_key, cat_title in categories.items():
        for page_number in range(1, 501):
            fname = get_fname(cat_key, page_number)
            if os.path.isfile(fname):
                print('.', end='')
                continue
            url = build_url(page_number=page_number, category=cat_key)
            local_hdrs = hdrs.copy()
            local_hdrs['Referer'] = url
            response = s.get(url, headers=local_hdrs)

            if response.ok:
                try:
                    content_json = response.json()
                    with open(fname, 'w') as fp:
                        json.dump(content_json["results"]["profiles"], fp)
                    save_session(s)
                    print('ok', fname)

                except BaseException as e:
                    print('Not a json', fname, response.text)
                    with open(fname + '.fail', 'w') as f:
                        print(url)
                        f.write(response.text)
                        save_session(s)
                        return

            else:
                print('Response not ok', fname, response)
                print(response.text)
                print(json.dumps(s.cookies.get_dict()))
                save_session(s)
                return

            time.sleep(random.randint(3, 5))

go()
