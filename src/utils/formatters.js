import { format, formatDistance, formatRelative } from 'date-fns';

/**
 * Format a date using date-fns
 * 
 * @param {Date|string|number} date - The date to format
 * @param {string} formatString - The format string (date-fns format)
 * @param {Object} options - Additional options for date-fns
 * @returns {string} - Formatted date string
 */
export function formatDate(date, formatString = 'MMM d, yyyy', options = {}) {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return format(dateObj, formatString, options);
  } catch (error) {
    console.error('Error formatting date:', error);
    return '';
  }
}

/**
 * Format a date as a relative time (e.g., "5 minutes ago")
 * 
 * @param {Date|string|number} date - The date to format
 * @param {Date} baseDate - The base date to compare against (defaults to now)
 * @param {Object} options - Additional options for date-fns
 * @returns {string} - Formatted relative date string
 */
export function formatRelativeTime(date, baseDate = new Date(), options = {}) {
  if (!date) return '';
  
  try {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return formatDistance(dateObj, baseDate, { addSuffix: true, ...options });
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return '';
  }
}

/**
 * Format a number as currency
 * 
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code
 * @param {string} locale - The locale
 * @returns {string} - Formatted currency string
 */
export function formatCurrency(amount, currency = 'USD', locale = 'en-US') {
  if (amount === null || amount === undefined) return '';
  
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency
    }).format(amount);
  } catch (error) {
    console.error('Error formatting currency:', error);
    return '';
  }
}

/**
 * Format a number with commas
 * 
 * @param {number} number - The number to format
 * @param {number} decimals - Number of decimal places
 * @param {string} locale - The locale
 * @returns {string} - Formatted number string
 */
export function formatNumber(number, decimals = 0, locale = 'en-US') {
  if (number === null || number === undefined) return '';
  
  try {
    return new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(number);
  } catch (error) {
    console.error('Error formatting number:', error);
    return '';
  }
}

/**
 * Format a percentage
 * 
 * @param {number} value - The value to format (0-1)
 * @param {number} decimals - Number of decimal places
 * @param {string} locale - The locale
 * @returns {string} - Formatted percentage string
 */
export function formatPercentage(value, decimals = 0, locale = 'en-US') {
  if (value === null || value === undefined) return '';
  
  try {
    return new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  } catch (error) {
    console.error('Error formatting percentage:', error);
    return '';
  }
}

/**
 * Truncate text with ellipsis
 * 
 * @param {string} text - The text to truncate
 * @param {number} length - Maximum length
 * @param {string} ellipsis - Ellipsis string
 * @returns {string} - Truncated text
 */
export function truncateText(text, length = 100, ellipsis = '...') {
  if (!text) return '';
  
  if (text.length <= length) return text;
  
  return text.slice(0, length) + ellipsis;
}

/**
 * Format a file size
 * 
 * @param {number} bytes - Size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} - Formatted file size
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
}