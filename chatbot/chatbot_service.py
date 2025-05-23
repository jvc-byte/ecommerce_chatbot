import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
from typing import List, Dict, Any
import requests
import google.generativeai as genai

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# LLM Configuration - Multiple options available
LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # Options: 'openai', 'huggingface', 'local', 'simple', 'gemini'
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyCiLA3Xs7CDP0cElyRmBk8RE6OiENAawes')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')  # Optional, for higher rate limits
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configure Google Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini_model = genai.GenerativeModel(model_name='models/gemma-3-4b-it')

# Load products data
PRODUCTS = []
try:
    with open('../database/products.json', 'r') as f:
        PRODUCTS = json.load(f)
except FileNotFoundError:
    print("Warning: products.json not found. Using empty product list.")
    PRODUCTS = []

# Conversation memory (in production, use a proper database)
conversation_history = {}

def is_product_search_intent(message: str) -> bool:
    """Determine if the message is actually asking about products"""
    message_lower = message.lower().strip()
    
    # Pure greetings - not product searches
    pure_greetings = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
        'how are you', 'how\'s it going', 'what\'s up', 'greetings', 'howdy'
    ]
    
    # If it's just a greeting, return False
    if any(message_lower == greeting or message_lower.startswith(greeting + ' ') for greeting in pure_greetings):
        return False
    
    # Conversational phrases that aren't product searches
    conversational_phrases = [
        'thank you', 'thanks', 'goodbye', 'bye', 'see you later',
        'okay', 'ok', 'alright', 'sounds good', 'perfect', 'great',
        'yes', 'no', 'maybe', 'sure', 'definitely', 'absolutely',
        'tell me about yourself', 'who are you', 'what can you do',
        'help me', 'i need help', 'can you help'
    ]
    
    if any(phrase in message_lower for phrase in conversational_phrases):
        return False
    
    # Clear product search indicators
    product_search_indicators = [
        'search', 'find', 'look for', 'looking for', 'do you have', 'have you got',
        'show me', 'i want', 'i need', 'buy', 'purchase', 'price', 'cost',
        'available', 'in stock', 'sell', 'carry', 'offer',
        'recommend', 'suggest', 'best', 'good', 'popular'
    ]
    
    # Only return True if there are clear product search indicators
    return any(indicator in message_lower for indicator in product_search_indicators)

class ProductSearchEngine:
    def __init__(self, products: List[Dict]):
        self.products = products
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict]:
        """Enhanced product search with scoring"""
        query = query.lower().strip()
        results = []
        
        for product in self.products:
            score = 0
            name_lower = product['name'].lower()
            desc_lower = product.get('description', '').lower()
            category_lower = product.get('category', '').lower()
            
            # Exact name match (highest score)
            if query in name_lower:
                score += 10
            
            # Word matches in name
            query_words = query.split()
            for word in query_words:
                if word in name_lower:
                    score += 5
                if word in desc_lower:
                    score += 2
                if word in category_lower:
                    score += 3
            
            # Model number matches
            if re.findall(r'\d+', query):
                numbers_in_query = re.findall(r'\d+', query)
                numbers_in_name = re.findall(r'\d+', name_lower)
                if any(num in numbers_in_name for num in numbers_in_query):
                    score += 7
            
            if score > 0:
                product_copy = product.copy()
                product_copy['relevance_score'] = score
                results.append(product_copy)
        
        # Sort by relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_product_by_name(self, name: str) -> Dict:
        """Get exact product match"""
        name_lower = name.lower()
        for product in self.products:
            if name_lower == product['name'].lower():
                return product
        return None
    
    def get_products_by_category(self, category: str, limit: int = 5) -> List[Dict]:
        """Get products by category"""
        category_lower = category.lower()
        results = []
        for product in self.products:
            if category_lower in product.get('category', '').lower():
                results.append(product)
        return results[:limit]
    
    def get_products_in_stock(self, limit: int = 5) -> List[Dict]:
        """Get products that are in stock"""
        return [p for p in self.products if p.get('stock', 0) > 0][:limit]
    
    def get_products_by_price_range(self, min_price: float = None, max_price: float = None, limit: int = 5) -> List[Dict]:
        """Get products within price range"""
        results = []
        for product in self.products:
            price = product.get('price', 0)
            if min_price is not None and price < min_price:
                continue
            if max_price is not None and price > max_price:
                continue
            results.append(product)
        return results[:limit]

# Initialize search engine
search_engine = ProductSearchEngine(PRODUCTS)

