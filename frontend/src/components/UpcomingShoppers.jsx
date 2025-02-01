import React, { useEffect, useState } from 'react';
import api from '../api';

const UpcomingShoppersList = () => {

    const [shoppers, setShoppers] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchShoppers = async () => {
        try {
            setLoading(true);  // Start loading before API call
            const response = await api.get('/upcoming-shoppers');
            setShoppers(response.data.shoppers);
        } catch (error) {
          console.error("Error Recommending Products", error);
        } finally {
          setLoading(false); // Stop loading after API call completes
        }
    };

    useEffect(() => {
      fetchShoppers();
    }, []); // Empty dependency array ensures it runs on mount

    return (
        <div>
        <h2>Upcoming Shoppers</h2>

        {loading ? ( // Show loading state while fetching
        <p>Loading...</p>
        ) : shoppers.length === 0 ? ( // Show message only after search
        <p>No Upcoming Shoppers were predicted.</p>
        ) : (
        <ul>
          {shoppers.map((shopper, index) => (
            <li key={index}>{shopper.shopper_id} | {shopper.name} | {shopper.email}</li>
          ))}
        </ul>
        )}
        </div>
      );

};

export default UpcomingShoppersList;