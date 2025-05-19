import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

class EnterpriseFetcher:
    BASE_URL = 'https://arsp.cd/registre-des-entreprises-enregistrees/'
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/50.0.2661.102 Safari/537.36'
        )
    }
    def fetch_main_page(self):
        print("Loading main page...")
        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        response.raise_for_status()
        print("Main page loaded.")
        return response.text
    
    def extract_links(self, html):
        print("Extracting links from main page...")
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find('tbody')
        links = []
        if not tds:
            return links
        for td in tqdm(tds, desc="Extracting enterprise links"):
            a = td.find('a')
            if str(a) != "-1" and a is not None:
                link = a['onclick'][22:110]
                links.append("https://arsp.cd/" + link)
        print(f"Total enterprises found: {len(links)}")
        return links
    
    def fetch_enterprise_info(self, link):
        res = requests.get(link, headers=self.HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find('table')
        if not table:
            return []
        informations = table.find_all('td')
        return [info.text.strip() for info in informations]
