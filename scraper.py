import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

# --- Configuration ---
URL = "https://www.myntra.com/handbags-and-bags"

def scrape_myntra_bags():
    # --- WebDriver Initialization (with STEALTH options) ---
    print("Initializing WebDriver for Brave...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    # Anti-detection measures
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    print("WebDriver initialized.")
    driver.get(URL)
    print(f"Opened page: {URL}")

    products_data = []
    page_num = 1
    
    while True:
        print(f"\n--- Scraping Page {page_num} ---")
        
        try:
            # Wait for products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ul.results-base"))
            )
            product_elements = driver.find_elements(By.CSS_SELECTOR, "li.product-base")
            print(f"Found {len(product_elements)} products on this page.")
            
            # --- Data Extraction (No changes needed here) ---
            for product in product_elements:
                try:
                    # ... your data extraction code for each product ...
                    brand = product.find_element(By.CSS_SELECTOR, "h3.product-brand").text
                    product_name = product.find_element(By.CSS_SELECTOR, "h4.product-product").text
                    product_url = product.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
                    category = "Handbags and Bags"
                    price_info = product.find_element(By.CSS_SELECTOR, "div.product-price")
                    sale_price_text, mrp_text = "", ""
                    try:
                        sale_price_text = price_info.find_element(By.CSS_SELECTOR, "span.product-discountedPrice").text
                    except NoSuchElementException:
                        sale_price_text = price_info.find_element(By.CSS_SELECTOR, "span").text
                    try:
                        mrp_text = price_info.find_element(By.CSS_SELECTOR, "span.product-strike").text
                    except NoSuchElementException:
                        mrp_text = sale_price_text
                    try:
                        rating_div = product.find_element(By.CSS_SELECTOR, "div.product-ratingsContainer")
                        rating = rating_div.text.split('|')[0].strip()
                        reviews = rating_div.text.split('|')[1].strip() if '|' in rating_div.text else '0'
                    except NoSuchElementException:
                        rating, reviews = None, None
                    products_data.append({
                        "Brand": brand, "ProductName": product_name, "Category": category,
                        "MRP": mrp_text, "SalePrice": sale_price_text, "Rating": rating,
                        "NumberOfReviews": reviews, "URL": product_url
                    })
                except Exception as e:
                    print(f"Skipping a product due to an error: {e}")
                    continue
                    
        except TimeoutException:
            print("Timed out waiting for products to load. Stopping.")
            driver.save_screenshot('debug_timeout.png')
            break

        try:
            # --- Pagination Logic ---
            # Wait for the 'Next' button to be clickable
            next_button_selector = "li.pagination-next" 
            # This selector may need to be adjusted based on the actual HTML structure
            next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", next_button)
            time.sleep(1) # Wait for scroll to finish

            clickable_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, next_button_selector))
            )
            driver.execute_script("arguments[0].click();", clickable_button)
            page_num += 1

            if page_num > 5:
                print("\nReached the maximum limit of 5 pages. Stopping the scrape.")
                break
        except (NoSuchElementException, TimeoutException):
            print("\nCould not find a clickable 'Next' button. This is the last page.")
            driver.save_screenshot('debug_final_page.png')
            break
                
    driver.quit()
    print("WebDriver closed.")

    df = pd.DataFrame(products_data)
    df.to_csv("myntra_bags_raw.csv", index=False)
    print(f"\nData saved to myntra_bags_raw.csv. Total products scraped: {len(df)}")

if __name__ == "__main__":
    scrape_myntra_bags()