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
    res = requests.get(url, headers=headers, params=params)
    if res.status_code==429:
      time.sleep(5)
      continue
    if res.status_code != 200:#Added Fix
      return None
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
      cpu = li_items[0].text.strip() if len(li_items) > 0 else None
      ram = li_items[1].text.strip() if len(li_items) > 1 else None
      OS = li_items[2].text.strip() if len(li_items) > 2 else None
      SSD = li_items[3].text.strip() if len(li_items) > 3 else None
      Display = li_items[4].text.strip() if len(li_items) > 4 else None
      Warranty = li_items[5].text.strip() if len(li_items) > 5 else None
      discount_tag = product.find('div', class_ = 'HQe8jr')
      if not(name_tag and actual_price_tag and discnt_price_tag):
        continue
      try:
        name = name_tag.text.strip()
        actual_price = clean_price(actual_price_tag.text)
        discnt_price = clean_price(discnt_price_tag.text)
        rating = float(rating_tag.text.strip()) if rating_tag else None
        discount = discount_tag.text.strip() if discount_tag else None
        raw_data.append({
        'Name': name,
        'Actual_Price': actual_price,
        'Discount_Price': discnt_price,
        'Rating': rating,
        'Discount': discount,
        'CPU': cpu,
        'Ram': ram,
        'OS': OS,
        'SSD': SSD,
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
