/**
 * Performance monitoring utility
 * 
 * This utility provides functions for measuring and tracking performance metrics
 * including component rendering, function execution, and resource loading.
 */

// Store for performance marks and measures
const performanceMarks = {};

// Store for performance metrics
const performanceMetrics = {
  measures: [],
  interactions: [],
  renders: {},
  resources: [],
  maxMeasures: 100
};

// Configuration
const config = {
  enabled: true,
  logLevel: 'warn', // 'debug', 'info', 'warn', 'error', 'none'
  logThreshold: 100, // Log warnings for operations taking longer than this (ms)
  samplingRate: 1.0, // Capture all measures by default
  maxMeasures: 100, // Maximum number of measures to store
  autoTrackResources: true, // Track resource loading automatically
  autoTrackLongTasks: true // Track long tasks automatically
};

/**
 * Initialize performance monitoring
 * 
 * @param {Object} options - Configuration options
 * @param {boolean} [options.enabled=true] - Whether performance monitoring is enabled
 * @param {string} [options.logLevel='warn'] - Log level ('debug', 'info', 'warn', 'error', 'none')
 * @param {number} [options.logThreshold=100] - Log warnings for operations taking longer than this (ms)
 * @param {number} [options.samplingRate=1.0] - Sampling rate for performance measures (0.0 to 1.0)
 * @param {number} [options.maxMeasures=100] - Maximum number of measures to store
 * @param {boolean} [options.autoTrackResources=true] - Track resource loading automatically
 * @param {boolean} [options.autoTrackLongTasks=true] - Track long tasks automatically
 */
export function initPerformanceMonitoring(options = {}) {
  // Update configuration
  Object.assign(config, options);
  
  // Skip if disabled or not in browser
  if (!config.enabled || typeof window === 'undefined' || typeof performance === 'undefined') {
    return;
  }
  
  // Set up resource timing observer if enabled
  if (config.autoTrackResources && window.PerformanceObserver) {
    try {
      const resourceObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        
        for (const entry of entries) {
          if (entry.entryType === 'resource') {
            trackResourceTiming(entry);
          }
        }
      });
      
      resourceObserver.observe({ entryTypes: ['resource'] });
    } catch (error) {
      console.error('Failed to observe resource timing:', error);
    }
  }
  
  // Set up long task observer if enabled
  if (config.autoTrackLongTasks && window.PerformanceObserver) {
    try {
      const longTaskObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        
        for (const entry of entries) {
          if (entry.entryType === 'longtask') {
            trackLongTask(entry);
          }
        }
      });
      
      longTaskObserver.observe({ entryTypes: ['longtask'] });
    } catch (error) {
      // Long task observation might not be supported in all browsers
      if (config.logLevel !== 'none' && config.logLevel !== 'error') {
        console.warn('Long task observation not supported');
      }
    }
  }
  
  // Log initialization
  if (config.logLevel === 'debug' || config.logLevel === 'info') {
    console.log('[Performance] Monitoring initialized', config);
  }
}

/**
 * Track resource timing
 * 
 * @param {PerformanceResourceTiming} entry - Resource timing entry
 */
function trackResourceTiming(entry) {
  // Apply sampling
  if (Math.random() > config.samplingRate) {
    return;
  }
  
  const resource = {
    name: entry.name,
    type: entry.initiatorType,
    startTime: entry.startTime,
    duration: entry.duration,
    size: entry.transferSize || 0,
    timestamp: Date.now()
  };
  
  // Add to metrics
  performanceMetrics.resources.push(resource);
  
  // Trim if needed
  if (performanceMetrics.resources.length > config.maxMeasures) {
    performanceMetrics.resources.shift();
  }
  
  // Log slow resources
  if (entry.duration > config.logThreshold && shouldLog('warn')) {
    console.warn(`[Performance] Slow resource load: ${entry.name} (${entry.duration.toFixed(2)}ms)`);
  }
}

/**
 * Track long task
 * 
 * @param {PerformanceLongTaskTiming} entry - Long task timing entry
 */
function trackLongTask(entry) {
  // Apply sampling
  if (Math.random() > config.samplingRate) {
    return;
  }
  
  const task = {
    duration: entry.duration,
    startTime: entry.startTime,
    timestamp: Date.now()
  };
  
  // Log long tasks
  if (shouldLog('warn')) {
    console.warn(`[Performance] Long task detected: ${entry.duration.toFixed(2)}ms`);
  }
  
  // We could store these for analysis, but they can be numerous
  // For now, we just log them
}

