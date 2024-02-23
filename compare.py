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
import cProfile


def main(filter_price):
    return html_cache(filter_price)

def get_path(path):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    # Construct paths to the files
    full_path = os.path.join(current_directory, path).replace("/", "\\")
    return full_path
    


#loads the json directory from the file
def read_dictionary_from_file():
    with open(get_path("cache/price_cache.txt"), 'r', encoding="utf-8") as file:
        data = json.loads(file.read())
        return data
# gets the price and than writes it to the cache file   
def cache_price(phone_name):
    price_cache_path = get_path("cache/price_cache.txt")
    price_cache = read_dictionary_from_file()
    price = get_price(phone_name)
    price_cache[phone_name] = price
    with open(price_cache_path, 'w') as file:
        json.dump(price_cache, file, indent=4)
    return price

#check if price is cached else cache it
def check_price_cache(phone_name):
    with open(get_path("cache/price_cache.txt"), 'r', encoding="utf-8") as file:
        data = json.loads(file.read())
        if phone_name in data:
            return data[phone_name]
        else:
            return cache_price(phone_name)

def get_price(phone_name):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    html_phone_name = phone_name.replace(" ", "%20")
    base_url = f"https://www.zoxs.de/ankauf_suche.html?q={html_phone_name}"
    driver = webdriver.Chrome(options=options)
    driver.get(base_url)
    #handling cookie button
    cookie_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btnAccept"]')))
    cookie_button.click()
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    grid = soup.findAll(class_="col-6 col-md-4 px-1 text-center offer-tile")
    #checking every result
    if len(grid) < 1:
        return 0
    for item in grid:
        if item == "\n":
            continue
        extracted_name = item.find(class_="bottom").text
        phone_name_split = [*phone_name]
        extracted_name_split = [*extracted_name]
        pass
        #check if result matches the phone name
        if all(letter in extracted_name_split for letter in phone_name_split):
            link_element = item.find(class_="text-dark nav-link p-0 rounded offer-tile-klickarea")
            phone_sell_url = "https://www.zoxs.de/" + link_element["href"]
            print(phone_sell_url)
            driver.get(phone_sell_url)
            soup2 = BeautifulSoup(driver.page_source, "html.parser")
            try:
                price_element = soup2.find(id="productPrice", class_="h2 mb-0 text-grey-5 font-size-md")
                price_element2 = price_element.find('input', {'name': 'gesamt'})
                value = price_element2["value"]
                if value == None:
                    pass
                print(value)
                print(phone_name)
                price = float(value.replace(' EUR', '').replace(",","."))
                if type(price) != float:
                    return 0
                return price
            except Exception as error:
                print(error)
                return 0
            #manually adding prices that couldnt be resolved by the code because the phone name is misleading
        else:
            print("\n")
            print(phone_name)
            print("Link: " + f"https://www.zoxs.de/ankauf_suche.html?q={html_phone_name}")
            manual_price = float(input("Manuelle Preiseingabe: ").replace(",","."))
            return manual_price
            pass
def get_html(url):   
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    #wait 6 seconds for the direction to the deal site
    time.sleep(6)
    return driver.page_source
def scrape_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')

    # put url here
    url = ""
    # put url here
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    # opening the url with selenium
    
    # Handling cookies consent
    consent_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="BorlabsCookieBox"]/div/div/div[2]/div/div/div[2]/div/div/div/div/div/div[1]/div/div[2]/div/div[2]/button')))
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


def html_cache(filter_price): #check if html is cached if not cache it
    skip_element = []
    if os.path.getsize(get_path("cache/cache.html")) < 1:
        html = scrape_selenium()
        with open(get_path("cache/cache.html"), "w", encoding="utf-8") as file:
            file.write(html)
        return soup_process(html, skip_element, filter_price)
    else:
        with open(get_path("cache/cache.html"), "r", encoding="utf-8") as file:
            html = file.read()
    return soup_process(html, skip_element, filter_price)
       
def soup_process(page_source, skip_element, filter_price): #function to compare pricess
    last_price = 9999
    last_data = 0
    last_phone_name = "test"
    soup = BeautifulSoup(page_source, "html.parser")
    grid = soup.find(id="collapse-compare", attrs={"data-type": "phone-and-tariff"})
    elements = grid.contents
    elements = [element for element in elements if element != "\n"]
    if skip_element != None:
            pass
    for element in elements:
        contract_link = element.find("a", class_="compare-item__cta btn green")
        contract_url = contract_link["href"]
        if len(skip_element) > 0:
            if contract_url in skip_element:
                continue
        
        price_wrapper = element.find("div", class_="compare-item__prices-wrapper pricingdetail")
        wrapper_child = price_wrapper.find("div", class_="compare-item__regular-average-wrapper")
        average_montly_price = wrapper_child.find("div", class_="compare-item__regular-average-price").text
        average_montly_price = numbers = re.findall(r'\d[\d,.]*', average_montly_price)
        average_montly_price = float(numbers[0].replace(',', '.')) if numbers else None
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
        # getting all the data
        phone_price = check_price_cache(phone_name)
        Final_price = (average_montly_price * 24 - float(phone_price)) / 24
        # if Final_price < last_price:
        # basicly a filter
        if filter_price == 0:
            if Final_price < last_price:
                last_data = cellular_data
                last_price = Final_price
                last_contract_url = contract_url
                last_phone_name = phone_name
        else:
            if Final_price <= filter_price and cellular_data > last_data:
                last_data = cellular_data
                last_price = Final_price
                last_contract_url = contract_url
                last_phone_name = phone_name
    
    if "Refurbished" in str(get_html(last_contract_url)):
        print("\n" + last_contract_url)
        answer = input("Refurbished?(ja oder nein): ").lower()
        if answer == "ja":
            #recursive call to filter out refurbished devices
            skip_element.append(last_contract_url)
            return soup_process(page_source, skip_element) 
    
    return [last_price,last_phone_name,last_contract_url]

    
if __name__ == "__main__":
    main()

