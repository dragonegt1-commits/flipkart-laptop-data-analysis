import requests
from bs4 import BeautifulSoup
import pandas as pd 
import time
"""
Flipkart Laptop Scraper & Analyzer

- Scrapes laptop data
- Cleans and filters products under ₹50,000
- Finds top cheapest and highest rated laptops
- Saves results to CSV

Tech: Python, BeautifulSoup, pandas
"""
def get_ssd_from_name(string,item):#Made this fix to fetch data from the name of the product
  first = string.lower().find(item)
  second = string.lower().find(item)
  item_from_data = string[second + 2:second+9].replace('/','').strip() + ' Storage'
  return item_from_data



def clean_name(string):#To get rid of useless data
  result = string.split('- (')[0].strip()
  return result
  
  
def clean_price(value):
    return float(value.replace('₹', '').replace(',', '').strip())

def get_data():
  raw_data = []
  for page in range(1,6):
    url = "https://www.flipkart.com/search"
    headers = {
      "User-Agent": "Mozilla/5.0"
      }
    params = {
    'q': 'laptops',
    'page': page
    }
    try:
      res = requests.get(url, headers=headers, params=params)
      res.raise_for_status()
      if res.status_code==429:
        time.sleep(5)
        continue
      if res.status_code != 200:#Fix to skip over this 
          print(f"Skipping page {page}")
          continue

    except requests.exceptions.RequestException as e:
      print(f"Error fetching data: {e}")
      time.sleep(1)
    soup = BeautifulSoup(res.text,'html.parser')
    products = soup.find_all('div', class_ = 'lvJbLV')# class for products
    for product in products:
      name_tag = product.find('div', class_ = 'RG5Slk')
      actual_price_tag = product.find('div', class_ = 'gxR4EY')
      discnt_price_tag = product.find('div', class_ = 'hZ3P6w')
      rating_tag = product.find('div', class_= 'MKiFS6')
      specs_container = product.find('ul')
      li_items = specs_container.find_all('li') if specs_container else []
      cpu = ram = OS = SSD = Display = Warranty = None
#Fix added so that the different columns dont have some other values and rather have none
      for li in li_items:
        text = li.text.strip().lower()
        if "processor" in text or "core" in text:
            cpu = li.text.strip()
        elif 'gb' in text and 'ddr' in text and 'ram' in text:
            ram = li.text.strip()
        elif any(ssd_word in text for ssd_word in ['ssd','gb emmc storage','storage']) and ('gb' in text or 'tb' in text):
            SSD = li.text.strip()
        elif "inch" in text or "display" in text:
            Display = li.text.strip()
        elif any(os_word in text for os_word in ["windows", "dos", "linux", "ubuntu", "chrome", "mac", "android"]):
            OS = li.text.strip()
        elif "warranty" in text or 'damage protection' in text:
            Warranty = li.text.strip()
      if OS is None:
        OS = "Not Specified"
      if SSD is None:
        SSD = "Not Specified"
      if Warranty is None:
        Warranty = "Not Specified"
      discount_tag = product.find('div', class_ = 'HQe8jr')
      if not(name_tag and actual_price_tag and discnt_price_tag):
        continue
      try:
        name = name_tag.text.strip()
        actual_price = clean_price(actual_price_tag.text)
        discnt_price = clean_price(discnt_price_tag.text)
        rating = float(rating_tag.text.strip()) if rating_tag else None
        discount = discount_tag.text.strip() if discount_tag else None
        ssd_info = get_ssd_from_name(name,'gb')
        if 'Not Specified' in SSD:
          SSD = SSD.replace('Not Specified','')
          new_ssd = ssd_info + SSD
        else:
          continue
        cleaned_name = clean_name(name)
        raw_data.append({
        'Name': cleaned_name,
        'Actual_Price': actual_price,
        'Discount_Price': discnt_price,
        'Rating': rating,
        'Discount': discount,
        'CPU': cpu,
        'Ram': ram,
        'OS': OS,
        'SSD': new_ssd,
        'Display': Display,
        'Warranty': Warranty
        })
      except Exception as e:
        print('Error:',e)
        continue
  return raw_data if raw_data else None

def filtered_data(details):
  filter_data = [p for p in details if p['Discount_Price'] < 50000]
  return filter_data if filter_data else None

def data_format(information):
  df = pd.DataFrame(information)
  df = df.dropna(subset=["Rating", "Discount_Price"]) #Removes missing values where needed
  top_rated = df.sort_values(by="Rating", ascending=False).head(5)#For top rated
  top_cheapest = df.sort_values(by="Discount_Price", ascending=True).head(5)#For top cheapest
  top_rated["Category"] = "Top Rated"
  top_cheapest["Category"] = "Top Cheapest"
  final_df = pd.concat([top_rated, top_cheapest])
  final_df = final_df.sort_values(by="Discount_Price")#Sorting Before saving
  final_df.to_csv("Cleaned_Ecommerce_Data.csv", index=False)#Logic to add both top rated and cheapest in the same csv file
  print('Saving data to Cleaned_Ecommerce_Data.csv!\n')
  return df

def main():
  print('Fetching Data...')
  time.sleep(1)
  info = get_data()
  if info is None:
    print("Failed to fetch data")
    return
  data = filtered_data(info)
  prod = data_format(data)
  print('Data Fetching completed!!\n')

if __name__ == '__main__':
  main()
