/**
 * Hooks index file
 * 
 * This file exports all custom hooks for easy importing
 */

// API and data fetching hooks
export { useApiQuery, useApiMutation } from './use-api-query';
export { useDebounce } from './use-debounce';
export { useLocalStorage } from './use-local-storage';
export { useErrorHandler } from './use-error-handler';
export { useFormWithValidation } from './use-form-with-validation';
export { useMobile } from './use-mobile';

// Performance optimization hooks
export { useDeepMemo } from './use-deep-memo';
export { useMemoizedCallback } from './use-memoized-callback';
export { useExpensiveCalculation } from './use-expensive-calculation';
export { useEventCallback } from './use-event-callback';
export { useBatchedState } from './use-batched-state';
export { useVirtualizedList } from './use-virtualized-list';
export { usePerformanceTracking } from './use-performance-tracking';