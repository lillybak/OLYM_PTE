// Import the main React library
import React from 'react';
// Import the new ReactDOM client API for React 18+
import ReactDOM from 'react-dom/client';
// Import your main App component
import App from './App';

// Find the root element in your HTML where the app will be mounted
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement // Type assertion for TypeScript
);

// Render the App component inside <React.StrictMode> for highlighting potential problems
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);