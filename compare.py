from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import time
import os
import re
import json 


def main():
    html_cache()

def read_dictionary_from_file():
    with open("price_cache.txt", 'r', encoding="utf-8") as file:
        data = json.loads(file.read())
        return data
    
def cache_price(phone_name):
    price_cache_path = "price_cache.txt"
    price_cache = read_dictionary_from_file()
    price = get_price(phone_name)
    price_cache[phone_name] = price
    with open(price_cache_path, 'w') as file:
        json.dump(price_cache, file, indent=4)
    return price

def check_price_cache(phone_name):
    with open("price_cache.txt", 'r', encoding="utf-8") as file:
        data = json.loads(file.read())
        if phone_name in data:
            return data[phone_name]
        else:
            return cache_price(phone_name)

def get_price(phone_name):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    base_url = f"https://www.zoxs.de/ankauf_suche.html?q={phone_name}"
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAccept"]')))
    cookie_button.click()
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    grid = soup.findAll(class_="col-6 col-md-4 px-1 text-center offer-tile")
    for item in grid:
        if item == "\n":
            continue
        extracted_name = item.find(class_="bottom").text
        phone_name_split = [*phone_name]
        extracted_name_split = [*extracted_name]
        if all(letter in extracted_name_split for letter in phone_name_split):
            link_element = item.find(class_="text-dark nav-link p-0 rounded offer-tile-klickarea")
            phone_sell_url = "https://www.zoxs.de/" + link_element["href"]
            driver.get(phone_sell_url)
            soup2 = BeautifulSoup(driver.page_source, "html.parser")
            try:
                price_element = soup2.find(id="productPrice", class_="h2 mb-0 text-grey-5 font-size-md")
                price_element2 = price_element.find('input', {'name': 'gesamt'})
                value = price_element2["value"]
                print(value)
                print(phone_name)
                price = float(value.replace(' EUR', '').replace(",","."))
                if type(price) != float:
                    return 0
                return price
            except Exception as error:
                print(error)
                return 0
        else:
            print("\n")
            print(phone_name)
            print("Link: " + f"https://www.zoxs.de/ankauf_suche.html?q={phone_name}")
            manual_price = float(input("Manuelle Preiseingabe: ").replace(",","."))
            return manual_price
            pass
      
def scrape_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # put url here
    url = "https://www.handyhase.de/handy-mit-vertrag/#data-volume=5&download-speed=99999&monthly-costs=99999&onetimecosts=99999&device-rom=99999&phone-options=99999&contract-period=99999&cancelable-automatic-data-renewal=99999&manufacturerId=99999&classification=99999&providerId=99999&shopId=99999&sort=4&young=1&data5g=0&combined=1&esim=0&multicard=0&landline-number=0&device5g=0&cellular-network=1%2C3%2C5"
    # put url here
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    # opening the url with selenium
    
    # Handling cookies consent
    consent_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CookieBoxSaveButton"]')))
    consent_button.click()
    
    
    # Handling annoying popup
    

    while True:
        try:
            # Clicking on the "Load More" button
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="infinite-reload-compare-button"]')))
            button.click()
            # Adding a pause to allow time for the new content to load
            time.sleep(3) 
        except TimeoutException:
            print("Loading complete or error occurred.")
            break
        except :
            try:
                annoying_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Blockieren")]')))
                annoying_button.click()
            except TimeoutException:
                pass

    return driver.page_source

def html_cache(): #check if html is cached if not cache it
    if os.path.getsize("cache.html") < 1:
        html = scrape_selenium()
        with open("cache.html", "w", encoding="utf-8") as file:
            file.write(html)
    else:
        with open("cache.html", "r", encoding="utf-8") as file:
            html = file.read()
    soup_process(html)
        
def soup_process(page_source): #function to compare pricess
    last_price = 999
    last_data = 0
    last_phone_name = "test"
    soup = BeautifulSoup(page_source, "html.parser")
    grid = soup.find(id="collapse-compare", attrs={"data-type": "phone-and-tariff"})
    elements = grid.contents
    for element in elements:
        if element == "\n":
            continue
        price_wrapper = element.find("div", class_="compare-item__prices-wrapper pricingdetail")
        wrapper_parent = price_wrapper.find("div", class_="compare-item__prices")
        price_wrapper_child = wrapper_parent.find("div", class_="compare-item__regular-prices")
        price_wrapper_child_list = price_wrapper_child.find_all("div", class_="compare-item__regular-price-wrapper")
        price_wrapper_child1 = price_wrapper_child_list[0]
        price_wrapper_child2 = price_wrapper_child_list[1]
        monthly_price = price_wrapper_child1.find("div", class_="compare-item__regular-price").text
        onetime_price = price_wrapper_child2.find("div", class_="compare-item__regular-price").text
        head_wrapper = element.find("div", class_="compare-item__head-wrapper")
        meta_wrapper = head_wrapper.find("div", class_="compare-item__meta-wrapper")
        phone_name = meta_wrapper.find("div", class_="compare-item__meta-device").text
        cellular_wrapper = element.find("div", class_="compare-item__usp-wrapper")
        cellular_wrapper_child = cellular_wrapper.find("div", class_="compare-item__usp-item -data")
        if cellular_wrapper_child is None:
            cellular_data = 0
        else:
            cellular_data = cellular_wrapper_child.text
            cellular_data_match = re.search(r'\b(\d+)\s*GB\b', cellular_data)
            cellular_data = float(cellular_data_match.group(1)) if cellular_data_match else 0
        phone_name = re.sub(r'\([^)]*\)', '', phone_name)
        phone_name = phone_name.strip()
        Final_price = check_price_cache(phone_name)
        # getting all the data
        # with open("prices.json", "r") as prices:
        #     prices_list = json.loads(prices.read())
        # phone_price = prices_list.get(phone_name, "0")
        # monthly_price = monthly_price.replace(".", "").replace("€", "").replace(",", ".").strip()
        # onetime_price = onetime_price.replace(".", "").replace("€", "").replace(",", ".").strip()
        # phone_price = phone_price.replace("€", "").replace(".", "").replace(",", ".").strip()
        # Final_price = (24 * float(monthly_price) + float(onetime_price)) - float(phone_price)
        # Final_price = Final_price / 24
        #cleaning the data
        if 4 > Final_price and cellular_data > last_data:
            last_data = cellular_data
            last_price = Final_price
            last_phone_name = phone_name
            contract_link = element.find("a", class_="compare-item__cta btn green")
            # basicly a filter
    print(last_price)
    print(last_phone_name)
    print(contract_link["href"])
    # print the results

main()
