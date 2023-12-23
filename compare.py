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

def scrape_selenium():
    # put url here
    url = ""
    # put url here
    driver = webdriver.Chrome()
    driver.get(url)
    # opening the url with selenium
    
    # Handling cookies consent
    consent_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="CookieBoxSaveButton"]')))
    consent_button.click()
    
    # Handling annoying popup
    annoying_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Blockieren")]')))
    annoying_button.click()

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
        # getting all the data
        with open("prices.json", "r") as prices:
            prices_list = json.loads(prices.read())
        phone_price = prices_list.get(phone_name, "0")
        monthly_price = monthly_price.replace(".", "").replace("€", "").replace(",", ".").strip()
        onetime_price = onetime_price.replace(".", "").replace("€", "").replace(",", ".").strip()
        phone_price = phone_price.replace("€", "").replace(".", "").replace(",", ".").strip()
        Final_price = (24 * float(monthly_price) + float(onetime_price)) - float(phone_price)
        Final_price = Final_price / 24
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
