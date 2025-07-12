import { useState, useRef, useCallback, useEffect } from 'react';
import { useDeepMemo } from './use-deep-memo';

/**
 * Hook for virtualizing large lists to improve performance
 * 
 * This hook implements a simple virtualization technique that only renders
 * the items that are visible in the viewport, plus a buffer of items above
 * and below to ensure smooth scrolling.
 * 
 * @param {Object} options - Options
 * @param {Array} options.items - Array of items to render
 * @param {number} options.itemHeight - Height of each item in pixels
 * @param {number} [options.overscan=3] - Number of items to render above and below the visible area
 * @param {number} [options.scrollingDelay=150] - Delay in ms to wait after scrolling stops before recalculating
 * @returns {Object} - Virtualization helpers
 */
export function useVirtualizedList({
  items,
  itemHeight,
  overscan = 3,
  scrollingDelay = 150
}) {
  // Reference to the container element
  const containerRef = useRef(null);
  
  // Store scroll position
  const [scrollTop, setScrollTop] = useState(0);
  
  // Store container height
  const [containerHeight, setContainerHeight] = useState(0);
  
  // Track if we're currently scrolling
  const isScrolling = useRef(false);
  
  // Store timeout ID for scroll end detection
  const scrollTimeoutId = useRef(null);
  
  // Calculate the total height of all items
  const totalHeight = items.length * itemHeight;
  
  // Calculate which items should be visible
  const visibleItems = useDeepMemo(() => {
    if (containerHeight === 0) return [];
    
    // Calculate visible range
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    // Create array of visible items with their positions
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
      style: {
        position: 'absolute',
        top: (startIndex + index) * itemHeight,
        height: itemHeight,
        left: 0,
        right: 0
      }
    }));
  }, [items, scrollTop, containerHeight, itemHeight, overscan]);
  
  // Handle scroll events
  const handleScroll = useCallback((event) => {
    const { scrollTop } = event.currentTarget;
    
    // Update scroll position
    setScrollTop(scrollTop);
    
    // Mark as scrolling
    isScrolling.current = true;
    
    // Clear previous timeout
    if (scrollTimeoutId.current !== null) {
      clearTimeout(scrollTimeoutId.current);
    }
    
    // Set timeout to detect when scrolling stops
    scrollTimeoutId.current = setTimeout(() => {
      isScrolling.current = false;
    }, scrollingDelay);
  }, [scrollingDelay]);
  
  // Measure container on mount and resize
  useEffect(() => {
    if (!containerRef.current) return;
    
    // Create resize observer
    const resizeObserver = new ResizeObserver((entries) => {
      const { height } = entries[0].contentRect;
      setContainerHeight(height);
    });
    
    // Observe container
    resizeObserver.observe(containerRef.current);
    
    // Initial measurement
    setContainerHeight(containerRef.current.clientHeight);
    
    // Cleanup
    return () => {
      resizeObserver.disconnect();
      
      if (scrollTimeoutId.current !== null) {
        clearTimeout(scrollTimeoutId.current);
      }
    };
  }, []);
  
  // Scroll to a specific item
  const scrollToItem = useCallback((index, options = {}) => {
    const { align = 'auto', behavior = 'auto' } = options;
    
    if (!containerRef.current) return;
    
    const itemTop = index * itemHeight;
    const itemBottom = itemTop + itemHeight;
    
    const containerTop = containerRef.current.scrollTop;
    const containerBottom = containerTop + containerRef.current.clientHeight;
    
    let targetScrollTop = containerTop;
    
    if (align === 'start' || (align === 'auto' && itemTop < containerTop)) {
      targetScrollTop = itemTop;
    } else if (align === 'end' || (align === 'auto' && itemBottom > containerBottom)) {
      targetScrollTop = itemBottom - containerRef.current.clientHeight;
    } else if (align === 'center') {
      targetScrollTop = itemTop - (containerRef.current.clientHeight - itemHeight) / 2;
    }
    
    containerRef.current.scrollTo({
      top: targetScrollTop,
      behavior
    });
  }, [itemHeight]);
  
  return {
    containerProps: {
      ref: containerRef,
      onScroll: handleScroll,
      style: {
        position: 'relative',
        height: '100%',
        overflow: 'auto'
      }
    },
    totalHeight,
    visibleItems,
    isScrolling: isScrolling.current,
    scrollToItem
  };
}