def extract_product_keywords(message: str) -> List[str]:
    """Extract potential product names/keywords from user message"""
    message_lower = message.lower()
    
    # Common product categories and brands
    product_keywords = [
        # Electronics
        'iphone', 'samsung', 'phone', 'smartphone', 'mobile',
        'laptop', 'computer', 'macbook', 'dell', 'hp', 'lenovo',
        'headphones', 'earbuds', 'airpods', 'beats', 'sony',
        'tablet', 'ipad', 'android',
        'camera', 'canon', 'nikon', 'gopro',
        'tv', 'television', 'monitor', 'display',
        'keyboard', 'mouse', 'razer', 'logitech',
        'charger', 'cable', 'adapter',
        'speaker', 'bluetooth', 'wireless',
        
        # Fashion
        'shirt', 'pants', 'dress', 'shoes', 'sneakers',
        'jacket', 'coat', 'jeans', 'hoodie',
        'nike', 'adidas', 'puma',
        
        # Home
        'chair', 'table', 'desk', 'bed', 'sofa',
        'lamp', 'light', 'furniture',
        
        # General terms
        'watch', 'bag', 'backpack', 'case', 'cover',
        'gaming', 'console', 'xbox', 'playstation', 'nintendo'
    ]
    
    found_keywords = []
    for keyword in product_keywords:
        if keyword in message_lower:
            found_keywords.append(keyword)
    
    # Also extract quoted terms or specific product mentions
    words = message_lower.split()
    for word in words:
        if len(word) > 3 and word not in ['have', 'does', 'what', 'where', 'when', 'how', 'can', 'will', 'would', 'could', 'should']:
            found_keywords.append(word)
    
    return list(set(found_keywords))  # Remove duplicates

def get_enhanced_product_context(products: List[Dict], searched_terms: List[str], original_message: str) -> str:
    """Enhanced product context that includes search information"""
    context = ""
    
    if products:
        context += f"FOUND PRODUCTS ({len(products)} results):\n"
        for i, product in enumerate(products[:5], 1):
            stock_status = "✅ In stock" if product.get('stock', 0) > 0 else "❌ Out of stock"
            context += f"{i}. {product['name']} - ${product.get('price', 'N/A')} ({stock_status})\n"
            context += f"   Description: {product.get('description', 'No description')}\n\n"
    else:
        # Be specific about what wasn't found
        if searched_terms:
            searched_items = ', '.join(searched_terms[:3])  # Show first 3 terms
            context += f"NO PRODUCTS FOUND for: {searched_items}\n"
            context += f"Search terms tried: {searched_terms}\n"
        else:
            context += "NO PRODUCTS FOUND - No specific product terms detected\n"
        
        context += f"Original user query: '{original_message}'\n"
        context += "Available product categories: Check the complete product database to suggest alternatives\n"
    
    return context

def extract_search_intent(message: str) -> Dict[str, Any]:
    """Extract search parameters from user message"""
    message_lower = message.lower()
    intent = {
        'search_query': None,
        'category': None,
        'price_min': None,
        'price_max': None,
        'stock_only': False
    }
    
    # Extract price range
    price_matches = re.findall(r'\$?(\d+(?:\.\d{2})?)', message)
    if len(price_matches) >= 2:
        prices = [float(p) for p in price_matches]
        intent['price_min'] = min(prices)
        intent['price_max'] = max(prices)
    elif len(price_matches) == 1:
        if 'under' in message_lower or 'below' in message_lower or 'less than' in message_lower:
            intent['price_max'] = float(price_matches[0])
        elif 'over' in message_lower or 'above' in message_lower or 'more than' in message_lower:
            intent['price_min'] = float(price_matches[0])
    
    # Check for stock requirement
    if any(phrase in message_lower for phrase in ['in stock', 'available', 'stock']):
        intent['stock_only'] = True
    
    # Extract general search query (remove price and stock related words)
    search_terms = re.sub(r'\$?\d+(?:\.\d{2})?', '', message)
    search_terms = re.sub(r'\b(in stock|available|stock|under|over|above|below|less than|more than|price|cost)\b', '', search_terms, flags=re.IGNORECASE)
    intent['search_query'] = search_terms.strip()
    
    return intent

