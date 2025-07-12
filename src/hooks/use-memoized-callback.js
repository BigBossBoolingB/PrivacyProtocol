import { useCallback, useRef } from 'react';

/**
 * Custom hook for memoizing callbacks with deep dependency comparison
 * 
 * This hook is similar to useCallback but performs deep comparison of dependencies
 * to prevent unnecessary callback recreation when dependencies are equivalent but
 * not referentially equal.
 * 
 * @param {Function} callback - The callback function to memoize
 * @param {Array} dependencies - Array of dependencies
 * @returns {Function} - Memoized callback
 */
export function useMemoizedCallback(callback, dependencies) {
  // Store the previous dependencies and callback
  const ref = useRef({
    dependencies: null,
    callback,
    memoizedCallback: null
  });

  // Check if dependencies have changed
  const depsChanged = areDepsChanged(dependencies, ref.current.dependencies);

  // If callback or dependencies changed, update the memoized callback
  if (callback !== ref.current.callback || depsChanged) {
    ref.current.dependencies = dependencies;
    ref.current.callback = callback;
    ref.current.memoizedCallback = (...args) => ref.current.callback(...args);
  }

  return ref.current.memoizedCallback;
}

/**
 * Deep compare two dependency arrays
 * 
 * @param {Array} newDeps - New dependencies
 * @param {Array} prevDeps - Previous dependencies
 * @returns {boolean} - Whether dependencies have changed
 */
function areDepsChanged(newDeps, prevDeps) {
  // If either is null, consider changed
  if (!newDeps || !prevDeps) return true;
  
  // Different lengths means changed
  if (newDeps.length !== prevDeps.length) return true;
  
  // Compare each dependency
  for (let i = 0; i < newDeps.length; i++) {
    const a = newDeps[i];
    const b = prevDeps[i];
    
    // If both are objects, do a deep comparison
    if (isObject(a) && isObject(b)) {
      if (!deepEqual(a, b)) return true;
    } 
    // Otherwise do a simple comparison
    else if (a !== b) {
      return true;
    }
  }
  
  return false;
}

/**
 * Check if a value is an object
 * 
 * @param {any} value - Value to check
 * @returns {boolean} - Whether the value is an object
 */
function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

/**
 * Deep equality check for objects
 * 
 * @param {Object} a - First object
 * @param {Object} b - Second object
 * @returns {boolean} - Whether the objects are deeply equal
 */
function deepEqual(a, b) {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);
  
  if (keysA.length !== keysB.length) return false;
  
  for (const key of keysA) {
    const valA = a[key];
    const valB = b[key];
    
    if (isObject(valA) && isObject(valB)) {
      if (!deepEqual(valA, valB)) return false;
    } else if (Array.isArray(valA) && Array.isArray(valB)) {
      if (!arraysEqual(valA, valB)) return false;
    } else if (valA !== valB) {
      return false;
    }
  }
  
  return true;
}

/**
 * Deep equality check for arrays
 * 
 * @param {Array} a - First array
 * @param {Array} b - Second array
 * @returns {boolean} - Whether the arrays are deeply equal
 */
function arraysEqual(a, b) {
  if (a.length !== b.length) return false;
  
  for (let i = 0; i < a.length; i++) {
    const valA = a[i];
    const valB = b[i];
    
    if (isObject(valA) && isObject(valB)) {
      if (!deepEqual(valA, valB)) return false;
    } else if (Array.isArray(valA) && Array.isArray(valB)) {
      if (!arraysEqual(valA, valB)) return false;
    } else if (valA !== valB) {
      return false;
    }
  }
  
  return true;
}