import { createClient } from '@base44/sdk';
import { toast } from 'sonner';

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
 * Enhanced API request wrapper with error handling
 * 
 * @param {Function} apiCall - The API function to call
 * @param {Object} options - Options for the API call
 * @param {boolean} [options.showSuccessToast=false] - Whether to show a success toast
 * @param {boolean} [options.showErrorToast=true] - Whether to show an error toast
 * @param {string} [options.successMessage] - Custom success message
 * @param {string} [options.errorMessage] - Custom error message
 * @param {Function} [options.onSuccess] - Callback for successful API calls
 * @param {Function} [options.onError] - Callback for failed API calls
 * @returns {Promise<any>} - The API response
 */
export async function apiRequest(apiCall, options = {}) {
  const {
    showSuccessToast = false,
    showErrorToast = true,
    successMessage,
    errorMessage,
    onSuccess,
    onError
  } = options;

  try {
    const response = await apiCall();
    
    if (showSuccessToast && successMessage) {
      toast.success(successMessage);
    }
    
    if (onSuccess) {
      onSuccess(response);
    }
    
    return response;
  } catch (error) {
    console.error('API Error:', error);
    
    if (showErrorToast) {
      toast.error(
        errorMessage || 
        error.message || 
        'An error occurred while processing your request'
      );
    }
    
    if (onError) {
      onError(error);
    }
    
    throw error;
  }
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