import React, { useState } from 'react';

const FindRecommendedProducts = ({ fetchProducts }) => {
    const [customerID, setCustomerID] = useState('');
    
    const handleSubmit = (event) => {
        event.preventDefault();
        if (customerID) {
            fetchProducts(customerID);
            setCustomerID(customerID);
        }
    };
    

    return (
        <form onSubmit={handleSubmit}>
            <input
            type="text"
            value={customerID}
            onChange={(e)=>setCustomerID(e.target.value)}
            placeholder="Enter Customer ID"
            />
            <button type='submit'>Find Recommended Products</button>
        </form>
    );
};

export default FindRecommendedProducts;