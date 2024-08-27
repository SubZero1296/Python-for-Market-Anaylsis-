import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv


URL = "https://books.toscrape.com/catalogue/scott-pilgrims-precious-little-life-scott-pilgrim-1_987/index.html"
page = requests.get(URL)
base_url = 'https://books.toscrape.com/'
soup = BeautifulSoup(page.content, "html.parser")

product_page_url = URL
universal_product_code = soup.find('th', string='UPC').find_next('td').get_text()
book_title = soup.find('h1').get_text()
price_including_tax = soup.find('th', string='Price (incl. tax)').find_next('td').get_text()
price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next('td').get_text()  
quantity_available = soup.find('th', string='Availability').find_next('td').get_text()
description_div = soup.find('div', id='product_description')
product_description = description_div.find_next('p').get_text() if description_div else 'Product Description not found'
breadcrumb_items = soup.find('ul', class_='breadcrumb').find_all('li')
category = breadcrumb_items[2].get_text(strip=True)
review_rating = soup.find('p', class_='star-rating')['class'][1]
image_url = soup.find('img')
relative_src = image_url['src']
full_url = urljoin(base_url, relative_src)


csv_file_path = 'book_details.csv'

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Product Page URL', 'Universal Product Code', 'Book Title', 'Price (including tax)', 'Price (excluding tax)', 'Quantity Available', 'Product Description', 'Category', 'Review Rating', 'Image URL']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerow({
        'Product Page URL': product_page_url,
        'Universal Product Code': universal_product_code,
        'Book Title': book_title,
        'Price (including tax)': price_including_tax,
        'Price (excluding tax)': price_excluding_tax,
        'Quantity Available': quantity_available,
        'Product Description': product_description,
        'Category': category,
        'Review Rating': review_rating,
        'Image URL': full_url
    })

print(f"Data has been exported to {csv_file_path}")
