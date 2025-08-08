"""Scraper to find curriculum links on the program pages.
Looks for Google Drive file links of the form /file/d/<id>/view
"""
import re
import requests
from bs4 import BeautifulSoup

PROGRAM_PAGES = {
    'ai': 'https://abit.itmo.ru/program/master/ai',
    'ai_product': 'https://abit.itmo.ru/program/master/ai_product',
}

USER_AGENT = 'itmo-advisor-bot/1.0 (+https://example.org)'

def find_drive_links(url):
    resp = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        m = re.search(r'/file/d/([a-zA-Z0-9_-]+)/', href)
        if m:
            links.add(m.group(1))
        m2 = re.search(r'drive.google.com/file/d/([a-zA-Z0-9_-]+)/', href)
        if m2:
            links.add(m2.group(1))
    return list(links)

if __name__ == '__main__':
    out = {}
    for key, url in PROGRAM_PAGES.items():
        try:
            ids = find_drive_links(url)
        except Exception as e:
            print(f'Failed to fetch {url}:', e)
            ids = []
        out[key] = ids
        print(key, ids)
    # Save to file
    import json
    with open('drive_links.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print('Saved drive_links.json')
