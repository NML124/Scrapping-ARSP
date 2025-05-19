import asyncio
import aiohttp

from services.enterprise_fetcher import EnterpriseFetcher
from services.persistent_manager import PersistenceManager
from services.progress_reporter import ProgressReporter


class EnterpriseScraper:
    def __init__(self, persistence=PersistenceManager(progress_file="scraper_progress.pkl", temp_csv_file="data/entreprise_temp.csv"), fetcher=EnterpriseFetcher(), progress_reporter_cls=ProgressReporter):
        self.persistence = persistence
        self.fetcher = fetcher
        progress = self.persistence.load_progress()
        self.links = progress.get('links', [])
        self.data = progress.get('data', [])
        self.scraped_links = set(progress.get('scraped_links', []))
        self.progress_reporter_cls = progress_reporter_cls

    async def scrape_async(self):
        if not self.links:
            main_html = await self.fetcher.fetch_main_page()
            self.links = self.fetcher.extract_links(main_html)
        to_process = [(idx, link) for idx, link in enumerate(self.links, 1) if link not in self.scraped_links]
        total = len(self.links)
        print(f"Scraping enterprise data... ({len(to_process)} to process out of {total})")
        progress_bar = self.progress_reporter_cls(total=total, initial=len(self.scraped_links), desc="Scraping enterprises")
        batch_size = 100
        counter = 0
        semaphore = asyncio.Semaphore(100)
        async with aiohttp.ClientSession(headers=self.fetcher.HEADERS) as session:
            async def fetch_and_store(idx_link):
                nonlocal counter
                _, link = idx_link
                if link in self.scraped_links:
                    progress_bar.update(1)
                    return None
                async with semaphore:
                    info = await self.fetcher.fetch_enterprise_info(session, link)
                if info:
                    self.data.append(info)
                    self.scraped_links.add(link)
                    self.persistence.append_to_temp_csv(info)
                    counter += 1
                    if counter % batch_size == 0:
                        self.persistence.save_progress(self.links, self.data, self.scraped_links)
                progress_bar.update(1)
                return info
            try:
                tasks = [fetch_and_store(idx_link) for idx_link in to_process]
                await asyncio.gather(*tasks)
            except KeyboardInterrupt:
                print("\nScraping interrupted. Saving progress to temporary file...")
                self.persistence.save_progress(self.links, self.data, self.scraped_links)
            finally:
                self.persistence.save_progress(self.links, self.data, self.scraped_links)
                progress_bar.close()
                if len(self.scraped_links) == total:
                    print("Scraping completed successfully.")
                else:
                    print("Progress saved")

    def scrape(self):
        asyncio.run(self.scrape_async())

    def save_to_csv(self, filename='data/entreprise.csv'):
        self.persistence.save_to_csv(self.data, filename)
