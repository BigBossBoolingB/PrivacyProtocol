
/**
 * Main utilities export file
 */

// Export all utilities
export * from './formatters';
export * from './validators';
export * from './analytics';
export * from './error-tracking';
export * from './performance';
export * from './security';
export * from './accessibility';
export * from './cache';
export * from './data-transform';

/**
 * Create a URL for a page
 * 
 * @param {string} pageName - Name of the page
 * @returns {string} - URL for the page
 */
export function createPageUrl(pageName: string): string {
  return '/' + pageName.toLowerCase().replace(/ /g, '-');
}

/**
 * Combine class names with conditional logic
 * 
 * @param {...string} classes - Class names to combine
 * @returns {string} - Combined class names
 */
export function cn(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

/**
 * Sleep for a specified duration
 * 
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise<void>} - Promise that resolves after the specified duration
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Generate a UUID v4
 * 
 * @returns {string} - UUID v4
 */
export function uuidv4(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

/**
 * Check if a value is empty (null, undefined, empty string, empty array, empty object)
 * 
 * @param {any} value - Value to check
 * @returns {boolean} - Whether the value is empty
 */
export function isEmpty(value: any): boolean {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

/**
 * Deep clone an object
 * 
 * @param {any} obj - Object to clone
 * @returns {any} - Cloned object
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj;
  return JSON.parse(JSON.stringify(obj));
}