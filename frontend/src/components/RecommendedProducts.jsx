import React, { useEffect, useState} from 'react';
import FindRecommendedProducts from './FindRecommendedProducts';
import api from '../api';

const RecommendedProductsList = () => {

    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [hasFetched, setHasFetched] = useState(false);

    const fetchProducts = async (cust_id) => {
      if (!cust_id) return;
        try {
            setLoading(true);  // Start loading before API call
            setHasFetched(true)
            const response = await api.get('/recommend-products', {params: {customer_id: cust_id}});
            setProducts(response.data.products);
        } catch (error) {
            console.error("Error Recommending Products", error);
        } finally {
          setLoading(false); // Stop loading after API call completes
        }
    };

    return (
        <div>
        <h2>Recommended Products</h2>

        {loading ? ( // Show loading state while fetching
        <p>Loading...</p>
        ) : hasFetched && products.length === 0 ? ( // Show message only after search
        <p>Customer has made no orders.</p>
        ) : (
        <ul>
          {products.map((product, index) => (
            <li key={index}>{product.name}</li>
          ))}
        </ul>
        )}
        
          <FindRecommendedProducts fetchProducts={fetchProducts} />
        </div>
      );

};

export default RecommendedProductsList;

