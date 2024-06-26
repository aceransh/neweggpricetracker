import requests
from bs4 import BeautifulSoup
import time

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

    def fetch_product_data(self):
        if "newegg.com" not in self.url:
            raise ValueError("Invalid URL. Please provide a valid Newegg URL.")
        response = requests.get(self.url)
        doc = BeautifulSoup(response.content, 'html.parser')

        # Extracting the Name
        self.name = doc.find('h1', class_='product-title').get_text()
        # print('Product Name: ' + self.name)

        # Extracting the price
        price_Location = doc.find('div', class_= 'product-price').find_next('li', class_="price-current")
        price_Whole_Number = price_Location.find_next('strong').get_text()
        price_Decimal = price_Location.find_next('sup').get_text()
        full_price = price_Whole_Number + price_Decimal
        full_price = full_price.replace(',', '')
        self.price = float(full_price)
        # print('Price: ' + str(self.price))
        # print("Price's Variable Type: " + str(type(self.price)))

        # Extracting the "Shipped by" information
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
        # print('Shipped by: ' + self.shipped_by)

        # Extracting the "Sold by" information
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
        # print('Sold by: ' + self.sold_by)

        # Extracting the "Rating" information
        rating_location = doc.find('div', class_='product-rating')
        if rating_location:
            # print('Rating location found')
            rating_element = rating_location.find_next('i')
            if rating_element:
                # print('Rating element found')
                title = rating_element.get('title')
                if title:
                    # print('Title atrribute found')
                    self.rating = title.split()[0]
                else:
                    # print('Title attribute not found')
                    self.rating = None
            else:
                # print('Rating element not found')
                self.rating = None
        else:
            # print('Rating location not found')
            self.rating = None

        # print('Rating: ' + self.rating + '/5')

        # Recording the timestamp
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        # print('Timestamp: ' + self.timestamp)

    def return_product_data(self):
        return {
            'Name': self.name,
            'URL': self.url,
            'Price': self.price,
            'Shipped_by': self.shipped_by,
            'Sold_by': self.sold_by,
            'Rating': self.rating,
            'Timestamp': self.timestamp
        }

# Test
# url = 'https://www.newegg.com/black-asus-tuf-gaming-vg249q1r-24/p/N82E16824281256'
# scraper = ProductScraper(url)
# scraper.fetch_product_data()
# product_data = scraper.return_product_data()
# print(scraper.price)
# print(product_data)