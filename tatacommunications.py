from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time 
import csv
from datetime import datetime

import warnings
        
warnings.filterwarnings("ignore")

def get_options():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--incognito")
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    return options


def check_dismiss_flag(driver):
    """
    this is used to dismiss alert in run time
    """
    try:
        element = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//a[contains(text(),"Dismiss")]')))            
        if element:
            element.click()
        return True
    except:pass

def get_inner_text(selector, xpath, elements=None):
    """
    return text in the selector object
    """
    try:
        if elements:
            return [i.text for i in selector.find_elements_by_xpath(xpath)]
        else:
            for x in xpath.split('|'):
                try:
                    return selector.find_element_by_xpath(x).text
                except:pass
    except:
        return [] if elements else ''

def get_item_data(item, writer):
    """
    return list of rows for one item
    """
    try:
        element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH,'//h3[contains(@class,"menuItemModal-name")]')))            
        # Category	ItemName	Description	ItemPrice	OptionName	Options	OptionPrice
        item_name = get_inner_text(item, '//h3[contains(@class,"menuItemModal-name")]')
        itemPrice = get_inner_text(item, '//h5[contains(@class,"menuItemModal-price")]')
        description = get_inner_text(item, '//p[contains(@class,"menuItemModal-description")]')
        optionName =get_inner_text(item, '//span[contains(@class,"menuItemModal-choice-name")]')
        choice_option_descriptions = get_inner_text(item, '//span[contains(@class,"menuItemModal-choice-option-description")]',elements=True)
        
        category = get_inner_text(item, './../../../../../../../..//h3[contains(@class,"menuSection-title")] | //h3[contains(@class,"menuSection-title")] | ./../../../../../../../..//span[contains(@class,"menuVirtualizedSection")] | ./../../../../../div[@class="menuItem-container"]//button//h3 | ./../../../../../../../..//h3[contains(@class,"menuSection-title")]')
        # category = get_inner_text(item, './/h3[contains(@class,"menuSection-title")] | ./../../../../../../../..//h3[contains(@class,"menuSection-title')
        if not category:
            category = ''.join([i.text for i in item.parent.find_elements_by_xpath('//h3[contains(@class,"menuSection-title")]')])        
        if choice_option_descriptions:
            for choice_option in choice_option_descriptions:
                if '+' in choice_option:
                    option, optionPrice = choice_option.split('+')
                else:
                    option, optionPrice = choice_option, ''
                writer.writerow({
                    "Category":category,
                    "ItemName":item_name,
                    "Description":description,
                    "ItemPrice": itemPrice,
                    "OptionName": optionName,
                    "Options": option,
                    "OptionPrice": optionPrice,
                })
        else:
            writer.writerow({
                    "Category":category,
                    "ItemName":item_name,
                    "Description":description,
                    "ItemPrice": itemPrice,
                    "OptionName": optionName,
                    "Options": '',
                    "OptionPrice": '',
                })
    except:
        yield {}

def process_item(item,index,driver, writer, retry=0):   
    """
    framing each row by extracting text from HTML using XPATH
    """
    # print(items[index].text)
    try:
        check_dismiss_flag(driver)
        items[index].click()
        check_dismiss_flag(driver)
        data = get_item_data(items[index], writer)
        time.sleep(4)
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '//button[@data-testid="close-add-item-modal"]')))            
        if element:
            element.click()
    except Exception as e:
        if retry < 20:
            time.sleep(3)
            retry = retry+1
            process_item(item,index,driver, writer, retry=retry)
        else:
            check_dismiss_flag(driver)


if __name__ == '__main__':
    """
    creating driver object
    creating new file object
    ....

    """
    options = get_options()

    with webdriver.Chrome('/home/saai/Desktop/FyersTrading/driver/chromedriver',options=options) as driver:
        driver.maximize_window()
        csvfile = open(f'outPut_{datetime.now().strftime("%m/%d/%Y%H:%M:%S")}.csv', 'w')
        fieldnames = ["Category","ItemName","Description","ItemPrice","OptionName","Options","OptionPrice"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        time.sleep(4)
        driver.get('https://www.grubhub.com/restaurant/the-mad-greek-cafe-of-charlotte-5011-south-blvd-charlotte/2159864')
        time.sleep(8)

        index = 0
        items = []
        flag = True

        while flag:
            try:
                print(len(items), index)
                items = driver.find_elements_by_xpath('//div[@data-testid="restaurant-menu-item"][@role="button"]//div[contains(@id,"menuItem")]')        
                for i in range(index, len(items)-1):        
                    print(len(items), index)
                    process_item(items[index], index, driver, writer) 
                    index=index+1
                            
                driver.execute_script("arguments[0].scrollIntoView();",items[index-2])  
            except IndexError:
                pass

        csvfile.close()
        driver.close()
