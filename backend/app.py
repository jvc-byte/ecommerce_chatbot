from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Get the absolute path to the products.json file
PRODUCTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../database/products.json')

# Load products from JSON file
def load_products():
    try:
        with open(PRODUCTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save products to JSON file
def save_products(products):
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(products, f, indent=4)

@app.route('/api/products', methods=['GET'])
def get_products():
    products = load_products()
    return jsonify(products)

@app.route('/api/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify(product)
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'Product ID is required'}), 400

    # Load current cart from localStorage
    cart = json.loads(request.headers.get('Cart', '[]'))

    # Check if product is already in cart
    existing_item = next((item for item in cart if item['id'] == product_id), None)
    if existing_item:
        existing_item['quantity'] += quantity
    else:
        # Add new item to cart
        products = load_products()
        product = next((p for p in products if p['id'] == product_id), None)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        cart.append({
            'id': product_id,
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity
        })

    return jsonify(cart)

if __name__ == '__main__':
    app.run(debug=True)
