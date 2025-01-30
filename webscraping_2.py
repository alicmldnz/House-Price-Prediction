import requests
from bs4 import BeautifulSoup
import csv
import time

class RightmoveScraper:
    results = []    
    
    def fetch(self, url):
        print('HTTP GET request to URL: %s' % url, end='')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        print(' | Status code: %s' % response.status_code)
        return response
    
    def parse(self, html):
        content = BeautifulSoup(html, 'lxml')
        titles = [title.text.strip() for title in content.findAll('h2', {'class': 'propertyCard-title'})] if content.findAll('h2', {'class': 'propertyCard-title'}) else []
        addresses = [address['content'] for address in content.findAll('meta', {'itemprop': 'streetAddress'})] if content.findAll('meta', {'itemprop': 'streetAddress'}) else []
        descriptions = [description.text.strip() for description in content.findAll('span', {'data-test': 'property-description'})] if content.findAll('span', {'data-test': 'property-description'}) else []
        prices = [price.text.strip() for price in content.findAll('div', {'class': 'propertyCard-priceValue'})] if content.findAll('div', {'class': 'propertyCard-priceValue'}) else []
        dates = [date.text.split(' ')[-1] for date in content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'})] if content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'}) else []

        for index in range(len(titles)):
            self.results.append({
                'title': titles[index],
                'address': addresses[index] if index < len(addresses) else 'N/A',
                'description': descriptions[index] if index < len(descriptions) else 'N/A',
                'price': prices[index] if index < len(prices) else 'N/A',
                'date': dates[index] if index < len(dates) else 'N/A',
            })
    
    def to_csv(self):
        if self.results:
            filename = f'rightmove_{int(time.time())}.csv'
            with open(filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
                writer.writeheader()
                for row in self.results:
                    writer.writerow(row)
            print(f'Stored results to "{filename}"')
        else:
            print("No data to save.")
    
    def get_total_pages(self, html):
        content = BeautifulSoup(html, 'lxml')
        page_info = content.find('span', {'class': 'pagination-pageInfo'})
        if page_info:
            total_pages = int(page_info.text.split()[-1])
            return total_pages
        return 1
    
    def run(self):
        url = 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&maxPrice=1200000&minPrice=1300000&index=0'
        response = self.fetch(url)
        total_pages = self.get_total_pages(response.text)
        
        for page in range(42):
            index = page * 24
            url = f'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&maxPrice=1200000&minPrice=1300000&index={index}'
            response = self.fetch(url)
            self.parse(response.text)

        self.to_csv()


if __name__ == '__main__':
    scraper = RightmoveScraper()
    scraper.run()
