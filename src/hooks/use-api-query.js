import { useState, useEffect, useCallback, useRef } from 'react';
import { apiRequest } from '@/api/apiClient';

// In-memory cache for API queries
const queryCache = new Map();

/**
 * Generate a cache key from query function and dependencies
 * 
 * @param {Function} queryFn - The query function
 * @param {Array} dependencies - Query dependencies
 * @returns {string} - Cache key
 */
function generateCacheKey(queryFn, dependencies = []) {
  // Use function name or toString() as part of the key
  const fnKey = queryFn.name || queryFn.toString().slice(0, 100);
  // Stringify dependencies to include in cache key
  const depsKey = JSON.stringify(dependencies);
  return `${fnKey}:${depsKey}`;
}

/**
 * Custom hook for API data fetching with loading, error, caching and refetch capabilities
 * 
 * @param {Function} queryFn - Function that returns a promise with the data
 * @param {Object} options - Hook options
 * @param {boolean} [options.enabled=true] - Whether to execute the query automatically
 * @param {any} [options.initialData=null] - Initial data to use before the query is executed
 * @param {Function} [options.onSuccess] - Callback for successful queries
 * @param {Function} [options.onError] - Callback for failed queries
 * @param {Array<any>} [options.dependencies=[]] - Dependencies array to trigger refetch
 * @param {boolean} [options.cacheEnabled=true] - Whether to use cache
 * @param {number} [options.cacheTTL=5*60*1000] - Cache TTL in milliseconds (default: 5 minutes)
 * @param {boolean} [options.staleWhileRevalidate=true] - Return cached data while fetching fresh data
 * @returns {Object} - Query result object
 */
export function useApiQuery(queryFn, options = {}) {
  const {
    enabled = true,
    initialData = null,
    onSuccess,
    onError,
    dependencies = [],
    cacheEnabled = true,
    cacheTTL = 5 * 60 * 1000, // 5 minutes default
    staleWhileRevalidate = true
  } = options;

  const [data, setData] = useState(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState(null);
  const [isStale, setIsStale] = useState(false);
  
  // Use ref for the cache key to avoid recreating it on every render
  const cacheKeyRef = useRef(generateCacheKey(queryFn, dependencies));
  
  // Check if we have cached data on mount
  useEffect(() => {
    if (cacheEnabled && queryCache.has(cacheKeyRef.current)) {
      const cachedData = queryCache.get(cacheKeyRef.current);
      if (Date.now() < cachedData.expiresAt) {
        setData(cachedData.data);
        setIsStale(false);
      } else if (staleWhileRevalidate) {
        // Data is stale but we'll use it while fetching fresh data
        setData(cachedData.data);
        setIsStale(true);
      }
    }
  }, [cacheEnabled, staleWhileRevalidate]);

  const fetchData = useCallback(async (options = {}) => {
    const { skipCache = false } = options;
    
    if (!enabled) return;
    
    // Check cache first if enabled and not explicitly skipped
    if (cacheEnabled && !skipCache) {
      const cacheKey = cacheKeyRef.current;
      const cachedData = queryCache.get(cacheKey);
      
      if (cachedData && Date.now() < cachedData.expiresAt) {
        // Return cached data if it's still valid
        setData(cachedData.data);
        setIsStale(false);
        return cachedData.data;
      } else if (cachedData && staleWhileRevalidate) {
        // Use stale data while fetching
        setData(cachedData.data);
        setIsStale(true);
      }
    }
    
    // Set loading state based on whether we have stale data
    if (!staleWhileRevalidate || !data) {
      setIsLoading(true);
    }
    setIsFetching(true);
    setError(null);
    
    try {
      const result = await apiRequest(queryFn, {
        showErrorToast: false,
        onSuccess,
        onError
      });
      
      // Update state with fresh data
      setData(result);
      setIsStale(false);
      
      // Cache the result if caching is enabled
      if (cacheEnabled) {
        queryCache.set(cacheKeyRef.current, {
          data: result,
          expiresAt: Date.now() + cacheTTL
        });
      }
      
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
      setIsFetching(false);
    }
  }, [queryFn, enabled, onSuccess, onError, cacheEnabled, cacheTTL, staleWhileRevalidate, data, ...dependencies]);

  // Fetch data when enabled or dependencies change
  useEffect(() => {
    if (enabled) {
      fetchData().catch(err => {
        console.error('Error in useApiQuery:', err);
      });
    }
  }, [fetchData, enabled]);

  // Function to invalidate cache for this query
  const invalidateCache = useCallback(() => {
    if (cacheEnabled) {
      queryCache.delete(cacheKeyRef.current);
    }
  }, [cacheEnabled]);

  return {
    data,
    isLoading,
    isFetching,
    isStale,
    error,
    refetch: (options) => fetchData(options),
    setData,
    invalidateCache
  };
}

/**
 * Custom hook for API mutations with loading and error states
 * 
 * @param {Function} mutationFn - Function that returns a promise with the mutation result
 * @param {Object} options - Hook options
 * @param {boolean} [options.showSuccessToast=false] - Whether to show a success toast
 * @param {boolean} [options.showErrorToast=true] - Whether to show an error toast
 * @param {string} [options.successMessage] - Custom success message
 * @param {string} [options.errorMessage] - Custom error message
 * @param {Function} [options.onSuccess] - Callback for successful mutations
 * @param {Function} [options.onError] - Callback for failed mutations
 * @returns {Object} - Mutation result object
 */
export function useApiMutation(mutationFn, options = {}) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const mutate = async (variables) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await apiRequest(() => mutationFn(variables), options);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    mutate,
    isLoading,
    error,
    data,
    reset: () => {
      setData(null);
      setError(null);
    }
  };
}