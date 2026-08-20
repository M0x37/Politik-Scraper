import React from 'react';
import { createRoot } from 'react-dom/client';
import HandwritingConverter from './HandwritingConverter';
import './HandwritingConverter.css';

const App = () => {
  return (
    <div className="App">
      <HandwritingConverter />
    </div>
  );
};

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