def generate_llm_response(user_message: str, session_id: str, product_context: str = "", is_product_search: bool = False) -> str:
    """Generate response using different LLM providers"""
    
    # Get conversation history
    history = conversation_history.get(session_id, [])
    
    # System prompt - adjusted based on whether this is a product search
    if is_product_search and product_context:
        system_prompt = f"""You are a helpful and friendly customer service chatbot for an e-commerce store.

CRITICAL INSTRUCTIONS:
1. ALWAYS base your product responses on the ACTUAL search results provided
2. If NO PRODUCTS are found, clearly state that you don't have those items
3. Only mention products that actually exist in the search results
4. Be specific about what was searched for and what was/wasn't found
5. Don't make up or assume products exist

Store Policies:
- Free shipping on orders over $50
- Standard shipping takes 3-5 business days  
- 30-day return policy for full refund
- Accept major credit cards, PayPal, and Apple Pay

PRODUCT SEARCH RESULTS:
{product_context}

Be conversational, helpful, and HONEST about product availability."""
    else:
        system_prompt = """You are a helpful and friendly customer service chatbot for an e-commerce store.

You can help customers with:
1. General conversation and greetings
2. Product searches and recommendations  
3. Information about shipping, returns, and policies
4. Answering questions about our store

Store Policies:
- Free shipping on orders over $50
- Standard shipping takes 3-5 business days
- 30-day return policy for full refund
- Accept major credit cards, PayPal, and Apple Pay

Be conversational, friendly, and helpful. For greetings and general conversation, respond naturally without forcing product information."""

    try:
        if LLM_PROVIDER == 'openai':
            return generate_openai_response(user_message, history, system_prompt)
        elif LLM_PROVIDER == 'huggingface':
            return generate_huggingface_response(user_message, history, system_prompt, product_context)
        elif LLM_PROVIDER == 'local':
            return generate_local_response(user_message, history, system_prompt)
        elif LLM_PROVIDER == 'gemini':
            return generate_gemini_response(user_message, history, system_prompt, session_id)
        else:  # simple fallback
            return generate_simple_response(user_message, product_context, is_product_search)
            
    except Exception as e:
        print(f"LLM Error: {str(e)}")
        return generate_simple_response(user_message, product_context, is_product_search)

def generate_gemini_response(user_message: str, history: List, system_prompt: str, session_id: str) -> str:
    """Generate response using Google Gemini (Gemma-3-4b-it)"""
    try:
        # Prepare the conversation context
        conversation_text = f"{system_prompt}\n\nConversation:\n"
        
        # Add conversation history
        for msg in history[-8:]:  # Keep recent context
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_text += f"{role}: {msg['content']}\n"
        
        # Add current message
        conversation_text += f"User: {user_message}\nAssistant:"
        
        # Generate response using Gemini
        response = gemini_model.generate_content(
            conversation_text,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
                top_p=0.9,
                top_k=40
            )
        )
        
        ai_response = response.text.strip()
        
        # Update conversation history
        if session_id not in conversation_history:
            conversation_history[session_id] = []
        
        conversation_history[session_id].append({"role": "user", "content": user_message})
        conversation_history[session_id].append({"role": "assistant", "content": ai_response})
        
        # Keep only last 20 messages per session
        if len(conversation_history[session_id]) > 20:
            conversation_history[session_id] = conversation_history[session_id][-20:]
        
        return ai_response
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return generate_simple_response(user_message, "", False)

