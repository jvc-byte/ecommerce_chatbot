import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import './Breadcrumb.css';

const Breadcrumb = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(x => x);

  return (
    <nav className="breadcrumb">
      <div className="breadcrumb-container">
        <Link to="/" className="breadcrumb-link">
          <span className="breadcrumb-icon">🏠</span>
          Home /
        </Link>
        {pathnames.map((name, index) => {
          const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
          // const isLast = index === pathnames.length - 1;
          return (
            <div key={index} className="breadcrumb-item">
              {/* <span className="breadcrumb-arrow">/</span> */}
              <Link to={routeTo} className="breadcrumb-link">
                {name} /
              </Link>
            </div>
          );
        })}
      </div>
    </nav>
  );
};

export default Breadcrumb;
