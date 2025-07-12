import React from 'react';
import ReactDOM from 'react-dom/client';
import App from '@/App.jsx';
import '@/index.css';

import { initPerformanceMonitoring } from '@/utils/performance';
import { optimizeFonts, FontDisplay } from '@/utils/font-optimization';

// Initialize performance monitoring
initPerformanceMonitoring({
  logLevel: process.env.NODE_ENV === 'development' ? 'info' : 'warn',
  samplingRate: process.env.NODE_ENV === 'development' ? 1.0 : 0.1,
  logThreshold: 100
});

// Optimize fonts
optimizeFonts([
  {
    family: 'Inter',
    weights: ['400', '500', '600', '700'],
    display: FontDisplay.SWAP,
    preload: true
  }
]);

// Create root and render app
const root = ReactDOM.createRoot(document.getElementById('root'));

// Measure initial render time
performance.mark('initial_render_start');

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Measure render completion and register Service Worker
window.addEventListener('load', () => {
  performance.mark('initial_render_end');
  performance.measure('initial_render', 'initial_render_start', 'initial_render_end');
  
  const entries = performance.getEntriesByName('initial_render');
  if (entries.length > 0) {
    console.log(`Initial render took ${entries[0].duration.toFixed(2)}ms`);
  }
  
  // Report to analytics in production
  if (process.env.NODE_ENV === 'production') {
    // reportPerformanceMetric('initial_render', entries[0].duration);
  }

  // Register Service Worker
  if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      })
      .catch(error => {
        console.error('Service Worker registration failed:', error);
      });
  }
});