/**
 * Check if we should log at the specified level
 * 
 * @param {string} level - Log level
 * @returns {boolean} - Whether to log
 */
function shouldLog(level) {
  const levels = { debug: 0, info: 1, warn: 2, error: 3, none: 4 };
  return levels[level] >= levels[config.logLevel];
}

/**
 * Start measuring performance for a specific operation
 * 
 * @param {string} name - Name of the operation
 * @returns {void}
 */
export function startMeasure(name) {
  if (!config.enabled || typeof performance === 'undefined') return;
  
  // Apply sampling
  if (Math.random() > config.samplingRate) {
    return;
  }
  
  const markName = `${name}_start`;
  performance.mark(markName);
  performanceMarks[name] = {
    markName,
    startTime: performance.now()
  };
}

/**
 * End measuring performance for a specific operation
 * 
 * @param {string} name - Name of the operation
 * @param {Object} [options] - Options
 * @param {boolean} [options.log] - Whether to log the result
 * @param {string} [options.category] - Category of the operation
 * @param {Object} [options.metadata] - Additional metadata
 * @returns {number|null} - Duration in milliseconds
 */
export function endMeasure(name, options = {}) {
  if (!config.enabled || typeof performance === 'undefined' || !performanceMarks[name]) return null;
  
  const { log = shouldLog('info'), category = 'general', metadata = {} } = options;
  
  const { markName: startMark, startTime } = performanceMarks[name];
  const endMark = `${name}_end`;
  
  performance.mark(endMark);
  
  try {
    performance.measure(name, startMark, endMark);
    
    const entries = performance.getEntriesByName(name);
    const duration = entries[entries.length - 1].duration;
    
    // Store the measurement
    const measure = {
      name,
      duration,
      category,
      timestamp: Date.now(),
      metadata
    };
    
    performanceMetrics.measures.push(measure);
    
    // Trim if needed
    if (performanceMetrics.measures.length > config.maxMeasures) {
      performanceMetrics.measures.shift();
    }
    
    // Log if requested or if duration exceeds threshold
    if (log || (duration > config.logThreshold && shouldLog('warn'))) {
      const logMethod = duration > config.logThreshold ? 'warn' : 'log';
      const logLevel = duration > config.logThreshold ? 'warn' : 'info';
      
      if (shouldLog(logLevel)) {
        console[logMethod](`[Performance] ${name} took ${duration.toFixed(2)}ms`);
      }
    }
    
    // Clean up
    performance.clearMarks(startMark);
    performance.clearMarks(endMark);
    performance.clearMeasures(name);
    
    delete performanceMarks[name];
    
    return duration;
  } catch (error) {
    if (shouldLog('error')) {
      console.error('[Performance] Error measuring performance:', error);
    }
    return null;
  }
}

/**
 * Track component render time
 * 
 * @param {string} componentName - Name of the component
 * @param {number} duration - Render duration in milliseconds
 * @param {Object} [props] - Component props
 */
export function trackRender(componentName, duration, props = {}) {
  if (!config.enabled) return;
  
  // Apply sampling
  if (Math.random() > config.samplingRate) {
    return;
  }
  
  // Initialize component metrics if needed
  if (!performanceMetrics.renders[componentName]) {
    performanceMetrics.renders[componentName] = {
      count: 0,
      totalDuration: 0,
      min: Infinity,
      max: 0,
      recent: []
    };
  }
  
  const metrics = performanceMetrics.renders[componentName];
  
  // Update metrics
  metrics.count++;
  metrics.totalDuration += duration;
  metrics.min = Math.min(metrics.min, duration);
  metrics.max = Math.max(metrics.max, duration);
  
  // Store recent render
  metrics.recent.push({
    duration,
    timestamp: Date.now(),
    props: Object.keys(props)
  });
  
  // Trim recent renders
  if (metrics.recent.length > 10) {
    metrics.recent.shift();
  }
  
  // Log slow renders
  if (duration > config.logThreshold && shouldLog('warn')) {
    console.warn(`[Performance] Slow render: ${componentName} (${duration.toFixed(2)}ms)`);
  }
}

