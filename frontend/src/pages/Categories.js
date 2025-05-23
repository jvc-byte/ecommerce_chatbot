import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Categories.css';

const Categories = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const categories = [
    { id: 1, name: "Laptops", image: "https://i.dell.com/is/image/DellContent//content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-7590/general/111-xps-product-imagery-notebook-xps-15-7590-campaign.jpg?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=855&qlt=100,1&resMode=sharp2&size=855,402&chrss=full" },
    { id: 2, name: "Smartphones", image: "https://adminapi.applegadgetsbd.com/storage/media/large/Galaxy-S23-Ultra-Cream-1280.jpg" },
    { id: 3, name: "Tablets", image: "https://i5.walmartimages.com/seo/Android-13-Tablet-Android-Tablet-SIM-Card-Slot-Unlocked-4G-LTE-GSM-Cellular-Phone-Tablet-Octa-Core-6GB-RAM-128GB-ROM-GPS-WiFi-Case-Dual-Camera-Speake_a8a87ed9-b103-448e-97f9-a8fd89deb3ae.16db33842207ed61ae5e795b22258c38.jpeg?odnHeight=640&odnWidth=640&odnBg=FFFFFF" },
    { id: 4, name: "Accessories", image: "https://as1.ftcdn.net/jpg/11/49/43/28/1000_F_1149432899_JRRMlHXEiBveNtGQceDgiXKZEdEJDh6g.webp" },
    { id: 5, name: "Gaming", image: "https://media.istockphoto.com/id/1334436084/photo/top-down-view-of-colorful-illuminated-gaming-accessories-laying-on-table.jpg?s=612x612&w=0&k=20&c=E9xnbAZoBS5LlUX0q-zxT_3m6gEZpyB2k51_U4LLMNs=" },
    { id: 6, name: "Audio", image: "https://image.ceneostatic.pl/data/products/131921458/4ca84c6a-70d4-4dba-8dc8-41d18bfc6d6e_i-sony-wh-1000xm5-czarny.jpg" },
  ];

  const handleCategoryClick = (category) => {
    navigate(`/category/${category.id}`, { state: location });
  };

  return (
    <div className="categories-container">
      <h1>Shop by Category</h1>
      <div className="category-grid">
        {categories.map(category => (
          <div 
            key={category.id} 
            className="category-card"
            onClick={() => handleCategoryClick(category)}
          >
            <img src={category.image} alt={category.name} className="category-image" />
            <h3>{category.name}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Categories;
