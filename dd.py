import requests
import pandas as pd
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

API_KEY = ""
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

LOCATIONS = [
    "Los Angeles, CA",
    "Seattle, WA",
    "Miami, FL",
    "Dallas, TX",
    "Denver, CO",
    "Washington, D.C.",
    "Boston, MA",
    "Phoenix, AZ",
    "Atlanta, GA",
    "Orlando, FL",
    "San Diego, CA"
]
CATEGORIES = ["marketing", "advertising", "web_design"] 

BASE_URL = "https://api.yelp.com/v3/businesses/search"

CSV_FILE = "ccc.csv"

def get_yelp_businesses(location, categories, limit=50, max_results=240):
    businesses = []
    for category in categories:
        offset = 0
        while offset < max_results:
            params = {
                "location": location,
                "categories": category,
                "limit": limit,
                "offset": offset
            }
            response = requests.get(BASE_URL, headers=HEADERS, params=params)

            if response.status_code != 200:
                print(f"Greška kod kategorije {category}: {response.json()}")
                break

            data = response.json()
            business_list = data.get("businesses", [])

            if not business_list:
                break  

            businesses.extend(business_list)
            offset += limit

            time.sleep(1)

    return businesses

def extract_relevant_data(businesses):
    extracted_data = []
    for biz in businesses:
        email = None
        
        extracted_data.append({
            "id": biz.get("id"),
            "name": biz.get("name"),
            "category": ", ".join([c["title"] for c in biz.get("categories", [])]),
            "rating": biz.get("rating"),
            "review_count": biz.get("review_count"),
            "address": " ".join(biz.get("location", {}).get("display_address", [])),
            "phone": biz.get("phone"),
            "url": biz.get("url"),
        })
    return extracted_data

def save_to_csv(data, filename):
    new_data = pd.DataFrame(data)

    try:
        existing_data = pd.read_csv(filename)
        combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=["id"])
    except FileNotFoundError:
        combined_data = new_data

    combined_data.to_csv(filename, index=False)
    print(f"Podaci sačuvani u {filename}")

def setup_browser():
    driver_path = r"E:\chromedrvr\chromedriver.exe" 
    options = Options()
    options.headless = False  
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    return driver

def scrape_page(url, driver):
    driver.get(url)
    time.sleep(3)  
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    data = {}

    business_name = soup.find('h1')  
    if business_name:
        data['Business Name'] = business_name.text.strip()

    return data

def save_to_excel(data_list, filename):
    df = pd.DataFrame(data_list)
    df.to_excel(filename, index=False)

def main():
    all_businesses = []
    for location in LOCATIONS:
        businesses = get_yelp_businesses(location, CATEGORIES)
        filtered_data = extract_relevant_data(businesses)
        save_to_csv(filtered_data, CSV_FILE)
        all_businesses.extend(filtered_data)

    driver = setup_browser()
    urls = [
        "https://www.example1.com",
        "https://www.example2.com",  
    ]
    
    all_data = []
    
    for url in urls:
        page_data = scrape_page(url, driver)
        if page_data: 
            all_data.append(page_data)
    
    save_to_excel(all_data, 'scraped_data.xlsx')
    driver.quit()

if __name__ == "__main__":
    main()

