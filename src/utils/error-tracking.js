/**
 * Error tracking utility
 * 
 * This module provides error tracking functionality that can be integrated with
 * services like Sentry, LogRocket, or a custom solution.
 */
import React from 'react';

// Configuration
const config = {
  environment: 'development',
  release: '0.1.0',
  sampleRate: 1.0, // Capture 100% of errors by default
  maxBreadcrumbs: 100,
  ignoreErrors: [
    // Common errors to ignore
    'ResizeObserver loop limit exceeded',
    'Network request failed',
    /^Script error\.?$/,
    /^ResizeObserver loop completed with undelivered notifications\.?$/
  ]
};

// Track whether error tracking is initialized
let isInitialized = false;

// User context
let userContext = {};

// Session information
let sessionContext = {
  id: generateSessionId(),
  startedAt: new Date().toISOString(),
  lastActivity: new Date().toISOString()
};

// Breadcrumbs for tracking user actions
const breadcrumbs = [];

/**
 * Generate a unique session ID
 * 
 * @returns {string} - Session ID
 */
function generateSessionId() {
  return 'session_' + Math.random().toString(36).substring(2, 15);
}

/**
 * Initialize error tracking
 * 
 * @param {Object} options - Initialization options
 * @param {string} [options.environment='development'] - Environment name
 * @param {string} [options.release] - Release version
 * @param {Object} [options.user] - User information
 * @param {number} [options.sampleRate] - Error sampling rate (0.0 to 1.0)
 * @param {Array<string|RegExp>} [options.ignoreErrors] - Patterns of errors to ignore
 * @returns {Promise<void>}
 */
export async function initErrorTracking(options = {}) {
  if (isInitialized) return;
  
  try {
    // Update configuration
    Object.assign(config, options);
    
    // Set up global error handlers
    setupGlobalHandlers();
    
    // Set user context
    if (options.user) {
      setUserContext(options.user);
    }
    
    // Log initialization in development
    if (process.env.NODE_ENV !== 'production') {
      console.log('[ErrorTracking] Initialized', config);
    }
    
    isInitialized = true;
  } catch (error) {
    console.error('[ErrorTracking] Failed to initialize:', error);
  }
}

/**
 * Set up global error handlers
 */
function setupGlobalHandlers() {
  // Handle unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    captureException(event.reason, { 
      mechanism: 'unhandledrejection',
      handled: false
    });
  });
  
  // Handle uncaught exceptions
  window.addEventListener('error', (event) => {
    // Skip if the error should be ignored
    if (shouldIgnoreError(event.error || event.message)) {
      return;
    }
    
    captureException(event.error || new Error(event.message), {
      mechanism: 'uncaughtexception',
      handled: false,
      url: event.filename,
      line: event.lineno,
      column: event.colno
    });
  });
  
  // Track page visibility changes
  document.addEventListener('visibilitychange', () => {
    addBreadcrumb({
      category: 'ui.visibility',
      message: `Page ${document.visibilityState}`,
      level: 'info'
    });
  });
}

/**
 * Check if an error should be ignored
 * 
 * @param {Error|string} error - The error to check
 * @returns {boolean} - Whether the error should be ignored
 */
function shouldIgnoreError(error) {
  const errorMessage = error instanceof Error ? error.message : String(error);
  
  return config.ignoreErrors.some(pattern => {
    if (pattern instanceof RegExp) {
      return pattern.test(errorMessage);
    }
    return errorMessage.includes(pattern);
  });
}

/**
 * Set user context for error tracking
 * 
 * @param {Object} user - User information
 * @param {string} [user.id] - User ID
 * @param {string} [user.email] - User email
 * @param {string} [user.username] - Username
 */
export function setUserContext(user) {
  userContext = { ...userContext, ...user };
  
  addBreadcrumb({
    category: 'auth',
    message: 'User context updated',
    level: 'info'
  });
  
  if (process.env.NODE_ENV !== 'production') {
    console.log('[ErrorTracking] User context set:', userContext);
  }
}

