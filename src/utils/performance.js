/**
 * Simplified performance monitoring utility
 * Focuses on Core Web Vitals and essential metrics
 */

const performanceMetrics = {
  measures: [],
  interactions: [],
  renders: {},
  resources: [],
  maxMeasures: 100
};

const config = {
  enabled: true,
  logThreshold: 100,
  samplingRate: 1.0,
  maxMeasures: 100
};

/**
 * Initialize performance monitoring
 */
export function initPerformanceMonitoring(options = {}) {
  Object.assign(config, options);
  
  if (!config.enabled || typeof window === 'undefined' || typeof performance === 'undefined') {
    return;
  }
  
  if (window.PerformanceObserver) {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach(entry => {
          if (entry.entryType === 'resource' && entry.duration > config.logThreshold) {
            console.warn(`[Performance] Slow resource: ${entry.name} (${entry.duration.toFixed(2)}ms)`);
          }
        });
      });
      
      observer.observe({ entryTypes: ['resource'] });
    } catch (error) {
      console.warn('Performance observer setup failed:', error);
    }
  }
}

const performanceMarks = {};

/**
 * Start measuring performance for a specific operation
 */
export function startMeasure(name) {
  if (!config.enabled || typeof performance === 'undefined') return;
  
  const markName = `${name}_start`;
  performance.mark(markName);
  performanceMarks[name] = { markName, startTime: performance.now() };
}

/**
 * End measuring performance for a specific operation
 */
export function endMeasure(name, options = {}) {
  if (!config.enabled || typeof performance === 'undefined' || !performanceMarks[name]) return null;
  
  const { category = 'general', metadata = {} } = options;
  const { markName: startMark } = performanceMarks[name];
  const endMark = `${name}_end`;
  
  performance.mark(endMark);
  
  try {
    performance.measure(name, startMark, endMark);
    const entries = performance.getEntriesByName(name);
    const duration = entries[entries.length - 1].duration;
    
    const measure = { name, duration, category, timestamp: Date.now(), metadata };
    performanceMetrics.measures.push(measure);
    
    if (performanceMetrics.measures.length > config.maxMeasures) {
      performanceMetrics.measures.shift();
    }
    
    if (duration > config.logThreshold) {
      console.warn(`[Performance] ${name} took ${duration.toFixed(2)}ms`);
    }
    
    performance.clearMarks(startMark);
    performance.clearMarks(endMark);
    performance.clearMeasures(name);
    delete performanceMarks[name];
    
    return duration;
  } catch (error) {
    console.error('[Performance] Error measuring performance:', error);
    return null;
  }
}

/**
 * Track component render time
 */
export function trackRender(componentName, duration, props = {}) {
  if (!config.enabled) return;
  
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
  metrics.count++;
  metrics.totalDuration += duration;
  metrics.min = Math.min(metrics.min, duration);
  metrics.max = Math.max(metrics.max, duration);
  
  metrics.recent.push({
    duration,
    timestamp: Date.now(),
    props: Object.keys(props)
  });
  
  if (metrics.recent.length > 10) {
    metrics.recent.shift();
  }
  
  if (duration > config.logThreshold) {
    console.warn(`[Performance] Slow render: ${componentName} (${duration.toFixed(2)}ms)`);
  }
}

/**
 * Measure the performance of a function
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
 * Get performance metrics
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

initPerformanceMonitoring();
