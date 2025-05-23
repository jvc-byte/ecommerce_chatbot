import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './ShoppingCart.css';

const fetchProductDetails = async (productId) => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/products');
    if (!response.ok) throw new Error('Failed to fetch products');
    const products = await response.json();
    return products.find(product => product.id === productId) || null;
  } catch (error) {
    console.error('Error fetching product:', error);
    return null;
  }
};

const ShoppingCart = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [cartItems, setCartItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    console.log('Raw cart from localStorage:', cart); // Debug log
    const fetchCartDetails = async () => {
      setLoading(true);
      setError('');
      try {
        // Fetch details for each product in cart
        const updatedCart = await Promise.all(
          cart.map(async (item) => {
            console.log('Processing cart item:', item); // Debug log
            const product = await fetchProductDetails(item.id);
            if (product) {
              return {
                ...product,
                quantity: item.quantity || 1
              };
            }
            return item;
          })
        );
        console.log('Updated cart:', updatedCart); // Debug log
        setCartItems(updatedCart);
        calculateTotal(updatedCart);
      } catch (err) {
        setError('Failed to fetch cart items');
        console.error('Error:', err); // Debug log
      } finally {
        setLoading(false);
      }
    };
    fetchCartDetails();
  }, []);

  const calculateTotal = (items) => {
    const total = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    setTotal(total);
  };

  const removeFromCart = (productId) => {
    const updatedCart = cartItems.filter(item => item.id !== productId);
    setCartItems(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
    calculateTotal(updatedCart);
  };

  const updateQuantity = (productId, newQuantity) => {
    const updatedCart = cartItems.map(item =>
      item.id === productId ? { ...item, quantity: newQuantity } : item
    );
    setCartItems(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
    calculateTotal(updatedCart);
  };

  const checkout = () => {
    navigate('/checkout', { state: location });
  };

  return (
    <div className="cart-container">
      <h1>Shopping Cart</h1>
      {loading ? (
        <div className="loading-cart">
          <div className="loading-spinner"></div>
          <p>Loading cart items...</p>
        </div>
      ) : error ? (
        <div className="error-cart">
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Try again</button>
        </div>
      ) : cartItems.length === 0 ? (
        <div className="empty-cart">
          <p>Your cart is empty</p>
          <button onClick={() => navigate('/', { state: location })}>Continue Shopping</button>
        </div>
      ) : (
        <div className="cart-content">
          <div className="cart-items">
            {cartItems.map((item) => (
              <div key={item.id} className="cart-item">
                <img src={item.image} alt={item.name} className="cart-item-image" />
                <div className="cart-item-details">
                  <h3>{item.name}</h3>
                  <p>Price: ${item.price.toFixed(2)}</p>
                  <div className="quantity-controls">
                    <button 
                      onClick={() => updateQuantity(item.id, Math.max(1, item.quantity - 1))}
                      disabled={item.quantity <= 1}
                    >-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
                  </div>
                  <p>Subtotal: ${((item.price * item.quantity).toFixed(2))}</p>
                  <button 
                    className="remove-item"
                    onClick={() => removeFromCart(item.id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <h2>Order Summary</h2>
            <div className="summary-item">
              <span>Subtotal:</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <div className="summary-item">
              <span>Shipping:</span>
              <span>Free</span>
            </div>
            <div className="summary-item total">
              <span>Total:</span>
              <span>${total.toFixed(2)}</span>
            </div>
            <button className="checkout-button" onClick={checkout}>
              Proceed to Checkout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShoppingCart;
