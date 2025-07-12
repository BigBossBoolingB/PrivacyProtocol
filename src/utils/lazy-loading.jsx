import React, { lazy, Suspense } from 'react';
import { startMeasure, endMeasure } from './performance';

/**
 * Default loading component
 */
const DefaultLoading = () => (
  <div className="flex items-center justify-center p-8">
    <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full" />
  </div>
);

/**
 * Default error component
 */
const DefaultError = ({ error, retry }) => (
  <div className="p-4 border border-red-300 bg-red-50 rounded-md">
    <h3 className="text-lg font-medium text-red-800">Failed to load component</h3>
    <p className="mt-2 text-sm text-red-700">{error.message}</p>
    {retry && (
      <button
        onClick={retry}
        className="mt-3 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-800 rounded-md text-sm"
      >
        Retry
      </button>
    )}
  </div>
);

/**
 * Create a lazy-loaded component with performance tracking
 * 
 * @param {Function} importFn - Dynamic import function
 * @param {Object} options - Options
 * @param {React.Component} [options.Loading] - Loading component
 * @param {React.Component} [options.Error] - Error component
 * @param {string} [options.name] - Component name for tracking
 * @param {boolean} [options.trackPerformance=true] - Whether to track performance
 * @returns {React.Component} - Lazy-loaded component
 */
export function createLazyComponent(
  importFn,
  {
    Loading = DefaultLoading,
    Error = DefaultError,
    name = 'LazyComponent',
    trackPerformance = true
  } = {}
) {
  // Create lazy component with performance tracking
  const LazyComponent = lazy(() => {
    // Start measuring load time
    if (trackPerformance) {
      startMeasure(`${name}_lazy_load`);
    }
    
    return importFn()
      .then(module => {
        // End measuring load time
        if (trackPerformance) {
          endMeasure(`${name}_lazy_load`, {
            category: 'code_splitting',
            metadata: { component: name }
          });
        }
        
        return module;
      })
      .catch(error => {
        console.error(`Failed to load ${name}:`, error);
        throw error;
      });
  });
  
  // Create wrapper component with Suspense
  const WrappedComponent = (props) => {
    const [error, setError] = React.useState(null);
    
    // Handle errors
    const handleError = (err) => {
      console.error(`Error rendering ${name}:`, err);
      setError(err);
    };
    
    // Retry loading
    const retry = () => {
      setError(null);
    };
    
    // If there was an error, show error component
    if (error) {
      return <Error error={error} retry={retry} />;
    }
    
    return (
      <Suspense fallback={<Loading />}>
        <ErrorBoundary onError={handleError} name={name}>
          <LazyComponent {...props} />
        </ErrorBoundary>
      </Suspense>
    );
  };
  
  WrappedComponent.displayName = `Lazy(${name})`;
  
  return WrappedComponent;
}

/**
 * Error boundary component
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  componentDidCatch(error, info) {
    if (this.props.onError) {
      this.props.onError(error, info);
    }
  }
  
  render() {
    if (this.state.hasError) {
      return null; // Parent will handle the error
    }
    
    return this.props.children;
  }
}

/**
 * Create a lazy-loaded route component
 * 
 * @param {Function} importFn - Dynamic import function
 * @param {Object} options - Options
 * @returns {Object} - Route object with lazy component
 */
export function createLazyRoute(importFn, options = {}) {
  const { name = 'LazyRoute', ...rest } = options;
  
  return {
    element: createLazyComponent(importFn, { name, ...rest }),
    ...rest
  };
}