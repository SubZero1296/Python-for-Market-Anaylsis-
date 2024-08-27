import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

def scrape_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    ol_class_items = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
    product_urls = []
    for item in ol_class_items:
        a_tag = item.find('h3').find('a')
        relative_url = a_tag['href']
        full_url = urljoin(url, relative_url)
        product_urls.append(full_url)
    return product_urls

def get_next_page_url(soup, base_category_url):
    next_button = soup.find('li', class_='next')
    if next_button:
        next_link = next_button.find('a')['href']
        return urljoin(base_category_url, next_link)
    return None

def extract_product_details(product_url):
    page = requests.get(product_url)
    soup = BeautifulSoup(page.content, "html.parser")
    base_url = 'https://books.toscrape.com/'
    
    product_details = {}
    
    product_details['URL'] = product_url
    product_details['UPC'] = soup.find('th', string='UPC').find_next('td').get_text()
    product_details['Title'] = soup.find('h1').get_text()
    product_details['Price (incl. tax)'] = soup.find('th', string='Price (incl. tax)').find_next('td').get_text()
    product_details['Price (excl. tax)'] = soup.find('th', string='Price (excl. tax)').find_next('td').get_text()
    product_details['Availability'] = soup.find('th', string='Availability').find_next('td').get_text()
    
    description_div = soup.find('div', id='product_description')
    if description_div:
        product_details['Description'] = description_div.find_next('p').get_text()
    else:
        product_details['Description'] = 'Product Description not found'
    
    breadcrumb_items = soup.find('ul', class_='breadcrumb').find_all('li')
    product_details['Category'] = breadcrumb_items[2].get_text(strip=True)
    
    product_details['Review Rating'] = soup.find('p', class_='star-rating')['class'][1]
    
    image_url = soup.find('img')
    relative_src = image_url['src']
    full_url = urljoin(base_url, relative_src)
    product_details['Image URL'] = full_url
    
    return product_details

def main():
    base_category_url = "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html"
    url = base_category_url
    

    all_product_details = []
    
    while url:
        product_urls = scrape_page(url)
        for product_url in product_urls:
            product_details = extract_product_details(product_url)
            all_product_details.append(product_details)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        url = get_next_page_url(soup, base_category_url)

    keys = all_product_details[0].keys() if all_product_details else []
    with open('product_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        writer.writerows(all_product_details)

if __name__ == "__main__":
    main()
