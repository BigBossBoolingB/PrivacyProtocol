import { createClient } from '@base44/sdk';
import { toast } from 'sonner';

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
const cache = new Map();

/**
 * Configuration for the Base44 API client
 */
const API_CONFIG = {
  appId: "686ffa24aa92f0de3396591f",
  requiresAuth: true
};

/**
 * Create the Base44 API client instance
 */
export const base44 = createClient(API_CONFIG);

/**
 * Enhanced API request wrapper with caching and error handling
 * 
 * @param {Function} apiCall - The API function to call
 * @param {Object} options - Options for the API call
 * @param {boolean} [options.enableCache=true] - Whether to enable caching
 * @param {string} [options.cacheKey] - Custom cache key
 * @param {boolean} [options.showSuccessToast=false] - Whether to show a success toast
 * @param {boolean} [options.showErrorToast=true] - Whether to show an error toast
 * @param {string} [options.successMessage] - Custom success message
 * @param {string} [options.errorMessage] - Custom error message
 * @param {Function} [options.onSuccess] - Callback for successful API calls
 * @param {Function} [options.onError] - Callback for failed API calls
 * @param {number} [options.retries=3] - Number of retry attempts
 * @param {number} [options.timeout=30000] - Request timeout in milliseconds
 * @returns {Promise<any>} - The API response
 */
export async function apiRequest(apiCall, options = {}) {
  const {
    enableCache = true,
    cacheKey = null,
    showSuccessToast = false,
    showErrorToast = true,
    successMessage,
    errorMessage,
    onSuccess,
    onError,
    retries = 3,
    timeout = 30000
  } = options;

  const finalCacheKey = cacheKey || `${apiCall.name}_${JSON.stringify(arguments)}`;
  
  if (enableCache && cache.has(finalCacheKey)) {
    const cached = cache.get(finalCacheKey);
    if (Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data;
    }
    cache.delete(finalCacheKey);
  }

  let lastError;
  
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), timeout);
      });
      
      const result = await Promise.race([
        apiCall(),
        timeoutPromise
      ]);

      if (enableCache && result) {
        cache.set(finalCacheKey, {
          data: result,
          timestamp: Date.now()
        });
      }

      if (showSuccessToast && successMessage) {
        toast.success(successMessage);
      }
      
      if (onSuccess) {
        onSuccess(result);
      }
      
      return result;
    } catch (error) {
      lastError = error;
      
      if (error.status === 401 || error.status === 403) {
        break;
      }
      
      if (attempt < retries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
      }
    }
  }

  if (enableCache && cache.has(finalCacheKey)) {
    const cached = cache.get(finalCacheKey);
    console.warn('Using stale cached data due to API failure');
    return cached.data;
  }

  console.error('API Error:', lastError);
  
  if (showErrorToast) {
    toast.error(
      errorMessage || 
      lastError.message || 
      'An error occurred while processing your request'
    );
  }
  
  if (onError) {
    onError(lastError);
  }
  
  throw lastError;
}

/**
 * Check if the user's session is valid
 * 
 * @returns {Promise<boolean>} - Whether the session is valid
 */
export async function checkSession() {
  try {
    await base44.auth.me();
    return true;
  } catch (error) {
    return false;
  }
}
