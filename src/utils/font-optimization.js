/**
 * Font optimization utilities
 * 
 * This module provides utilities for optimizing font loading and rendering.
 */

/**
 * Font display strategies
 */
export const FontDisplay = {
  AUTO: 'auto',
  BLOCK: 'block',
  SWAP: 'swap',
  FALLBACK: 'fallback',
  OPTIONAL: 'optional'
};

/**
 * Load a font with optimized settings
 * 
 * @param {Object} options - Font options
 * @param {string} options.family - Font family name
 * @param {Array<string>} [options.weights=['400', '700']] - Font weights to load
 * @param {string} [options.display='swap'] - Font display strategy
 * @param {boolean} [options.preload=false] - Whether to preload the font
 * @param {string} [options.unicodeRange] - Unicode range to load
 * @returns {void}
 */
export function loadFont({
  family,
  weights = ['400', '700'],
  display = FontDisplay.SWAP,
  preload = false,
  unicodeRange
}) {
  if (typeof window === 'undefined' || !family) return;
  
  // Create a Google Fonts URL
  const url = createGoogleFontUrl({
    family,
    weights,
    display,
    unicodeRange
  });
  
  // If preload is true, create a preload link
  if (preload) {
    const preloadLink = document.createElement('link');
    preloadLink.rel = 'preload';
    preloadLink.as = 'style';
    preloadLink.href = url;
    document.head.appendChild(preloadLink);
  }
  
  // Create a stylesheet link
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = url;
  document.head.appendChild(link);
}

/**
 * Create a Google Fonts URL
 * 
 * @param {Object} options - Font options
 * @param {string} options.family - Font family name
 * @param {Array<string>} [options.weights=['400', '700']] - Font weights to load
 * @param {string} [options.display='swap'] - Font display strategy
 * @param {string} [options.unicodeRange] - Unicode range to load
 * @returns {string} - Google Fonts URL
 */
export function createGoogleFontUrl({
  family,
  weights = ['400', '700'],
  display = FontDisplay.SWAP,
  unicodeRange
}) {
  // Format family name for URL
  const formattedFamily = family.replace(/\s+/g, '+');
  
  // Format weights
  const formattedWeights = weights.join(',');
  
  // Build URL
  let url = `https://fonts.googleapis.com/css2?family=${formattedFamily}:wght@${formattedWeights}`;
  
  // Add display strategy
  url += `&display=${display}`;
  
  // Add unicode range if provided
  if (unicodeRange) {
    url += `&unicode-range=${unicodeRange}`;
  }
  
  return url;
}

/**
 * Create a font-face CSS rule
 * 
 * @param {Object} options - Font options
 * @param {string} options.family - Font family name
 * @param {string} options.url - Font file URL
 * @param {string} [options.weight='400'] - Font weight
 * @param {string} [options.style='normal'] - Font style
 * @param {string} [options.display='swap'] - Font display strategy
 * @param {string} [options.unicodeRange] - Unicode range
 * @returns {string} - CSS @font-face rule
 */
export function createFontFaceRule({
  family,
  url,
  weight = '400',
  style = 'normal',
  display = FontDisplay.SWAP,
  unicodeRange
}) {
  let rule = `@font-face {
  font-family: '${family}';
  font-weight: ${weight};
  font-style: ${style};
  font-display: ${display};
  src: url('${url}') format('woff2');`;
  
  if (unicodeRange) {
    rule += `\n  unicode-range: ${unicodeRange};`;
  }
  
  rule += '\n}';
  
  return rule;
}

/**
 * Add a font-face rule to the document
 * 
 * @param {Object} options - Font options
 * @returns {void}
 */
export function addFontFace(options) {
  if (typeof window === 'undefined') return;
  
  const rule = createFontFaceRule(options);
  
  // Create a style element
  const style = document.createElement('style');
  style.appendChild(document.createTextNode(rule));
  document.head.appendChild(style);
}

/**
 * Optimize font loading for the application
 * 
 * @param {Array<Object>} fonts - Fonts to load
 * @returns {void}
 */
export function optimizeFonts(fonts) {
  if (typeof window === 'undefined') return;
  
  // Add font-display to existing font-face rules
  const styleSheets = document.styleSheets;
  
  for (let i = 0; i < styleSheets.length; i++) {
    try {
      const rules = styleSheets[i].cssRules || styleSheets[i].rules;
      
      if (!rules) continue;
      
      for (let j = 0; j < rules.length; j++) {
        const rule = rules[j];
        
        if (rule.type === CSSRule.FONT_FACE_RULE && !rule.style.fontDisplay) {
          rule.style.fontDisplay = FontDisplay.SWAP;
        }
      }
    } catch (e) {
      // Skip cross-origin stylesheets
      console.warn('Could not access stylesheet rules', e);
    }
  }
  
  // Load specified fonts
  fonts.forEach(font => loadFont(font));
}