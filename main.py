from random import random
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import csv
import time

driver = uc.Chrome()
driver.set_page_load_timeout(10)


def get_product_page(page):
    try:
        driver.get(page)
        return True
    except Exception as e:
        print(f"Page not loaded: {page}, error: {e}")
        return False

def scrape_pages():
    all_links = []
    for i in range(20):
        page_url = f"https://www.newegg.com/Gaming-Monitor/SubCategory/ID-3743/Page-{i+1}"
        all_links+=scrape_newegg_page(page_url)
        if len(all_links)>500:
            break
    products_info = []
    for link in all_links:
        product_info = scrape_product_info(link)
        print(product_info)
        time.sleep(random.uniform(1,3))
        if product_info:
            products_info.append(product_info)
        else:
            print(link)
    print(f" Total links: {len(all_links)}, total products: {len(products_info)}")
    save_to_csv(products_info, "newegg_products.csv")
    driver.quit()

def scrape_product_info(product_URL):
    success = get_product_page(product_URL)
    if success:
        try:
            product_title = driver.find_element(By.CLASS_NAME, "product-title").text
        except Exception as e:
            return None
        description = ""
        try:
            bullets = driver.find_elements(By.CSS_SELECTOR, ".product-bullets ul li")
            for bullet in bullets:
                description += f'{bullet.text} ,'
        except Exception as e:
            description = ""

        try:
            seller_element = driver.find_element(By.CSS_SELECTOR, ".product-seller-sold-by strong")
            seller_name = seller_element.text
        except Exception as e:
            seller_name = ""


        try:
            price_element = driver.find_element(By.CSS_SELECTOR, ".price-current strong")
            price_value = price_element.text
            price_cents = driver.find_element(By.CSS_SELECTOR, ".price-current sup").text
            full_price = f"${price_value}{price_cents}"
        except Exception as e:
            full_price = ""


        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, ".product-rating i.rating")
            rating_title = rating_element.get_attribute("title")
            rating_value = rating_title.split(" ")[0]
        except Exception as e:
            rating_value = ""


        try:
            img_element = driver.find_element(By.CSS_SELECTOR, ".product-view-img-original")
            img_src = img_element.get_attribute("src")
        except Exception as e:
            img_src = ""



        return {
            "title": product_title,
            "description": description,
            "price": full_price,
            "rating": rating_value,
            "seller": seller_name,
            "image": img_src
        }
    else:
        return None


def scrape_newegg_page(page):
    driver.get(page)
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    links = soup.find_all('a', class_='item-img')
    product_links = [link['href'] for link in links if '/p' in link['href']]

    return product_links


def save_to_csv(products, csv_file_name="newegg_products.csv"):

    with open(csv_file_name, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ["title", "description", "price", "rating", "seller", "image"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for product in products:
            writer.writerow(product)

    print(f"CSV file '{csv_file_name}' has been created successfully.")

if __name__ == "__main__":
    scrape_pages()