/**
 * Add a breadcrumb to track user actions
 * 
 * @param {Object} breadcrumb - Breadcrumb information
 * @param {string} breadcrumb.category - Breadcrumb category
 * @param {string} breadcrumb.message - Breadcrumb message
 * @param {string} [breadcrumb.level='info'] - Log level
 * @param {Object} [breadcrumb.data] - Additional data
 */
export function addBreadcrumb(breadcrumb) {
  if (!isInitialized) return;
  
  // Update session last activity
  sessionContext.lastActivity = new Date().toISOString();
  
  // Add breadcrumb with timestamp
  breadcrumbs.push({
    timestamp: new Date().toISOString(),
    ...breadcrumb
  });
  
  // Limit breadcrumbs array size
  if (breadcrumbs.length > config.maxBreadcrumbs) {
    breadcrumbs.shift();
  }
}

/**
 * Capture an exception
 * 
 * @param {Error} error - The error to capture
 * @param {Object} [context] - Additional context
 */
export function captureException(error, context = {}) {
  if (!isInitialized) {
    console.warn('[ErrorTracking] Not initialized');
    console.error(error);
    return;
  }
  
  // Skip if the error should be ignored
  if (shouldIgnoreError(error)) {
    return;
  }
  
  // Apply sampling
  if (Math.random() > config.sampleRate) {
    return;
  }
  
  // Prepare error report
  const errorReport = {
    error,
    message: error.message,
    name: error.name,
    stack: error.stack,
    timestamp: new Date().toISOString(),
    context: { ...context },
    user: { ...userContext },
    session: { ...sessionContext },
    breadcrumbs: [...breadcrumbs],
    environment: config.environment,
    release: config.release
  };
  
  // In production, this would send to an error tracking service
  // For now, log to console in development
  if (process.env.NODE_ENV !== 'production') {
    console.error('[ErrorTracking] Exception captured:', errorReport);
  } else {
    // In production, we would send to a service
    // sendErrorToService(errorReport);
    console.error('[ErrorTracking]', error.message);
  }
}

/**
 * Capture a message
 * 
 * @param {string} message - The message to capture
 * @param {Object} [context] - Additional context
 * @param {string} [level='info'] - Log level
 */
export function captureMessage(message, context = {}, level = 'info') {
  if (!isInitialized) {
    console.warn('[ErrorTracking] Not initialized');
    return;
  }
  
  // Add as breadcrumb
  addBreadcrumb({
    category: 'log',
    message,
    level,
    data: context
  });
  
  // For warning and error levels, create a more detailed report
  if (level === 'warning' || level === 'error') {
    const messageReport = {
      message,
      level,
      timestamp: new Date().toISOString(),
      context: { ...context },
      user: { ...userContext },
      session: { ...sessionContext },
      breadcrumbs: [...breadcrumbs],
      environment: config.environment,
      release: config.release
    };
    
    if (process.env.NODE_ENV !== 'production') {
      console[level]('[ErrorTracking] Message captured:', messageReport);
    } else {
      // In production, we would send to a service for warnings and errors
      // sendMessageToService(messageReport);
      console[level]('[ErrorTracking]', message);
    }
  }
}

/**
 * Reset error tracking (e.g., on logout)
 */
export function resetErrorTracking() {
  userContext = {};
  sessionContext = {
    id: generateSessionId(),
    startedAt: new Date().toISOString(),
    lastActivity: new Date().toISOString()
  };
  breadcrumbs.length = 0;
  
  addBreadcrumb({
    category: 'session',
    message: 'Session reset',
    level: 'info'
  });
  
  if (process.env.NODE_ENV !== 'production') {
    console.log('[ErrorTracking] Reset');
  }
}

/**
 * Create an error boundary component
 * 
 * @param {Function} fallback - Fallback component to render on error
 * @returns {React.Component} - Error boundary component
 */
export function createErrorBoundary(fallback) {
  return class ErrorBoundary extends React.Component {
    constructor(props) {
      super(props);
      this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
      return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
      captureException(error, { 
        errorInfo,
        componentStack: errorInfo.componentStack,
        boundary: true
      });
    }

    render() {
      if (this.state.hasError) {
        return fallback(this.state.error);
      }

      return this.props.children;
    }
  };
}