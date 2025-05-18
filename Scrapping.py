import requests
from bs4 import BeautifulSoup


class EnterpriseScraper:
    BASE_URL = 'https://arsp.cd/registre-des-entreprises-enregistrees/'
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/50.0.2661.102 Safari/537.36'
        )
    }

    def __init__(self):
        self.links = []
        self.data = []

    def fetch_main_page(self):
        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        response.raise_for_status()
        return response.text

    def extract_links(self, html):
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find('tbody')
        if not tds:
            return
        for td in tds.find_all('tr'):
            a = td.find('a')
            if a and 'onclick' in a.attrs:
                link = a['onclick'][22:110]
                self.links.append("https://arsp.cd/" + link)

    def fetch_enterprise_info(self, link):
        res = requests.get(link, headers=self.HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find('table')
        if not table:
            return []
        informations = table.find_all('td')
        return [info.text.strip() for info in informations]

    def scrape(self):
        main_html = self.fetch_main_page()
        self.extract_links(main_html)
        for idx, link in enumerate(self.links, 1):
            info = self.fetch_enterprise_info(link)
            if info:
                self.data.append(info)
                print(idx)

    def save_to_csv(self, filename='entreprise2.csv'):
        with open(filename, 'w', encoding="utf-8") as file:
            for enterprise in self.data:
                file.write("\\".join(enterprise[:9]) + "\n")


if __name__ == "__main__":
    scraper = EnterpriseScraper()
    scraper.scrape()
    scraper.save_to_csv()