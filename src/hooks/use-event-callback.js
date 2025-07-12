import { useRef, useCallback, useLayoutEffect } from 'react';

/**
 * Hook for creating stable event callbacks that can access the latest props/state
 * without causing unnecessary re-renders of child components
 * 
 * This is similar to useCallback but doesn't need a dependencies array and
 * always returns the same function reference while still accessing the latest values.
 * 
 * @param {Function} callback - The callback function
 * @returns {Function} - Stable callback function
 */
export function useEventCallback(callback) {
  // Store the callback in a ref
  const callbackRef = useRef(callback);
  
  // Update the ref whenever the callback changes
  useLayoutEffect(() => {
    callbackRef.current = callback;
  });
  
  // Return a stable callback that uses the ref
  return useCallback((...args) => {
    return callbackRef.current(...args);
  }, []);
}