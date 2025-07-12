import { useState, useCallback } from 'react';
import { toast } from 'sonner';

/**
 * Custom hook for handling errors with toast notifications
 * 
 * @param {Object} options - Hook options
 * @param {string} [options.defaultMessage='An error occurred'] - Default error message
 * @param {boolean} [options.showToast=true] - Whether to show toast notifications
 * @returns {Object} - Error handling utilities
 */
export function useErrorHandler({
  defaultMessage = 'An error occurred',
  showToast = true
} = {}) {
  const [error, setError] = useState(null);
  const [isError, setIsError] = useState(false);

  /**
   * Handle an error
   * 
   * @param {Error|string} err - The error to handle
   * @param {string} [customMessage] - Custom error message
   */
  const handleError = useCallback((err, customMessage) => {
    const errorObj = err instanceof Error ? err : new Error(err || defaultMessage);
    
    setError(errorObj);
    setIsError(true);
    
    if (showToast) {
      toast.error(customMessage || errorObj.message || defaultMessage);
    }
    
    console.error('Error handled:', errorObj);
    
    return errorObj;
  }, [defaultMessage, showToast]);

  /**
   * Clear the error state
   */
  const clearError = useCallback(() => {
    setError(null);
    setIsError(false);
  }, []);

  /**
   * Wrap a function with error handling
   * 
   * @param {Function} fn - The function to wrap
   * @param {string} [customMessage] - Custom error message
   * @returns {Function} - Wrapped function
   */
  const withErrorHandling = useCallback((fn, customMessage) => {
    return async (...args) => {
      try {
        clearError();
        return await fn(...args);
      } catch (err) {
        handleError(err, customMessage);
        throw err;
      }
    };
  }, [handleError, clearError]);

  return {
    error,
    isError,
    handleError,
    clearError,
    withErrorHandling
  };
}