/**
 * Cache utility functions
 * 
 * This utility provides functions for caching data in memory and localStorage.
 */

// In-memory cache
const memoryCache = new Map();

/**
 * Set a value in the memory cache
 * 
 * @param {string} key - Cache key
 * @param {any} value - Value to cache
 * @param {number} [ttl] - Time to live in milliseconds
 */
export function setMemoryCache(key, value, ttl) {
  const item = {
    value,
    expiry: ttl ? Date.now() + ttl : null
  };
  
  memoryCache.set(key, item);
}

/**
 * Get a value from the memory cache
 * 
 * @param {string} key - Cache key
 * @returns {any|null} - Cached value or null if not found or expired
 */
export function getMemoryCache(key) {
  const item = memoryCache.get(key);
  
  if (!item) return null;
  
  // Check if expired
  if (item.expiry && item.expiry < Date.now()) {
    memoryCache.delete(key);
    return null;
  }
  
  return item.value;
}

/**
 * Remove a value from the memory cache
 * 
 * @param {string} key - Cache key
 */
export function removeMemoryCache(key) {
  memoryCache.delete(key);
}

/**
 * Clear the entire memory cache
 */
export function clearMemoryCache() {
  memoryCache.clear();
}

/**
 * Set a value in localStorage with optional expiry
 * 
 * @param {string} key - Cache key
 * @param {any} value - Value to cache
 * @param {number} [ttl] - Time to live in milliseconds
 */
export function setLocalStorageCache(key, value, ttl) {
  const item = {
    value,
    expiry: ttl ? Date.now() + ttl : null
  };
  
  try {
    localStorage.setItem(key, JSON.stringify(item));
  } catch (error) {
    console.error('Error setting localStorage cache:', error);
  }
}

/**
 * Get a value from localStorage
 * 
 * @param {string} key - Cache key
 * @returns {any|null} - Cached value or null if not found or expired
 */
export function getLocalStorageCache(key) {
  try {
    const itemStr = localStorage.getItem(key);
    
    if (!itemStr) return null;
    
    const item = JSON.parse(itemStr);
    
    // Check if expired
    if (item.expiry && item.expiry < Date.now()) {
      localStorage.removeItem(key);
      return null;
    }
    
    return item.value;
  } catch (error) {
    console.error('Error getting localStorage cache:', error);
    return null;
  }
}

/**
 * Remove a value from localStorage
 * 
 * @param {string} key - Cache key
 */
export function removeLocalStorageCache(key) {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing localStorage cache:', error);
  }
}

/**
 * Create a memoized version of a function
 * 
 * @param {Function} fn - Function to memoize
 * @param {Function} [keyFn] - Function to generate cache key from arguments
 * @returns {Function} - Memoized function
 */
export function memoize(fn, keyFn) {
  const cache = new Map();
  
  return function(...args) {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key);
    }
    
    const result = fn.apply(this, args);
    cache.set(key, result);
    
    return result;
  };
}

/**
 * Create a memoized version of an async function
 * 
 * @param {Function} fn - Async function to memoize
 * @param {Function} [keyFn] - Function to generate cache key from arguments
 * @param {number} [ttl] - Time to live in milliseconds
 * @returns {Function} - Memoized async function
 */
export function memoizeAsync(fn, keyFn, ttl) {
  const cache = new Map();
  
  return async function(...args) {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);
    
    const cachedItem = cache.get(key);
    
    if (cachedItem) {
      // Check if expired
      if (cachedItem.expiry && cachedItem.expiry < Date.now()) {
        cache.delete(key);
      } else {
        return cachedItem.value;
      }
    }
    
    const result = await fn.apply(this, args);
    
    cache.set(key, {
      value: result,
      expiry: ttl ? Date.now() + ttl : null
    });
    
    return result;
  };
}