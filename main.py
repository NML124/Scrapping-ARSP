from scrapper.enterprise_scrapper import EnterpriseScraper


if __name__ == "__main__":
    scraper = EnterpriseScraper()
    scraper.scrape()
    scraper.save_to_csv()