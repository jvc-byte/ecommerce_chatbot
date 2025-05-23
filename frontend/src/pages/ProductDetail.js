import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './ProductDetail.css';

const ProductDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await fetch(`/api/products/${id}`);
        const data = await response.json();
        setProduct(data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching product:', error);
        setLoading(false);
      }
    };

    // Load cart from localStorage
    const savedCart = JSON.parse(localStorage.getItem('cart') || '[]');
    setCart(savedCart);

    fetchProduct();
  }, [id]);

  const addToCart = (product) => {
    const updatedCart = [...cart, product];
    setCart(updatedCart);
    localStorage.setItem('cart', JSON.stringify(updatedCart));
    navigate('/cart');
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!product) {
    return <div className="not-found">Product not found</div>;
  }

  return (
    <div className="product-detail">
      <div className="product-images">
        <img src={product.image} alt={product.name} className="main-image" />
        <div className="thumbnail-images">
          {product.images.map((img, index) => (
            <img key={index} src={img} alt={`${product.name} thumbnail`} />
          ))}
        </div>
      </div>
      <div className="product-info">
        <h1>{product.name}</h1>
        <p className="price">${product.price}</p>
        <p className="description">{product.description}</p>
        <div className="specs">
          <h3>Specifications:</h3>
          {Object.entries(product.specs).map(([key, value]) => (
            <div key={key} className="spec-item">
              <span className="spec-key">{key}:</span>
              <span className="spec-value">{value}</span>
            </div>
          ))}
        </div>
        <button
          onClick={() => addToCart(product)}
          className="add-to-cart"
          disabled={product.stock === 0}
        >
          {product.stock === 0 ? 'Out of Stock' : 'Add to Cart'}
        </button>
      </div>
      <div className="related-products">
        <h2>Related Products</h2>
        <div className="product-grid">
          {/* Add related products here */}
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
