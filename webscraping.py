from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time
import re

def scrape_rightmove():
    driver = webdriver.Chrome()  # Chrome driver yolunu belirtin
    properties = []

    # Fiyat aralığı
    min_price = 5500001 #1850001
    max_price = 20000000 #20000000

    index = 0
    while True:
        driver.get(f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E87490&minPrice={min_price}&maxPrice={max_price}&index={index}")

        try:
            # Sayfanın tam olarak yüklenmesini beklemek gerekebilir
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'propertyCard')))
        except:
            # Eğer sayfa yüklenmezse veya daha fazla veri yoksa döngüyü sonlandır
            break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.find_all('div', class_='propertyCard')

        if not listings:
            # Eğer listede daha fazla emlak yoksa döngüyü sonlandır
            break

        for listing in listings:
            try:
                # Temel Bilgiler
                price = listing.find('div', class_='propertyCard-priceValue').text.strip() if listing.find('div', class_='propertyCard-priceValue') else 'N/A'
                address = listing.find('address', class_='propertyCard-address').text.strip() if listing.find('address', class_='propertyCard-address') else 'N/A'

                link = listing.find('a', class_='propertyCard-link')
                if link:
                    property_url = "https://www.rightmove.co.uk" + link['href']

                    # Ilana tıklayarak detaylı bilgi almak
                    driver.get(property_url)
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'info-reel')))
                    except:
                        continue

                    property_soup = BeautifulSoup(driver.page_source, 'html.parser')

                    # PROPERTY TYPE, BEDROOMS, BATHROOMS, SIZE bilgilerini al
                    property_type = 'N/A'
                    bedrooms = 'N/A'
                    bathrooms = 'N/A'
                    size = 'N/A'

                    info_reel = property_soup.find('dl', {'id': 'info-reel'})
                    if info_reel:
                        info_items = info_reel.find_all('div', class_='_3gIoc-NFXILAOZEaEjJi1n')
                        for item in info_items:
                            label = item.find('span', class_='ZBWaPR-rIda6ikyKpB_E2')
                            value = item.find('p', class_='_1hV1kqpVceE9m-QrX_hWDN')
                            if label and value:
                                label_text = label.text.strip().lower()
                                if 'bedroom' in label_text:
                                    bedrooms = re.search(r'\d+', value.text.strip()).group() if re.search(r'\d+', value.text.strip()) else 'N/A'
                                elif 'bathroom' in label_text:
                                    bathrooms = re.search(r'\d+', value.text.strip()).group() if re.search(r'\d+', value.text.strip()) else 'N/A'
                                elif 'size' in label_text or 'sq ft' in label_text:
                                    size = value.text.strip()
                                elif 'property type' in label_text:
                                    property_type = value.text.strip()

                    # Eğer bu property zaten listede varsa eklemeyi atla
                    if [address, price, property_type, bedrooms, bathrooms, size] not in properties:
                        properties.append([address, price, property_type, bedrooms, bathrooms, size])
            except AttributeError:
                continue

        # "Next" butonunu kontrol et
        next_button = soup.find('button', {'data-test': 'pagination-next'})
        if not next_button or 'disabled' in next_button.get('class', []):
            break

        # Bir sonraki sayfa için index güncelle
        index += 24

    driver.quit()

    # CSV'ye Kaydet
    with open('9.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Address', 'Price', 'Property Type', 'Bedrooms', 'Bathrooms', 'Size'])
        writer.writerows(properties)

scrape_rightmove()
