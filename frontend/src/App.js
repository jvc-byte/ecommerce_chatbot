import React, { useState, useEffect } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import Breadcrumb from './components/Breadcrumb';
import ProductCard from './components/ProductCard';
import Chatbot from './components/Chatbot';
import ProductDetail from './pages/ProductDetail';
import ShoppingCart from './pages/ShoppingCart';
import Checkout from './pages/Checkout';
import Categories from './pages/Categories';
import Search from './pages/Search';
import './App.css';

function App() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cart, setCart] = useState(JSON.parse(localStorage.getItem('cart')) || []);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/api/products');
        if (!response.ok) {
          throw new Error('Failed to fetch products');
        }
        const data = await response.json();
        setProducts(data);
      } catch (err) {
        console.error('Error fetching products:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  const updateCart = (newCart) => {
    setCart(newCart);
    localStorage.setItem('cart', JSON.stringify(newCart));
  };

  const addToCart = (product) => {
    console.log('Adding to cart:', product); // Debug log
    // Check if product is already in cart
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      // If product exists, update its quantity
      setCart(prev => {
        const updatedCart = prev.map(item => 
          item.id === product.id 
            ? { ...item, quantity: (item.quantity || 1) + 1 }
            : item
        );
        localStorage.setItem('cart', JSON.stringify(updatedCart));
        return updatedCart;
      });
    } else {
      // If product doesn't exist, add it with quantity 1
      setCart(prev => {
        const newCart = [...prev, {
          ...product,
          quantity: 1,
          image: product.image || 'default-image.jpg',
          description: product.description || 'No description available'
        }];
        localStorage.setItem('cart', JSON.stringify(newCart));
        return newCart;
      });
    }
  };

  return (
    <div className="app-container">
      <nav className="main-nav">
        <Link to="/" className="logo">TechStore</Link>
        <div className="nav-links">
          <Link to="/" className="nav-link">Home</Link>
          <Link to="/categories" className="nav-link">Categories</Link>
          <Link to="/search" className="nav-link">Search</Link>
          <Link to="/cart" className="cart-link">
            <span className="cart-icon">🛒</span>
            <span className="cart-count">{cart.reduce((total, item) => total + (item.quantity || 1), 0)}</span>
          </Link>
        </div>
      </nav>
      <div className="content">
        <Breadcrumb />
        <Routes>
          <Route path="/" element={
            <div className="home-page">
              <section className="hero">
                <h1>Welcome to TechStore</h1>
                <p>Your one-stop shop for all your tech needs</p>
                <div className="featured-products">
                  {/* Add featured products here */}
                </div>
              </section>
              {loading ? (
                <div className="loading-container">
                  <div className="loading-spinner"></div>
                  <p>Loading products...</p>
                </div>
              ) : error ? (
                <div className="error-container">
                  <p>Error loading products: {error}</p>
                  <button onClick={() => window.location.reload()}>Try again</button>
                </div>
              ) : (
                <main className="products-grid">
                  {products.map(product => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onAddToCart={addToCart}
                    />
                  ))}
                </main>
              )}
            </div>
          } />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<ShoppingCart updateCart={updateCart} />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/categories" element={<Categories />} />
          <Route path="/search" element={<Search />} />
          <Route path="*" element={
            <div className="error-page">
              <h1>404 - Page Not Found</h1>
              <p>Sorry, the page you're looking for doesn't exist.</p>
              <Link to="/" className="nav-link">Go back home</Link>
            </div>
          } />
        </Routes>
      </div>
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Customer Service</h3>
            <ul className="footer-links">
              <li><Link to="/contact" className="footer-link">Contact Us</Link></li>
              <li><Link to="/returns" className="footer-link">Returns</Link></li>
              <li><Link to="/shipping" className="footer-link">Shipping Info</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h3>Quick Links</h3>
            <ul className="footer-links">
              <li><Link to="/about" className="footer-link">About Us</Link></li>
              <li><Link to="/faq" className="footer-link">FAQ</Link></li>
              <li><Link to="/privacy" className="footer-link">Privacy Policy</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h3>Connect With Us</h3>
            <div className="social-links">
              <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" className="social-link">Facebook</a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="social-link">Twitter</a>
              <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="social-link">Instagram</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p className="copyright">&copy; {new Date().getFullYear()} TechStore. All rights reserved.</p>
          </div>
        </div>
      </footer>
      <Chatbot />
    </div>
  );
}

export default App;
