/**
 * Accessibility utility functions
 * 
 * This utility provides functions for enhancing application accessibility.
 */

/**
 * Generate an ID for ARIA attributes
 * 
 * @param {string} prefix - ID prefix
 * @returns {string} - Unique ID
 */
export function generateAriaId(prefix = 'aria') {
  return `${prefix}-${Math.random().toString(36).substring(2, 11)}`;
}

/**
 * Focus first focusable element in a container
 * 
 * @param {HTMLElement} container - Container element
 * @returns {boolean} - Whether an element was focused
 */
export function focusFirstElement(container) {
  if (!container) return false;
  
  const focusableElements = getFocusableElements(container);
  
  if (focusableElements.length > 0) {
    focusableElements[0].focus();
    return true;
  }
  
  return false;
}

/**
 * Get all focusable elements in a container
 * 
 * @param {HTMLElement} container - Container element
 * @returns {Array<HTMLElement>} - Focusable elements
 */
export function getFocusableElements(container) {
  if (!container) return [];
  
  const focusableSelectors = [
    'a[href]:not([disabled])',
    'button:not([disabled])',
    'textarea:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    '[tabindex]:not([tabindex="-1"])'
  ];
  
  return Array.from(
    container.querySelectorAll(focusableSelectors.join(','))
  );
}

/**
 * Trap focus within a container (for modals, dialogs, etc.)
 * 
 * @param {HTMLElement} container - Container element
 * @returns {Function} - Cleanup function
 */
export function trapFocus(container) {
  if (!container) return () => {};
  
  const focusableElements = getFocusableElements(container);
  
  if (focusableElements.length === 0) return () => {};
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];
  
  const handleKeyDown = (event) => {
    if (event.key !== 'Tab') return;
    
    // Shift + Tab
    if (event.shiftKey) {
      if (document.activeElement === firstElement) {
        lastElement.focus();
        event.preventDefault();
      }
    } 
    // Tab
    else {
      if (document.activeElement === lastElement) {
        firstElement.focus();
        event.preventDefault();
      }
    }
  };
  
  document.addEventListener('keydown', handleKeyDown);
  
  // Focus the first element initially
  if (focusableElements.length > 0 && !container.contains(document.activeElement)) {
    firstElement.focus();
  }
  
  // Return cleanup function
  return () => {
    document.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Announce a message to screen readers
 * 
 * @param {string} message - Message to announce
 * @param {string} [ariaLive='polite'] - ARIA live value ('polite' or 'assertive')
 */
export function announceToScreenReader(message, ariaLive = 'polite') {
  if (!message) return;
  
  // Create or get the announcement element
  let announcementElement = document.getElementById('screen-reader-announcement');
  
  if (!announcementElement) {
    announcementElement = document.createElement('div');
    announcementElement.id = 'screen-reader-announcement';
    announcementElement.className = 'sr-only';
    announcementElement.setAttribute('aria-live', ariaLive);
    announcementElement.setAttribute('aria-atomic', 'true');
    document.body.appendChild(announcementElement);
  }
  
  // Set the message
  announcementElement.textContent = message;
  
  // Clear the message after a delay
  setTimeout(() => {
    announcementElement.textContent = '';
  }, 3000);
}

/**
 * Check if reduced motion is preferred
 * 
 * @returns {boolean} - Whether reduced motion is preferred
 */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Check if high contrast mode is active
 * 
 * @returns {boolean} - Whether high contrast mode is active
 */
export function prefersHighContrast() {
  return window.matchMedia('(prefers-contrast: more)').matches;
}