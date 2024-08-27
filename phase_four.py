import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os
import re

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

def save_to_csv(products, filename):
    if not products:
        return
    keys = products[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(products)

def download_image(image_url, folder_path, image_name):
    response = requests.get(image_url)
    if response.status_code == 200:
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)

def sanitize_filename(filename):
    return re.sub(r'[\/:*?"<>’“”|]', '_', filename)

def main_page_scrape(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    category_bar = soup.find('ul', class_='nav nav-list')
    category_urls = []

    if category_bar:
        li_tags = category_bar.find_all('li')
        for index, li_tag in enumerate(li_tags):
            if index == 0:
                continue
            a_tag = li_tag.find('a')
            if a_tag and 'href' in a_tag.attrs:
                relative_url = a_tag['href']
                full_url = urljoin(url, relative_url)
                category_urls.append(full_url)

    return category_urls

def scrape_category(category_url, category_name):
    all_product_details = []
    images_folder = f"images_{category_name}"

    if not os.path.exists(images_folder):
        os.makedirs(images_folder)

    while category_url:
        product_urls = scrape_page(category_url)
        for product_url in product_urls:
            details = extract_product_details(product_url)
            all_product_details.append(details)
            image_url = details.get('Image URL')
            title = details.get('Title', 'unknown')
            sanitized_title = sanitize_filename(title) + '.jpg'
            if image_url:
                download_image(image_url, images_folder, sanitized_title)

        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, "html.parser")
        category_url = get_next_page_url(soup, category_url)

    csv_filename = f"{category_name}.csv"
    save_to_csv(all_product_details, csv_filename)

def main():
    home_page_url = 'https://books.toscrape.com/catalogue/category/books_1/index.html'
    categories = main_page_scrape(home_page_url)

    for category_url in categories:
        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, "html.parser")
        category_name = soup.find('h1').get_text().strip().replace('/', '_')


        scrape_category(category_url, category_name)




if __name__ == "__main__":
    main()
