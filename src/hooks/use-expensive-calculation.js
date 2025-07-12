import { useRef, useEffect } from 'react';
import { useDeepMemo } from './use-deep-memo';
import { startMeasure, endMeasure } from '@/utils/performance';

/**
 * Hook for optimizing expensive calculations with performance tracking
 * 
 * @param {Function} calculationFn - Function that performs the expensive calculation
 * @param {Array} dependencies - Dependencies array for the calculation
 * @param {Object} [options] - Options
 * @param {string} [options.name='expensiveCalculation'] - Name for performance tracking
 * @param {boolean} [options.trackPerformance=true] - Whether to track performance
 * @param {Object} [options.initialValue=null] - Initial value to use before calculation
 * @returns {any} - Result of the calculation
 */
export function useExpensiveCalculation(
  calculationFn,
  dependencies,
  {
    name = 'expensiveCalculation',
    trackPerformance = true,
    initialValue = null
  } = {}
) {
  // Store the calculation name
  const calculationName = useRef(`${name}_calculation`);
  
  // Use deep memo to avoid recalculating when dependencies are equivalent
  const result = useDeepMemo(() => {
    // Start performance measurement
    if (trackPerformance) {
      startMeasure(calculationName.current);
    }
    
    // Perform the calculation
    const calculationResult = calculationFn();
    
    // End performance measurement
    if (trackPerformance) {
      endMeasure(calculationName.current, {
        category: 'calculation',
        metadata: { dependencies: dependencies.map(dep => typeof dep) }
      });
    }
    
    return calculationResult;
  }, dependencies);
  
  // Return the result or initial value
  return result === undefined ? initialValue : result;
}