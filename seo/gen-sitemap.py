import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def crawl(url, depth=1):
    visited = set()
    urls = _crawl([url], visited, depth)
    return urls


def _crawl(urls, visited, depth):
    if depth < 0:
        return []

    new_urls = set()
    for url in urls:
        if url not in visited:
            print(f'Crawling {url} at depth {depth}...')
            visited.add(url)
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    page = BeautifulSoup(response.text, 'html.parser')
                    new_urls.update(
                        urljoin(url, link.get('href'))
                        for link in page.find_all('a')
                    )
            except requests.exceptions.RequestException:
                pass

    new_urls.update(_crawl(new_urls, visited, depth - 1))
    return list(new_urls)


def create_sitemap(urls):
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        sitemap += f'  <url>\n    <loc>{url}</loc>\n  </url>\n'
    sitemap += '</urlset>'
    return sitemap


urls = crawl('https://cleanb.life', depth=2)
sitemap = create_sitemap(urls)
with open('sitemap.xml', 'w') as f:
    f.write(sitemap)
