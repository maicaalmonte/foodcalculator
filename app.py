from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import os

# Initialize Flask app with template folder explicitly set
app = Flask(__name__, template_folder='public')

# Debug: Print the current working directory
print("Working directory:", os.getcwd())

# Function to fetch data from OpenFoodFacts API
def fetch_all_food_data(limit=100000, page=1):
    """
    Fetches product data from OpenFoodFacts API
    """
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms=&search_simple=1&action=process&json=true&page={page}&page_size={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data.get('products', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

# Function to extract relevant data (nutritional values and other attributes)
def extract_nutritional_data(products_data):
    """
    Extracts relevant columns from the OpenFoodFacts product data
    """
    rows = []
    for product in products_data:
        # Extract product-level data
        row = {
            'product_name': product.get('product_name', 'N/A'),
            'ingredients_text': product.get('ingredients_text', 'N/A'),
            'brands': product.get('brands', 'N/A'),
            'quantity': product.get('quantity', 'N/A'),
            'code': product.get('code', 'N/A'),
        }

        # Flatten the nutritional data
        nutriments = product.get('nutriments', {})
        row.update({
            key: nutriments.get(key, 0) for key in [
                'energy-kcal_100g', 'fat_100g', 'carbohydrates_100g',
                'sugars_100g', 'proteins_100g', 'salt_100g',
                'fiber_100g', 'vitamin-a_100g', 'vitamin-c_100g',
                'calcium_100g', 'iron_100g', 'magnesium_100g',
                'potassium_100g', 'sodium_100g', 'zinc_100g',
                'phosphorus_100g', 'vitamin-d_100g', 'vitamin-e_100g',
                'vitamin-k_100g', 'folate_100g', 'vitamin-b12_100g',
                'vitamin-b6_100g', 'copper_100g', 'manganese_100g', 'selenium_100g'
            ]
        })
        rows.append(row)

    # Create DataFrame from the list of rows
    products_df = pd.DataFrame(rows)
    return products_df

# Flask Routes
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return "Template not found. Ensure the 'templates/index.html' file exists.", 500

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        # Validate inputs
        page = int(request.json.get('page', 1))
        limit = int(request.json.get('limit', 100))
        category = request.json.get('category', '')
        brand = request.json.get('brand', '')
        product_name = request.json.get('product_name', '')

        if page < 1 or limit < 1:
            return jsonify({'status': 'error', 'message': 'Page and limit must be positive integers.'}), 400

        # Fetch data from the OpenFoodFacts API
        products_data = fetch_all_food_data(limit=limit, page=page)

        if not products_data:
            return jsonify({'status': 'error', 'message': 'No products were fetched. Please try again.'})

        # Extract and process the nutritional data
        products_df = extract_nutritional_data(products_data)

        # Apply filters
        if category:
            products_df = products_df[products_df['categories_tags'].str.contains(category, na=False)]
        if brand:
            products_df = products_df[products_df['brands'].str.contains(brand, na=False)]
        if product_name:
            products_df = products_df[products_df['product_name'].str.contains(product_name, na=False)]

        data_json = products_df.to_dict(orient='records')  # Convert DataFrame to a list of dictionaries

        return jsonify({'status': 'success', 'data': data_json})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)