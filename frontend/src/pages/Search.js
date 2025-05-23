import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import './Search.css';

const Search = () => {
  // const navigate = useNavigate();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [cart, setCart] = useState(JSON.parse(localStorage.getItem('cart') || '[]'));

  const handleSearch = useCallback(async (e) => {
    e.preventDefault();
    if (searchTerm.trim() === '') return;

    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/api/products`);
      if (!response.ok) throw new Error('Failed to fetch products');
      const products = await response.json();
      
      // Filter products based on search term
      const filteredProducts = products.filter(product =>
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
      
      setResults(filteredProducts);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    // Get search query from URL params
    const params = new URLSearchParams(location.search);
    const query = params.get('q');
    if (query) {
      setSearchTerm(query);
      handleSearch();
    }

    // Update cart state from localStorage
    const currentCart = JSON.parse(localStorage.getItem('cart') || '[]');
    setCart(currentCart);
  }, [handleSearch, location.search, setCart]);

  const addToCart = useCallback((product) => {
    // Update cart state
    setCart(prev => {
      const existingItem = prev.find(item => item.id === product.id);
      if (existingItem) {
        return prev.map(item => 
          item.id === product.id 
            ? { ...item, quantity: (item.quantity || 1) + 1 }
            : item
        );
      }
      return [...prev, {
        ...product,
        quantity: 1
      }];
    });

    // Update localStorage
    const currentCart = JSON.parse(localStorage.getItem('cart') || '[]');
    const existingItem = currentCart.find(item => item.id === product.id);
    if (existingItem) {
      const updatedCart = currentCart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: (item.quantity || 1) + 1 }
          : item
      );
      localStorage.setItem('cart', JSON.stringify(updatedCart));
    } else {
      const newCart = [...currentCart, {
        ...product,
        quantity: 1
      }];
      localStorage.setItem('cart', JSON.stringify(newCart));
    }

    // Update results to show updated quantities
    setResults(prev => prev.map(item => 
      item.id === product.id 
        ? { ...item, quantity: (item.quantity || 1) + 1 }
        : item
    ));
  }, [setCart]);

  return (
    <div className="search-container">
      <h1>Search Results</h1>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search for products..."
          className="search-input"
        />
        <button type="submit" className="search-button">
          Search
        </button>
      </form>

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Searching for products...</p>
        </div>
      )}

      {results.length === 0 && !loading && (
        <div className="no-results">
          <p>No products found matching "{searchTerm}"</p>
          <p>Try searching with different keywords or check our categories page.</p>
        </div>
      )}

      <div className="products-grid">
        {results.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={addToCart}
          />
        ))}
      </div>
    </div>
  );
};

export default Search;
