/**
 * Image optimization utilities
 * 
 * This module provides utilities for optimizing images in the application.
 */

/**
 * Generate a responsive image URL with appropriate size
 * 
 * @param {string} url - Original image URL
 * @param {Object} options - Options
 * @param {number} [options.width] - Desired width
 * @param {number} [options.height] - Desired height
 * @param {string} [options.format='webp'] - Image format (webp, jpeg, png)
 * @param {number} [options.quality=80] - Image quality (1-100)
 * @returns {string} - Optimized image URL
 */
export function getOptimizedImageUrl(url, options = {}) {
  if (!url) return '';
  
  const {
    width,
    height,
    format = 'webp',
    quality = 80
  } = options;
  
  // If URL is already from an image optimization service, return as is
  if (url.includes('imagedelivery.net') || url.includes('imagecdn.app')) {
    return url;
  }
  
  // For demo purposes, we'll just append query parameters
  // In a real app, you would use an image optimization service or CDN
  const params = new URLSearchParams();
  
  if (width) params.append('w', width.toString());
  if (height) params.append('h', height.toString());
  if (format) params.append('fmt', format);
  if (quality) params.append('q', quality.toString());
  
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}${params.toString()}`;
}

/**
 * Generate a set of srcset URLs for responsive images
 * 
 * @param {string} url - Original image URL
 * @param {Object} options - Options
 * @param {Array<number>} [options.widths=[640, 750, 828, 1080, 1200, 1920]] - Widths to generate
 * @param {string} [options.format='webp'] - Image format
 * @param {number} [options.quality=80] - Image quality
 * @returns {string} - srcset attribute value
 */
export function generateSrcSet(url, options = {}) {
  if (!url) return '';
  
  const {
    widths = [640, 750, 828, 1080, 1200, 1920],
    format = 'webp',
    quality = 80
  } = options;
  
  return widths
    .map(width => {
      const optimizedUrl = getOptimizedImageUrl(url, { width, format, quality });
      return `${optimizedUrl} ${width}w`;
    })
    .join(', ');
}

/**
 * Calculate image dimensions to maintain aspect ratio
 * 
 * @param {Object} originalDimensions - Original dimensions
 * @param {number} originalDimensions.width - Original width
 * @param {number} originalDimensions.height - Original height
 * @param {Object} constraints - Constraints
 * @param {number} [constraints.maxWidth] - Maximum width
 * @param {number} [constraints.maxHeight] - Maximum height
 * @returns {Object} - New dimensions
 */
export function calculateImageDimensions(originalDimensions, constraints = {}) {
  const { width: originalWidth, height: originalHeight } = originalDimensions;
  const { maxWidth, maxHeight } = constraints;
  
  // If no constraints, return original dimensions
  if (!maxWidth && !maxHeight) {
    return { width: originalWidth, height: originalHeight };
  }
  
  // Calculate aspect ratio
  const aspectRatio = originalWidth / originalHeight;
  
  // Initialize with original dimensions
  let width = originalWidth;
  let height = originalHeight;
  
  // Apply maxWidth constraint
  if (maxWidth && width > maxWidth) {
    width = maxWidth;
    height = width / aspectRatio;
  }
  
  // Apply maxHeight constraint
  if (maxHeight && height > maxHeight) {
    height = maxHeight;
    width = height * aspectRatio;
  }
  
  // Round dimensions to avoid subpixel rendering issues
  return {
    width: Math.round(width),
    height: Math.round(height)
  };
}

/**
 * Create an optimized image component props
 * 
 * @param {string} src - Image source URL
 * @param {Object} options - Options
 * @returns {Object} - Image props
 */
export function createOptimizedImageProps(src, options = {}) {
  const {
    width,
    height,
    sizes = '100vw',
    loading = 'lazy',
    decoding = 'async',
    alt = '',
    ...rest
  } = options;
  
  return {
    src: getOptimizedImageUrl(src, { width, height }),
    srcSet: generateSrcSet(src),
    sizes,
    width,
    height,
    loading,
    decoding,
    alt,
    ...rest
  };
}