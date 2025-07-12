/**
 * Data transformation utility functions
 * 
 * This utility provides functions for transforming data structures.
 */

/**
 * Group an array of objects by a key
 * 
 * @param {Array<Object>} array - Array to group
 * @param {string|Function} key - Key to group by or function that returns the key
 * @returns {Object} - Grouped object
 */
export function groupBy(array, key) {
  return array.reduce((result, item) => {
    const groupKey = typeof key === 'function' ? key(item) : item[key];
    
    // Create the group if it doesn't exist
    if (!result[groupKey]) {
      result[groupKey] = [];
    }
    
    // Add the item to the group
    result[groupKey].push(item);
    
    return result;
  }, {});
}

/**
 * Sort an array of objects by a key
 * 
 * @param {Array<Object>} array - Array to sort
 * @param {string|Function} key - Key to sort by or function that returns the value
 * @param {string} [direction='asc'] - Sort direction ('asc' or 'desc')
 * @returns {Array<Object>} - Sorted array
 */
export function sortBy(array, key, direction = 'asc') {
  const sortedArray = [...array];
  const multiplier = direction === 'desc' ? -1 : 1;
  
  return sortedArray.sort((a, b) => {
    const valueA = typeof key === 'function' ? key(a) : a[key];
    const valueB = typeof key === 'function' ? key(b) : b[key];
    
    if (valueA < valueB) return -1 * multiplier;
    if (valueA > valueB) return 1 * multiplier;
    return 0;
  });
}

/**
 * Filter an array of objects by a predicate
 * 
 * @param {Array<Object>} array - Array to filter
 * @param {Object|Function} predicate - Filter predicate
 * @returns {Array<Object>} - Filtered array
 */
export function filterBy(array, predicate) {
  if (typeof predicate === 'function') {
    return array.filter(predicate);
  }
  
  return array.filter(item => {
    return Object.entries(predicate).every(([key, value]) => {
      return item[key] === value;
    });
  });
}

/**
 * Map an array of objects to a new structure
 * 
 * @param {Array<Object>} array - Array to map
 * @param {Object|Function} mapper - Mapping definition or function
 * @returns {Array<Object>} - Mapped array
 */
export function mapTo(array, mapper) {
  if (typeof mapper === 'function') {
    return array.map(mapper);
  }
  
  return array.map(item => {
    const result = {};
    
    Object.entries(mapper).forEach(([targetKey, sourceKey]) => {
      if (typeof sourceKey === 'function') {
        result[targetKey] = sourceKey(item);
      } else {
        result[targetKey] = item[sourceKey];
      }
    });
    
    return result;
  });
}

/**
 * Convert an array to a lookup object
 * 
 * @param {Array<Object>} array - Array to convert
 * @param {string|Function} key - Key to use as the lookup key
 * @returns {Object} - Lookup object
 */
export function arrayToObject(array, key) {
  return array.reduce((result, item) => {
    const lookupKey = typeof key === 'function' ? key(item) : item[key];
    result[lookupKey] = item;
    return result;
  }, {});
}

/**
 * Flatten a nested array
 * 
 * @param {Array} array - Array to flatten
 * @param {number} [depth=Infinity] - Maximum recursion depth
 * @returns {Array} - Flattened array
 */
export function flatten(array, depth = Infinity) {
  return array.flat(depth);
}

/**
 * Create a unique array by removing duplicates
 * 
 * @param {Array} array - Array with potential duplicates
 * @param {string|Function} [key] - Key to use for comparison or function that returns the key
 * @returns {Array} - Array with duplicates removed
 */
export function unique(array, key) {
  if (!key) {
    return [...new Set(array)];
  }
  
  const seen = new Set();
  
  return array.filter(item => {
    const value = typeof key === 'function' ? key(item) : item[key];
    
    if (seen.has(value)) {
      return false;
    }
    
    seen.add(value);
    return true;
  });
}

/**
 * Chunk an array into smaller arrays
 * 
 * @param {Array} array - Array to chunk
 * @param {number} size - Chunk size
 * @returns {Array<Array>} - Array of chunks
 */
export function chunk(array, size) {
  return Array.from(
    { length: Math.ceil(array.length / size) },
    (_, index) => array.slice(index * size, (index + 1) * size)
  );
}