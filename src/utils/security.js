/**
 * Security utility functions
 * 
 * This utility provides functions for enhancing application security.
 */

/**
 * Sanitize HTML to prevent XSS attacks
 * 
 * @param {string} html - HTML string to sanitize
 * @returns {string} - Sanitized HTML
 */
export function sanitizeHtml(html) {
  if (!html) return '';
  
  // Simple implementation - in production, use a library like DOMPurify
  return html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Generate a random string (e.g., for CSRF tokens)
 * 
 * @param {number} length - Length of the string
 * @returns {string} - Random string
 */
export function generateRandomString(length = 32) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  
  // Use crypto API if available for better randomness
  if (window.crypto && window.crypto.getRandomValues) {
    const values = new Uint32Array(length);
    window.crypto.getRandomValues(values);
    
    for (let i = 0; i < length; i++) {
      result += chars[values[i] % chars.length];
    }
  } else {
    // Fallback to Math.random
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
  }
  
  return result;
}

/**
 * Check if a password is compromised using k-anonymity
 * 
 * This is a placeholder implementation. In a real application,
 * you would use a service like "Have I Been Pwned" API.
 * 
 * @param {string} password - Password to check
 * @returns {Promise<boolean>} - Whether the password is compromised
 */
export async function isPasswordCompromised(password) {
  // This is a placeholder - in a real implementation, you would:
  // 1. Hash the password with SHA-1
  // 2. Take the first 5 characters of the hash
  // 3. Send those to an API like HIBP
  // 4. Check if the rest of the hash is in the response
  
  console.log('Checking if password is compromised (placeholder)');
  
  // Simulate API call
  return new Promise(resolve => {
    setTimeout(() => {
      // For demo purposes, consider common passwords compromised
      const commonPasswords = [
        'password',
        '123456',
        'qwerty',
        'admin',
        'welcome',
        'password123'
      ];
      
      resolve(commonPasswords.includes(password.toLowerCase()));
    }, 500);
  });
}

/**
 * Mask sensitive data (e.g., for logging)
 * 
 * @param {string} value - Value to mask
 * @param {number} [visibleChars=4] - Number of visible characters
 * @param {string} [maskChar='*'] - Character to use for masking
 * @returns {string} - Masked value
 */
export function maskSensitiveData(value, visibleChars = 4, maskChar = '*') {
  if (!value) return '';
  
  const valueStr = String(value);
  
  if (valueStr.length <= visibleChars) {
    return valueStr;
  }
  
  const visiblePart = valueStr.slice(-visibleChars);
  const maskedPart = maskChar.repeat(valueStr.length - visibleChars);
  
  return maskedPart + visiblePart;
}

/**
 * Validate Content Security Policy
 * 
 * @param {Object} policy - CSP directives
 * @returns {string} - CSP header value
 */
export function buildCspHeader(policy) {
  return Object.entries(policy)
    .map(([directive, sources]) => {
      if (Array.isArray(sources)) {
        return `${directive} ${sources.join(' ')}`;
      }
      return `${directive} ${sources}`;
    })
    .join('; ');
}