/**
 * Create a higher-order component that tracks render performance
 * 
 * @param {React.Component} Component - The component to wrap
 * @param {string} [name] - Optional name override
 * @returns {React.Component} - Wrapped component
 */
export function withRenderTracking(Component, name) {
  const componentName = name || Component.displayName || Component.name || 'UnknownComponent';
  
  // Return a new component that tracks rendering
  const WrappedComponent = (props) => {
    const startTime = performance.now();
    const result = Component(props);
    const duration = performance.now() - startTime;
    
    // Track the render
    trackRender(componentName, duration, props);
    
    return result;
  };
  
  WrappedComponent.displayName = `WithRenderTracking(${componentName})`;
  
  return WrappedComponent;
}

/**
 * Measure the performance of a function
 * 
 * @param {Function} fn - The function to measure
 * @param {string} name - Name of the operation
 * @param {Object} [options] - Options
 * @param {boolean} [options.log] - Whether to log the result
 * @param {string} [options.category] - Category of the operation
 * @param {Object} [options.metadata] - Additional metadata
 * @returns {any} - The result of the function
 */
export function measureFunction(fn, name, options = {}) {
  if (!config.enabled) return fn();
  
  startMeasure(name);
  
  try {
    const result = fn();
    endMeasure(name, options);
    return result;
  } catch (error) {
    endMeasure(name, options);
    throw error;
  }
}

/**
 * Measure the performance of an async function
 * 
 * @param {Function} fn - The async function to measure
 * @param {string} name - Name of the operation
 * @param {Object} [options] - Options
 * @param {boolean} [options.log] - Whether to log the result
 * @param {string} [options.category] - Category of the operation
 * @param {Object} [options.metadata] - Additional metadata
 * @returns {Promise<any>} - The result of the async function
 */
export async function measureAsyncFunction(fn, name, options = {}) {
  if (!config.enabled) return fn();
  
  startMeasure(name);
  
  try {
    const result = await fn();
    endMeasure(name, options);
    return result;
  } catch (error) {
    endMeasure(name, options);
    throw error;
  }
}

/**
 * Create a higher-order function that measures performance
 * 
 * @param {Function} fn - The function to wrap
 * @param {string} name - Name of the operation
 * @param {Object} [options] - Options
 * @param {boolean} [options.log] - Whether to log the result
 * @param {string} [options.category] - Category of the operation
 * @returns {Function} - Wrapped function
 */
export function withPerformanceTracking(fn, name, options = {}) {
  if (!config.enabled) return fn;
  
  const operationName = name || fn.name || 'anonymous';
  
  return function(...args) {
    // Add args to metadata
    const metadata = {
      ...options.metadata,
      args: args.map(arg => typeof arg)
    };
    
    const measureOptions = {
      ...options,
      metadata
    };
    
    if (fn.constructor && fn.constructor.name === 'AsyncFunction') {
      return measureAsyncFunction(() => fn(...args), operationName, measureOptions);
    } else {
      return measureFunction(() => fn(...args), operationName, measureOptions);
    }
  };
}

/**
 * Track user interaction
 * 
 * @param {string} action - The action performed
 * @param {Object} [details] - Additional details
 */
export function trackInteraction(action, details = {}) {
  if (!config.enabled) return;
  
  // Apply sampling
  if (Math.random() > config.samplingRate) {
    return;
  }
  
  const interaction = {
    action,
    timestamp: Date.now(),
    details
  };
  
  performanceMetrics.interactions.push(interaction);
  
  // Trim if needed
  if (performanceMetrics.interactions.length > config.maxMeasures) {
    performanceMetrics.interactions.shift();
  }
  
  if (shouldLog('debug')) {
    console.log(`[Performance] Interaction tracked: ${action}`);
  }
}

/**
 * Get performance metrics
 * 
 * @returns {Object} - Performance metrics
 */
export function getPerformanceMetrics() {
  return {
    ...performanceMetrics,
    timestamp: Date.now()
  };
}

/**
 * Clear performance metrics
 */
export function clearPerformanceMetrics() {
  performanceMetrics.measures = [];
  performanceMetrics.interactions = [];
  performanceMetrics.renders = {};
  performanceMetrics.resources = [];
}

// Initialize with default settings
initPerformanceMonitoring();