import { useState, useRef, useCallback, useEffect } from 'react';

/**
 * Hook for batching multiple state updates to reduce renders
 * 
 * This is useful when you need to update multiple pieces of state
 * in response to a single event or API call, but want to avoid
 * multiple re-renders.
 * 
 * @param {Object} initialState - Initial state object
 * @param {Object} [options] - Options
 * @param {number} [options.batchDelay=0] - Delay in ms before applying batched updates
 * @returns {Array} - [state, setState, flushUpdates]
 */
export function useBatchedState(initialState, { batchDelay = 0 } = {}) {
  // Store the state
  const [state, setStateInternal] = useState(initialState);
  
  // Store pending updates
  const pendingUpdates = useRef({});
  
  // Store timeout ID
  const timeoutId = useRef(null);
  
  // Store whether we have pending updates
  const hasPendingUpdates = useRef(false);
  
  // Apply all pending updates
  const flushUpdates = useCallback(() => {
    if (!hasPendingUpdates.current) return;
    
    // Clear any existing timeout
    if (timeoutId.current !== null) {
      clearTimeout(timeoutId.current);
      timeoutId.current = null;
    }
    
    // Apply all pending updates
    setStateInternal(currentState => ({
      ...currentState,
      ...pendingUpdates.current
    }));
    
    // Reset pending updates
    pendingUpdates.current = {};
    hasPendingUpdates.current = false;
  }, []);
  
  // Schedule updates to be applied
  const scheduleUpdates = useCallback(() => {
    if (timeoutId.current !== null) {
      clearTimeout(timeoutId.current);
    }
    
    if (batchDelay <= 0) {
      flushUpdates();
    } else {
      timeoutId.current = setTimeout(flushUpdates, batchDelay);
    }
  }, [flushUpdates, batchDelay]);
  
  // Set state function that batches updates
  const setState = useCallback((updates) => {
    // Store updates
    pendingUpdates.current = {
      ...pendingUpdates.current,
      ...(typeof updates === 'function' 
        ? updates(state) 
        : updates)
    };
    
    hasPendingUpdates.current = true;
    
    // Schedule updates
    scheduleUpdates();
  }, [state, scheduleUpdates]);
  
  // Flush updates on unmount
  useEffect(() => {
    return () => {
      if (timeoutId.current !== null) {
        clearTimeout(timeoutId.current);
      }
      
      if (hasPendingUpdates.current) {
        flushUpdates();
      }
    };
  }, [flushUpdates]);
  
  return [state, setState, flushUpdates];
}