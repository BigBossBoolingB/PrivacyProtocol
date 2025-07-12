import { useState, useCallback } from 'react';

export const useErrorBoundary = () => {
  const [error, setError] = useState(null);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  const captureError = useCallback((error, errorInfo = {}) => {
    setError({ error, errorInfo });
    
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'exception', {
        description: error.message,
        fatal: false,
        ...errorInfo
      });
    }
  }, []);

  return {
    error,
    resetError,
    captureError,
    hasError: error !== null
  };
};

export const useAsyncError = () => {
  const { captureError } = useErrorBoundary();

  const throwAsyncError = useCallback((error) => {
    captureError(error, { type: 'async' });
    throw error;
  }, [captureError]);

  return throwAsyncError;
};
