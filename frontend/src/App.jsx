import React from 'react';
import './App.css';
import RecommendedProductsList from './components/RecommendedProducts';

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Customer Product Recommendation App</h1>
      </header>
      <main>
        <RecommendedProductsList />
      </main>
    </div>
  );
};

export default App;
