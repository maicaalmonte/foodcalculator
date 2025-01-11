from flask import Flask, render_template_string, request, jsonify
import requests
import pandas as pd
import os

# Initialize Flask app with template folder explicitly set
app = Flask(__name__)

# Debug: Print the current working directory
print("Working directory:", os.getcwd())

# Function to fetch data from OpenFoodFacts API
def fetch_all_food_data(pages=1, limit_per_page=100):
    """
    Fetches product data from OpenFoodFacts API
    """
    all_products = []
    for page in range(1, pages + 1):
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms=&search_simple=1&action=process&json=true&page={page}&page_size={limit_per_page}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            products = data.get('products', [])
            all_products.extend(products)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    return all_products

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
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FoodCalculatour</title>
        <br> Source: https://world.openfoodfacts.org/<br>
        <style>
            body { font-family: Bookman Old Style, sans-serif; margin: 11px; background-color: #d6cce6; }
            input, button { margin: 5px; padding: 10px; font-size: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 11px; background-color: #dbf3bb; }
            table, th, td { border: 1px solid #ccc; }
            th, td { padding: 10px; text-align: left; }
            th { background-color: #f4f4f4; font-weight: bold; }
            .calculator { margin-top: 11px; padding: 10px; background-color: #e6f7ff; border-radius: 5px; }
            .calculator label, .calculator input { margin-right: 10px; }
            .calculator div { display: inline-block; margin-right: 15px; }
            .status { color: red; margin: 10px 0; }
            .nutrition-results { margin-top: 11px; background-color: #e7ffe7; padding: 8px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>NUTRITIONAL VALUE😊</h1>
        <img src="/static/img/cute gif.gif" alt="First GIF" style="display: inline-block; margin-right: 10px;">
        <img src="/static/img/cute gif.gif" alt="Second GIF" style="display: inline-block;">

        <!-- Filters for Data -->
        <div>
            <label for="pages">Pages:</label>
            <input type="number" id="pages" value="1" min="1">

            <label for="limit">Limit per Page:</label>
            <input type="number" id="limit" value="10" min="1">

            <label for="category">Category:</label>
            <input type="text" id="category" placeholder="e.g., Beverages">

            <label for="brand">Brand:</label>
            <input type="text" id="brand" placeholder="e.g., Coca Cola">

            <label for="product_name">Product Name:</label>
            <input type="text" id="product_name" placeholder="e.g., Diet Coke">

            <button onclick="fetchData()">Fetch Data</button>
        </div>

        <!-- Status Message -->
        <div id="status" class="status"></div>

        <!-- Nutrition Calculator -->
        <div class="calculator">
            <div>
                <label for="products">Select Products (comma separated):</label>
                <input type="text" id="products" placeholder="e.g., Coca-Cola, Nutella">
            </div>

            <div>
                <label for="quantities">Quantities (comma separated, e.g., ml or g):</label>
                <input type="text" id="quantities" placeholder="e.g., 100ml, 50g">
            </div>

            <div>
                <button onclick="calculateNutrition()">Calculate Nutrition</button>
            </div>

            <div id="calculated-nutrition" class="nutrition-results" style="display:none;">
                <table id="calculated-nutrition-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Energy (kcal)</th>
                            <th>Fat (g)</th>
                            <th>Carbohydrates (g)</th>
                            <th>Sugars (g)</th>
                            <th>Proteins (g)</th>
                            <th>Salt (g)</th>
                            <th>Fiber (g)</th>
                            <th>Vitamin A (µg)</th>
                            <th>Vitamin C (mg)</th>
                            <th>Calcium (mg)</th>
                            <th>Iron (mg)</th>
                            <th>Magnesium (mg)</th>
                            <th>Potassium (mg)</th>
                            <th>Sodium (mg)</th>
                            <th>Zinc (mg)</th>
                            <th>Phosphorus (mg)</th>
                            <th>Vitamin D (µg)</th>
                            <th>Vitamin E (mg)</th>
                            <th>Vitamin K (µg)</th>
                            <th>Folate (µg)</th>
                            <th>Vitamin B12 (µg)</th>
                            <th>Vitamin B6 (mg)</th>
                            <th>Copper (mg)</th>
                            <th>Manganese (mg)</th>
                            <th>Selenium (µg)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Calculated nutrition data will be injected here -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Data Table -->
        <table id="data-table">
            <thead>
                <tr>
                    <th>Product Name</th>
                    <th>Brand</th>
                    <th>Ingredients</th>
                    <th>Quantity</th>
                    <th>Code</th>
                    <th>Energy (kcal/100g)</th>
                    <th>Fat (g/100g)</th>
                    <th>Carbohydrates (g/100g)</th>
                    <th>Sugars (g/100g)</th>
                    <th>Proteins (g/100g)</th>
                    <th>Salt (g/100g)</th>
                    <th>Fiber (g/100g)</th>
                    <th>Vitamin A (µg/100g)</th>
                    <th>Vitamin C (mg/100g)</th>
                    <th>Calcium (mg/100g)</th>
                    <th>Iron (mg/100g)</th>
                    <th>Magnesium (mg/100g)</th>
                    <th>Potassium (mg/100g)</th>
                    <th>Sodium (mg/100g)</th>
                    <th>Zinc (mg/100g)</th>
                    <th>Phosphorus (mg/100g)</th>
                    <th>Vitamin D (µg/100g)</th>
                    <th>Vitamin E (mg/100g)</th>
                    <th>Vitamin K (µg/100g)</th>
                    <th>Folate (µg/100g)</th>
                    <th>Vitamin B12 (µg/100g)</th>
                    <th>Vitamin B6 (mg/100g)</th>
                    <th>Copper (mg/100g)</th>
                    <th>Manganese (mg/100g)</th>
                    <th>Selenium (µg/100g)</th>
                </tr>
            </thead>
            <tbody>
                <!-- Data will be injected here -->
            </tbody>
        </table>

        <script>
            let productData = [];  // Store product data

            async function fetchData() {
                const pages = document.getElementById('pages').value;
                const limit = document.getElementById('limit').value;
                const category = document.getElementById('category').value;
                const brand = document.getElementById('brand').value;
                const product_name = document.getElementById('product_name').value;
                const statusDiv = document.getElementById('status');
                const tableBody = document.getElementById('data-table').querySelector('tbody');

                statusDiv.textContent = '';
                tableBody.innerHTML = '';

                try {
                    const response = await fetch('/fetch_data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            pages,
                            limit,
                            category,
                            brand,
                            product_name
                        })
                    });

                    const data = await response.json();
                    if (data.status === 'success') {
                        productData = data.data;

                        productData.forEach(product => {
                            const row = document.createElement('tr');
                            Object.values(product).forEach(value => {
                                const cell = document.createElement('td');
                                cell.textContent = value;
                                row.appendChild(cell);
                            });
                            tableBody.appendChild(row);
                        });
                    } else {
                        statusDiv.textContent = data.message;
                    }
                } catch (error) {
                    statusDiv.textContent = 'Error fetching data.';
                    console.error('Error:', error);
                }
            }

            // Function to calculate nutrition
            function calculateNutrition() {
                const products = document.getElementById('products').value.split(',');
                const quantities = document.getElementById('quantities').value.split(',');

                const resultsDiv = document.getElementById('calculated-nutrition');
                const resultsTable = document.getElementById('calculated-nutrition-table');
                const resultsTableBody = resultsTable.querySelector('tbody');
                resultsDiv.style.display = 'none';
                resultsTableBody.innerHTML = '';  // Clear previous results

                if (products.length !== quantities.length) {
                    resultsDiv.textContent = 'The number of products must match the number of quantities.';
                    resultsDiv.style.display = 'block';
                    return;
                }

                let totalNutrients = {};

                products.forEach((product, index) => {
                    const productInfo = productData.find(p => p.product_name.toLowerCase().includes(product.trim().toLowerCase()));
                    if (productInfo) {
                        const quantity = parseFloat(quantities[index].trim());  // Assuming quantity is in grams
                        const calculatedData = {};

                        // Calculate the nutritional values based on quantities
                        for (const [key, value] of Object.entries(productInfo)) {
                            if (key.includes('100g')) {
                                const nutritionalValue = value * (quantity / 100);
                                calculatedData[key] = nutritionalValue.toFixed(2);

                                // Sum up the nutritional values
                                if (totalNutrients[key]) {
                                    totalNutrients[key] += nutritionalValue;
                                } else {
                                    totalNutrients[key] = nutritionalValue;
                                }
                            }
                        }

                        // Display calculated data in table row
                        const row = document.createElement('tr');
                        row.innerHTML = `
                            <td>${product.trim()}</td>
                            <td>${quantity}</td>
                            ${Object.entries(calculatedData).map(([key, value]) => `<td>${value}</td>`).join('')}
                        `;
                        resultsTableBody.appendChild(row);
                    } else {
                        const p = document.createElement('p');
                        p.textContent = `No data found for product: ${product.trim()}`;
                        resultsDiv.appendChild(p);
                    }
                });

                // Display total sum of nutrients in table row
                const totalRow = document.createElement('tr');
                totalRow.innerHTML = `
                    <td><strong>Total</strong></td>
                    <td></td>
                    ${Object.entries(totalNutrients).map(([key, value]) => `<td>${value.toFixed(2)}</td>`).join('')}
                `;
                resultsTableBody.appendChild(totalRow);

                // Show results table
                resultsDiv.style.display = 'block';
                resultsTable.style.display = 'table';
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(template)

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    try:
        # Validate inputs
        pages = int(request.json.get('pages', 1))
        limit = int(request.json.get('limit', 100))
        category = request.json.get('category', '')
        brand = request.json.get('brand', '')
        product_name = request.json.get('product_name', '')

        if pages < 1 or limit < 1:
            return jsonify({'status': 'error', 'message': 'Pages and limit must be positive integers.'}), 400

        # Fetch data from the OpenFoodFacts API
        products_data = fetch_all_food_data(pages=pages, limit_per_page=limit)

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