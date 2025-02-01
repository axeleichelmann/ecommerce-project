import React from 'react';
import './App.css';
import RecommendedProductsList from './components/RecommendedProducts';
import UpcomingShoppersList from './components/UpcomingShoppers'

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Customer Base Insights App</h1>
      </header>
      <main>
        <RecommendedProductsList />
        <UpcomingShoppersList />
      </main>
    </div>
  );
};

export default App;
