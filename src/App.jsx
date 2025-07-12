import './App.css';
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import { Toaster } from 'sonner';
import { routes } from './routes';
import { AuthProvider } from './contexts/AuthContext';
import { SubscriptionProvider } from './contexts/SubscriptionContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { ErrorBoundary } from './components/ui/error-boundary';
import ErrorBoundaryComponent from './components/ErrorBoundary';
import AsyncErrorBoundary from './components/AsyncErrorBoundary';
import { initAnalytics } from './utils/analytics';
import { initErrorTracking } from './utils/error-tracking';
import { useEffect } from 'react';

// Create router from routes configuration
const router = createBrowserRouter(routes);

// Initialize analytics and error tracking
initAnalytics();
initErrorTracking({ environment: import.meta.env.MODE });

/**
 * Main App component
 * Provides global contexts and router
 * 
 * @returns {JSX.Element} - Rendered component
 */
function App() {
  // Performance monitoring for initial load
  useEffect(() => {
    // Report performance metrics when the app is fully loaded
    const reportPerformance = () => {
      if (window.performance) {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page load time: ${pageLoadTime}ms`);
      }
    };

    // Wait for the page to be fully loaded
    if (document.readyState === 'complete') {
      reportPerformance();
    } else {
      window.addEventListener('load', reportPerformance);
      return () => window.removeEventListener('load', reportPerformance);
    }
  }, []);

  return (
    <ErrorBoundaryComponent name="App" context={{ component: 'App' }}>
      <ThemeProvider>
        <AuthProvider>
          <SubscriptionProvider>
            <NotificationProvider>
              <AsyncErrorBoundary catchAsync={true}>
                <ErrorBoundary>
                  <RouterProvider router={router} />
                  <Toaster position="top-right" richColors closeButton />
                </ErrorBoundary>
              </AsyncErrorBoundary>
            </NotificationProvider>
          </SubscriptionProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundaryComponent>
  );
}

export default App;
