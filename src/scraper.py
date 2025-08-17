import logging
from datetime import datetime
from google_play_scraper import Sort, reviews
import csv
import yaml
import schedule
import time

logging.basicConfig(filename='logs/scraper.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PlayStoreScraper:
    def __init__(self, config_path='config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.lang = 'en'
        self.country = 'et'  # Ethiopia
        self.sort = Sort.NEWEST
        self.count = 400  # Per bank

    def scrape_reviews(self, app_id, bank_name):
        logging.info(f"Fetching reviews for {bank_name} ({app_id})...")
        try:
            results, _ = reviews(app_id, lang=self.lang, country=self.country, sort=self.sort, count=self.count)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'data/raw/{bank_name.replace(" ", "_")}_reviews_{timestamp}.csv'
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['review_text', 'rating', 'date', 'bank_name', 'source'])
                writer.writeheader()
                for entry in results:
                    writer.writerow({
                        'review_text': entry['content'],
                        'rating': entry['score'],
                        'date': entry['at'].strftime('%Y-%m-%d'),
                        'bank_name': bank_name,
                        'source': 'Google Play'
                    })
            logging.info(f"Saved {len(results)} reviews to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error for {bank_name}: {e}")
            return None

    def scrape_all(self):
        for key, app_id in self.config['app_ids'].items():
            bank_name = self.config['bank_names'][key]
            self.scrape_reviews(app_id, bank_name)

    def schedule_scraping(self):
        schedule.every().day.at("01:00").do(self.scrape_all)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    scraper = PlayStoreScraper()
    scraper.scrape_all() 