import requests
from bs4 import BeautifulSoup
import time
import random
from requests.exceptions import RequestException

class ProductScraper:
    def __init__(self, url):
        self.url = url
        self.id = None
        self.name = None
        self.url = url
        self.price = None
        self.shipped_by = None
        self.sold_by = None
        self.rating = None
        self.timestamp = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_product_data(self):
        if "newegg.com" not in self.url:
            raise ValueError("Invalid URL. Please provide a valid Newegg URL.")
        
        try:
            print(f"Fetching data from URL: {self.url}")
            response = self.session.get(self.url)
            if response.status_code == 403 or "Are you a human?" in response.text:
                raise RequestException("Blocked by CAPTCHA")
            
            doc = BeautifulSoup(response.content, 'html.parser')
            print("Document parsed with BeautifulSoup.")

            # Extracting the Name
            try:
                self.name = doc.find('h1', class_='product-title').get_text().strip()
                print(f"Product Name: {self.name}")
            except AttributeError:
                print("Product name not found.")
                self.name = 'Unknown'

            # Extracting the price
            try:
                price_Location = doc.find('div', class_='product-price').find_next('li', class_="price-current")
                price_Whole_Number = price_Location.find_next('strong').get_text()
                price_Decimal = price_Location.find_next('sup').get_text()
                full_price = price_Whole_Number + price_Decimal
                full_price = full_price.replace(',', '')
                self.price = float(full_price)
                print(f"Product Price: {self.price}")
            except (AttributeError, ValueError):
                print("Product price not found or could not be converted to float.")
                self.price = 0.0

            # Extracting the "Shipped by" information
            try:
                shipped_by_location = doc.find(class_="product-shipping")
                if shipped_by_location:
                    shipped_by_text = shipped_by_location.find_next(string='Shipped by: ')
                    if shipped_by_text:
                        self.shipped_by = shipped_by_text.find_next('strong').get_text()
                    else:
                        shipped_by_text = shipped_by_location.find_next(string='Shipped by:')
                        if shipped_by_text:
                            self.shipped_by = shipped_by_text.find_next('strong').get_text()
                        else:
                            self.shipped_by = None
                else:
                    self.shipped_by = None
                print(f"Shipped by: {self.shipped_by}")
            except AttributeError:
                print("Shipped by information not found.")
                self.shipped_by = 'Unknown'

            # Extracting the "Sold by" information
            try:
                sold_by_location = doc.find(class_="product-shipping")
                if sold_by_location:
                    sold_by_text = sold_by_location.find_next(string='Sold by: ')
                    if sold_by_text:
                        self.sold_by = sold_by_text.find_next('strong').get_text()
                    else:
                        sold_by_text = sold_by_location.find_next(string='Sold by:')
                        if sold_by_text:
                            self.sold_by = sold_by_text.find_next('strong').get_text()
                        else:
                            self.sold_by = None
                print(f"Sold by: {self.sold_by}")
            except AttributeError:
                print("Sold by information not found.")
                self.sold_by = 'Unknown'

            # Extracting the "Rating" information
            try:
                rating_location = doc.find('div', class_='product-rating')
                if rating_location:
                    rating_element = rating_location.find_next('i')
                    if rating_element:
                        title = rating_element.get('title')
                        if title:
                            self.rating = title.split()[0]
                        else:
                            self.rating = None
                print(f"Rating: {self.rating}")
            except AttributeError:
                print("Rating information not found.")
                self.rating = 'Unknown'

            # Recording the timestamp
            self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Timestamp: {self.timestamp}")

        except RequestException as e:
            print(f"Request failed: {e}")

    def return_product_data(self):
        product_data = {
            'Name': self.name,
            'URL': self.url,
            'Price': self.price,
            'Shipped_by': self.shipped_by,
            'Sold_by': self.sold_by,
            'Rating': self.rating,
            'Timestamp': self.timestamp
        }
        print(f"Product Data: {product_data}")
        return product_data

# Test
url = 'https://www.newegg.com/asus-pg32ucdp-32-uhd-dual-mode-4k-240hz-fhd-480hz-rog-swift-woled/p/N82E16824281314?Item=N82E16824281314'
scraper = ProductScraper(url)
scraper.fetch_product_data()
product_data = scraper.return_product_data()
# print(scraper.price)
# print(product_data)
