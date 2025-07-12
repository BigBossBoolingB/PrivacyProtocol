import { useState, useCallback } from 'react';

interface ErrorInfo {
  error: Error;
  errorInfo: Record<string, any>;
}

export const useErrorBoundary = () => {
  const [error, setError] = useState<ErrorInfo | null>(null);

  const resetError = useCallback(() => {
    setError(null);
  }, []);

  const captureError = useCallback((error: Error, errorInfo: Record<string, any> = {}) => {
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

  const throwAsyncError = useCallback((error: Error) => {
    captureError(error, { type: 'async' });
    throw error;
  }, [captureError]);

  return throwAsyncError;
};
