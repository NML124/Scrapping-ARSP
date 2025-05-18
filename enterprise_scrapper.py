import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os
import pickle
class EnterpriseScraper:
    BASE_URL = 'https://arsp.cd/registre-des-entreprises-enregistrees/'
    HEADERS = {
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/50.0.2661.102 Safari/537.36'
        )
    }
    PROGRESS_FILE = 'scraper_progress.pkl'
    TEMP_PROGRESS_FILE = 'scraper_progress_temp.pkl'
    TEMP_CSV_FILE = 'data/entreprise_temp.csv'

    def __init__(self):
        self.links = []
        self.data = []
        self.scraped_links = set()
        self.load_progress()

    def load_progress(self):
        # Prefer loading from temp file if it exists
        progress_file = self.TEMP_PROGRESS_FILE if os.path.exists(self.TEMP_PROGRESS_FILE) else self.PROGRESS_FILE
        if os.path.exists(progress_file):
            with open(progress_file, 'rb') as f:
                progress = pickle.load(f)
                self.links = progress.get('links', [])
                self.data = progress.get('data', [])
                self.scraped_links = set(progress.get('scraped_links', []))

    def save_progress(self, temp=False):
        file_to_save = self.TEMP_PROGRESS_FILE if temp else self.PROGRESS_FILE
        with open(file_to_save, 'wb') as f:
            pickle.dump({
                'links': self.links,
                'data': self.data,
                'scraped_links': list(self.scraped_links)
            }, f)

    def fetch_main_page(self):
        response = requests.get(self.BASE_URL, headers=self.HEADERS)
        response.raise_for_status()
        return response.text

    def extract_links(self, html):
        # Only extract if links are not already loaded
        if self.links:
            return
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find('tbody')
        if not tds:
            return
        for td in tds:
            a=td.find('a')
            if str(a)!="-1" and a!=None:
                link=a['onclick'][22:110]
                self.links.append("https://arsp.cd/"+link)

    def fetch_enterprise_info(self, link):
        res = requests.get(link, headers=self.HEADERS)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find('table')
        if not table:
            return []
        informations = table.find_all('td')
        return [info.text.strip() for info in informations]

    def append_to_temp_csv(self, enterprise):
        with open(self.TEMP_CSV_FILE, 'a', encoding='utf-8') as file:
            file.write("\\".join(enterprise[:9]) + "\n")

    def scrape(self):
        main_html = self.fetch_main_page()
        self.extract_links(main_html)

        def fetch_and_store(idx_link):
            idx, link = idx_link
            if link in self.scraped_links:
                return None
            info = self.fetch_enterprise_info(link)
            if info:
                print(idx)
                self.data.append(info)
                self.scraped_links.add(link)
                self.save_progress()  # Save main progress
                self.save_progress(temp=True)  # Save temp progress
                self.append_to_temp_csv(info)  # Append to temp CSV
            return info

        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(executor.map(fetch_and_store, enumerate(self.links, 1)))
        except KeyboardInterrupt:
            print("\nScraping interrupted. Saving progress to temporary file...")
            self.save_progress(temp=True)
            raise

    def save_to_csv(self, filename='data/entreprise.csv'):
        with open(filename, 'w', encoding="utf-8") as file:
            for enterprise in self.data:
                file.write("\\".join(enterprise[:9]) + "\n")
        # Optionally, update the temp CSV to match the final CSV after a successful run
        with open(self.TEMP_CSV_FILE, 'w', encoding='utf-8') as temp_file:
            for enterprise in self.data:
                temp_file.write("\\".join(enterprise[:9]) + "\n")