def generate_openai_response(user_message: str, history: List, system_prompt: str) -> str:
    """Generate response using OpenAI"""
    import openai
    openai.api_key = OPENAI_API_KEY
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history[-10:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    
    return response.choices[0].message.content.strip()

def generate_huggingface_response(user_message: str, history: List, system_prompt: str, product_context: str) -> str:
    """Generate response using Hugging Face API (Free!)"""
    
    # Prepare conversation context
    conversation_text = f"{system_prompt}\n\n"
    
    # Add recent history
    for msg in history[-6:]:  # Keep it shorter for free API
        role = "Human" if msg["role"] == "user" else "Assistant"
        conversation_text += f"{role}: {msg['content']}\n"
    
    conversation_text += f"Human: {user_message}\nAssistant:"
    
    # Hugging Face Inference API (Free tier available)
    api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    headers = {}
    if HUGGINGFACE_API_KEY:
        headers["Authorization"] = f"Bearer {HUGGINGFACE_API_KEY}"
    
    # For DialoGPT, we use a simpler format
    payload = {
        "inputs": user_message,
        "parameters": {
            "max_length": 200,
            "temperature": 0.7,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                # Clean up the response
                if user_message in generated_text:
                    response_text = generated_text.replace(user_message, '').strip()
                else:
                    response_text = generated_text.strip()
                
                return response_text if response_text else generate_simple_response(user_message, product_context, False)
        
        # Fallback if API fails
        return generate_simple_response(user_message, product_context, False)
        
    except Exception as e:
        print(f"Hugging Face API error: {e}")
        return generate_simple_response(user_message, product_context, False)

def generate_local_response(user_message: str, history: List, system_prompt: str) -> str:
    """Generate response using local LLM (like Ollama)"""
    try:
        # Example for Ollama (install ollama and run: ollama run llama2)
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',
                'prompt': f"{system_prompt}\n\nUser: {user_message}\nAssistant:",
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            raise Exception("Local LLM not available")
            
    except Exception as e:
        print(f"Local LLM error: {e}")
        return generate_simple_response(user_message, "", False)

def generate_simple_response(user_message: str, product_context: str, is_product_search: bool) -> str:
    """Simple rule-based responses as fallback - now context-aware"""
    message_lower = user_message.lower()
    
    # Handle greetings first - don't mention products unless it's actually a product search
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']) and not is_product_search:
        return "Hi there, welcome to TechStore!. I'm here to help you find products and answer your questions. What can I help you with today?"
    
    # Check if we found products in the search
    has_products = "FOUND PRODUCTS" in product_context
    no_products_found = "NO PRODUCTS FOUND" in product_context
    
    # Product search responses - only if this is actually a product search
    if is_product_search:
        if any(word in message_lower for word in ['search', 'find', 'look for', 'looking for', 'do you have', 'have you got']):
            if has_products:
                return f"Great! I found some products for you:\n\n{product_context.replace('FOUND PRODUCTS', 'Here are the products I found').replace('✅', '✅').replace('❌', '❌')}\n\nWould you like more details about any of these?"
            elif no_products_found:
                searched_item = extract_searched_item_from_context(product_context)
                return f"I'm sorry, but I don't currently have {searched_item} in our inventory. Let me check what similar items we do have available - would you like me to show you our current product selection?"
            else:
                return "I'd be happy to help you find products! Could you tell me more specifically what you're looking for?"
        
        # Direct questions about specific products
        elif any(word in message_lower for word in ['do you have', 'have you got', 'sell', 'carry']):
            if has_products:
                return f"Yes! Here's what I found:\n\n{product_context.replace('FOUND PRODUCTS', '').strip()}"
            elif no_products_found:
                searched_item = extract_searched_item_from_context(product_context)
                return f"No, I'm sorry - we don't currently carry {searched_item}. However, I'd be happy to show you what we do have available. What type of products are you interested in?"
            else:
                return "I can check our inventory for you! What specific product are you looking for?"
        
        # Pricing questions
        elif any(word in message_lower for word in ['price', 'cost', 'how much']):
            if has_products:
                return f"Here are the products with their prices:\n\n{product_context.replace('FOUND PRODUCTS', 'Here are the current prices').replace('✅', '✅').replace('❌', '❌')}"
            else:
                return "I can help you with pricing! What product are you interested in?"
        
        # Stock/availability
        elif any(word in message_lower for word in ['stock', 'available', 'in stock']):
            if has_products:
                return f"Here's the current availability:\n\n{product_context.replace('FOUND PRODUCTS', 'Current stock status').replace('✅', '✅').replace('❌', '❌')}"
            elif no_products_found:
                return "I checked our inventory for the items you mentioned, but they're not currently available. Would you like me to show you what we do have in stock?"
            else:
                return "I can check product availability for you. What items are you looking for?"
    
    # Shipping and policies
    if any(word in message_lower for word in ['shipping', 'delivery', 'return', 'refund']):
        return """Here's information about our policies:

🚚 **Shipping:** Free shipping on orders over $50. Standard delivery takes 3-5 business days.

↩️ **Returns:** 30-day return policy for full refund on unused items.

💳 **Payment:** We accept all major credit cards, PayPal, and Apple Pay.

Is there anything specific you'd like to know?"""
    
    # Recommendations - only if this is a product search
    if any(word in message_lower for word in ['recommend', 'suggest', 'best']) and is_product_search:
        if has_products:
            return f"Based on your search, here are some great options:\n\n{product_context.replace('FOUND PRODUCTS', 'I recommend these products').replace('✅', '✅').replace('❌', '❌')}\n\nThese are popular choices among our customers!"
        else:
            return "I'd love to recommend something perfect for you! What type of product are you interested in?"
    
    # Conversational responses
    if any(word in message_lower for word in ['thank you', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    if any(word in message_lower for word in ['goodbye', 'bye', 'see you']):
        return "Goodbye! Thanks for visiting our store. Have a great day!"
    
    if any(word in message_lower for word in ['how are you', 'how\'s it going']):
        return "I'm doing great, thank you for asking! I'm here and ready to help you find what you're looking for. How can I assist you today?"
    
    # Default response based on context
    if is_product_search:
        if has_products:
            return f"I found some relevant products for you:\n\n{product_context.replace('FOUND PRODUCTS', 'Here are some options').replace('✅', '✅').replace('❌', '❌')}\n\nHow can I help you further?"
        elif no_products_found:
            return "I checked our inventory based on your message, but didn't find exact matches. Could you tell me more specifically what you're looking for so I can help you better?"
        else:
            return "I'd be happy to help you find products! What are you looking for today?"
    else:
        return "I'm here to help! You can ask me about:\n• Product searches and availability\n• Pricing information\n• Shipping and return policies\n• Product recommendations\n\nWhat would you like to know?"

def extract_searched_item_from_context(context: str) -> str:
    """Extract what was searched for from the context"""
    if "NO PRODUCTS FOUND for:" in context:
        try:
            line = [line for line in context.split('\n') if 'NO PRODUCTS FOUND for:' in line][0]
            searched_item = line.split('NO PRODUCTS FOUND for:')[1].strip()
            return searched_item if searched_item else "those items"
        except:
            return "those items"
    return "those items"

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')  # Use session ID for conversation tracking
        
        if not message:
            return jsonify({
                'type': 'error',
                'message': "Please provide a message."
            }), 400
        
        # Determine if this is actually a product search
        is_product_search = is_product_search_intent(message)
        
        relevant_products = []
        product_context = ""
        
        # Only search for products if this is actually a product search
        if is_product_search:
            # Extract search intent from message
            intent = extract_search_intent(message)
            
            # Search for products in the message
            search_terms = extract_product_keywords(message)
            for term in search_terms:
                found_products = search_engine.search_products(term)
                relevant_products.extend(found_products)
            
            # Also use the extracted search query
            if intent['search_query']:
                additional_products = search_engine.search_products(intent['search_query'])
                relevant_products.extend(additional_products)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_products = []
            for product in relevant_products:
                if product['name'] not in seen:
                    seen.add(product['name'])
                    unique_products.append(product)
            relevant_products = unique_products
            
            # Filter by price range if specified
            if intent['price_min'] is not None or intent['price_max'] is not None:
                price_filtered = search_engine.get_products_by_price_range(
                    intent['price_min'], intent['price_max']
                )
                if relevant_products:
                    # Intersect with existing results
                    relevant_products = [p for p in relevant_products if p in price_filtered]
                else:
                    relevant_products = price_filtered
            
            # Filter by stock if requested
            if intent['stock_only']:
                relevant_products = [p for p in relevant_products if p.get('stock', 0) > 0]
            
            # If no specific search but asking about stock/availability
            if not relevant_products and any(word in message.lower() for word in ['stock', 'available', 'what do you have']):
                relevant_products = search_engine.get_products_in_stock()
            
            # Prepare product context for LLM - include info about what was searched
            searched_terms = search_terms + ([intent['search_query']] if intent['search_query'] else [])
            product_context = get_enhanced_product_context(relevant_products, searched_terms, message)
        
        # Generate response using LLM
        ai_response = generate_llm_response(message, session_id, product_context, is_product_search)
        
        return jsonify({
            'type': 'chat_response',
            'message': ai_response,
            'products': relevant_products[:3] if relevant_products else [],  # Include top 3 products
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'type': 'error',
            'message': "I apologize, but I'm experiencing technical difficulties. Please try again later."
        }), 500

@app.route('/api/chatbot/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in conversation_history:
            del conversation_history[session_id]
        
        return jsonify({
            'type': 'success',
            'message': "Conversation history cleared."
        })
        
    except Exception as e:
        print(f"Error clearing conversation: {str(e)}")
        return jsonify({
            'type': 'error',
            'message': "Failed to clear conversation history."
        }), 500

@app.route('/api/products', methods=['GET'])
def get_all_products():
    """Get all products (for debugging/admin purposes)"""
    return jsonify({
        'products': PRODUCTS,
        'total': len(PRODUCTS)
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'products_loaded': len(PRODUCTS),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print(f"Loaded {len(PRODUCTS)} products")
    print("Starting LLM-powered chatbot server...")
    app.run(port=5001, debug=True)