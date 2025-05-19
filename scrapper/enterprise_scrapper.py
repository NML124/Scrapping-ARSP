import concurrent.futures

from services.enterprise_fetcher import EnterpriseFetcher
from services.persistent_manager import PersistenceManager
from services.progress_reporter import ProgressReporter


class EnterpriseScraper:
    def __init__(self, persistence=PersistenceManager(progress_file="scraper_progress.pkl",temp_csv_file="data\entreprise_temp.csv",temp_progress_file="scraper_progress_temp.pkl"), fetcher=EnterpriseFetcher(), progress_reporter_cls=ProgressReporter):
        self.persistence = persistence
        self.fetcher = fetcher
        progress = self.persistence.load_progress()
        self.links = progress.get('links', [])
        self.data = progress.get('data', [])
        self.scraped_links = set(progress.get('scraped_links', []))
        self.progress_reporter_cls = progress_reporter_cls

    def scrape(self):
        if not self.links:
            main_html = self.fetcher.fetch_main_page()
            self.links = self.fetcher.extract_links(main_html)
        to_process = [(idx, link) for idx, link in enumerate(self.links, 1) if link not in self.scraped_links]
        total = len(self.links)
        print(f"Scraping enterprise data... ({len(to_process)} to process out of {total})")
        progress_bar = self.progress_reporter_cls(total=total, initial=len(self.scraped_links), desc="Scraping enterprises")
        def fetch_and_store(idx_link):
            idx, link = idx_link
            if link in self.scraped_links:
                progress_bar.update(1)
                return None
            info = self.fetcher.fetch_enterprise_info(link)
            if info:
                self.data.append(info)
                self.scraped_links.add(link)
                self.persistence.save_progress(self.links, self.data, self.scraped_links)
                self.persistence.save_progress(self.links, self.data, self.scraped_links, temp=True)
                self.persistence.append_to_temp_csv(info)
            progress_bar.update(1)
            return info
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                list(executor.map(fetch_and_store, to_process))
        except KeyboardInterrupt:
            print("\nScraping interrupted. Saving progress to temporary file...")
            self.persistence.save_progress(self.links, self.data, self.scraped_links, temp=True)
            raise
        finally:
            progress_bar.close()

    def save_to_csv(self, filename='data/entreprise.csv'):
        self.persistence.save_to_csv(self.data, filename)
