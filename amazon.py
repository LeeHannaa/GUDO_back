# class="a-fixed-left-grid-col a-col-left" -> 별점들을 감싸는 div
# class="a-align-center a-spacing-none" -> 별점 5이상인것 비중
# class="a-section a-spacing-none a-text-right aok-nowrap" -> 별점 퍼센트

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

@app.route('/amazon/bestsellers', methods=['GET'])
def get_bestsellers():
    url = 'https://www.amazon.com/bestsellers'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    html = BeautifulSoup(response.text, 'html.parser')

    categories = html.select('div.a-column.a-span8')
    categories_list = [categorie.text.strip() for categorie in categories]
    categories_list.reverse()

# Debugging: Check if categories are extracted correctly
    print("Categories List:", categories_list)
    
    bestsellers_data = []
    divs = html.select('div.a-carousel-row-inner')
    
    for div in divs:
        if categories_list:
            current_category = categories_list.pop()  # Get the current category
            
            # Initialize the dictionary for this category with an empty list for products
            category_data = {
                "category": current_category,
                "products": []
            }

        lis = div.select('li.a-carousel-card')
        
        for li in lis:
            num = li.select_one('span.zg-bdg-text').text.strip()
            title = li.select('a.a-link-normal')[1].text.strip()
            product_url = 'https://www.amazon.com' + li.select('a.a-link-normal')[1]['href']
            rating = li.select('a.a-link-normal')[2].text.strip()

            # Request individual product page to get 5-star rating percentage
            product_page = requests.get(product_url, headers=headers)
            product_html = BeautifulSoup(product_page.text, 'html.parser')
            
            # Locate and extract the 5-star rating percentage
            five_star_percentage = "Not found"
            ratings = product_html.select("ul#histogramTable li.a-align-center.a-spacing-none")
            if ratings:
                five_star_div = ratings[0].select_one('div.a-section.a-spacing-none.a-text-right.aok-nowrap')
                if five_star_div:
                    five_star_percentage = five_star_div.select_one('span').text.strip()

            # Add the product data to the list
            category_data["products"].append({
                "num": num,
                "title": title,
                "rating": rating,
                "5stars": five_star_percentage
            })
            
            # Adding a small delay to avoid Amazon's anti-scraping mechanisms
            time.sleep(1)
        
        bestsellers_data.append(category_data)

    # Return data as JSON
    return jsonify(bestsellers_data)

if __name__ == '__main__':
    app.run(debug=True)
