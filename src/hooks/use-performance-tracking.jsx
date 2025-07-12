import { useEffect, useRef } from 'react';
import { trackRender, startMeasure, endMeasure } from '@/utils/performance';

/**
 * Hook for tracking component render and lifecycle performance
 * 
 * @param {string} componentName - Name of the component
 * @param {Object} [options] - Options
 * @param {boolean} [options.trackMounts=true] - Track component mounts
 * @param {boolean} [options.trackUnmounts=true] - Track component unmounts
 * @param {boolean} [options.trackUpdates=true] - Track component updates
 * @param {boolean} [options.trackRenders=true] - Track component renders
 * @param {Object} [options.props] - Component props for context
 * @returns {Object} - Performance tracking methods
 */
export function usePerformanceTracking(
  componentName,
  {
    trackMounts = true,
    trackUnmounts = true,
    trackUpdates = true,
    trackRenders = true,
    props = {}
  } = {}
) {
  // Store render start time
  const renderStartTime = useRef(performance.now());
  
  // Store update count
  const updateCount = useRef(0);
  
  // Track mount and unmount
  useEffect(() => {
    if (trackMounts) {
      endMeasure(`${componentName}_mount`, {
        category: 'component',
        metadata: { props: Object.keys(props) }
      });
    }
    
    return () => {
      if (trackUnmounts) {
        startMeasure(`${componentName}_unmount`);
        // We can't measure the end since the component is unmounting
        // But we can at least mark the start for debugging
      }
    };
  }, []);
  
  // Track updates
  useEffect(() => {
    // Skip first render
    if (updateCount.current > 0 && trackUpdates) {
      endMeasure(`${componentName}_update`, {
        category: 'component',
        metadata: { 
          updateCount: updateCount.current,
          props: Object.keys(props)
        }
      });
    }
    
    updateCount.current++;
    
    if (trackUpdates) {
      startMeasure(`${componentName}_update`);
    }
  });
  
  // Track render time
  useEffect(() => {
    if (trackRenders) {
      const renderTime = performance.now() - renderStartTime.current;
      trackRender(componentName, renderTime, props);
    }
    
    // Reset for next render
    renderStartTime.current = performance.now();
  });
  
  // Return methods for manual tracking
  return {
    /**
     * Track a specific operation within the component
     * 
     * @param {string} operationName - Name of the operation
     */
    trackOperation: (operationName) => {
      startMeasure(`${componentName}_${operationName}`);
      
      return {
        /**
         * End tracking the operation
         * 
         * @param {Object} [metadata] - Additional metadata
         */
        end: (metadata = {}) => {
          endMeasure(`${componentName}_${operationName}`, {
            category: 'component_operation',
            metadata: {
              ...metadata,
              componentName
            }
          });
        }
      };
    }
  };
}