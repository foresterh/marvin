import urllib2, base64, urllib
import requests
from bs4 import BeautifulSoup
import json
import random


def build_request(url, username=None, password=None):
    request = urllib2.Request(url)
    if username and password:
        base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
    return request


def get_title(url):
    try:
        soup = BeautifulSoup(urllib2.urlopen(url))
        return soup.title.string
    except:
        return None
        #return "Not logged in or bad url"

def get_text(url):
    try:
        soup = BeautifulSoup(urllib2.urlopen(url))
        return soup.string
    except:
        error_messages = ("No way can I do that", "Why would I want to do that?", "Bank error in your favor", "You trying to kill me with that request??")
        return random.choice(error_messages)


def get_json_with_querystring(url, params):
    r = requests.get(url, params=params)
    if r.text:
        return r.text
    return None


def get_json(url, username=None, password=None):
    data = get_raw(url, username, password)
    if data:
        return json.loads(data)
    return None


def get_raw(url, username=None, password=None):
    request = build_request(url, username, password)
    page = urllib2.urlopen(request)
    data = page.read().decode("utf-8-sig")
    if data:
        return data
    return None


def post_json_secure(url, token, body):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept-Encoding': 'gzip'
    }
    return requests.post(url, data=body, headers=headers)


def get_json_secure(url, token):
    headers = {
        'Authorization': 'Bearer {}'.format(token),
        'Accept-Encoding': 'gzip'
    }
    data = requests.get(url, headers=headers)
    if data:
        return json.loads(data.text)
    return None

def post_json(url, username, password, **kwargs):
    request = build_request(url, username, password)
    request.add_data(urllib.urlencode(kwargs))

    page = urllib2.urlopen(request)
    data = page.read()
    if data:
        return json.loads(data)
    return data
