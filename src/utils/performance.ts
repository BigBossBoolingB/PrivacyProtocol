/**
 * TypeScript Performance monitoring utility
 * Simplified version with Core Web Vitals tracking
 */

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  isGood: boolean;
}

interface PerformanceThresholds {
  LCP: number;
  FID: number;
  CLS: number;
  TTFB: number;
  FCP: number;
}

class PerformanceTracker {
  private metrics = new Map<string, PerformanceMetric[]>();
  private observers = new Map<string, PerformanceObserver>();
  private readonly thresholds: PerformanceThresholds = {
    LCP: 2500,
    FID: 100,
    CLS: 0.1,
    TTFB: 800,
    FCP: 1800
  };
  private isInitialized = false;

  init(): void {
    if (this.isInitialized || typeof window === 'undefined') return;
    
    try {
      this.initCoreWebVitals();
      this.initNavigationTiming();
      this.isInitialized = true;
    } catch (error) {
      console.warn('Performance monitoring initialization failed:', error);
    }
  }

  private initCoreWebVitals(): void {
    if (!('PerformanceObserver' in window)) return;

    this.observeMetric('largest-contentful-paint', (entries) => {
      const lastEntry = entries[entries.length - 1];
      this.recordMetric('LCP', lastEntry.startTime);
    });

    this.observeMetric('first-input', (entries) => {
      entries.forEach(entry => {
        const firstInputEntry = entry as PerformanceEntry & { processingStart?: number };
        if (firstInputEntry.processingStart) {
          this.recordMetric('FID', firstInputEntry.processingStart - entry.startTime);
        }
      });
    });

    this.observeLayoutShift();
  }

  private observeMetric(type: string, callback: (entries: PerformanceEntry[]) => void): void {
    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries());
      });
      observer.observe({ entryTypes: [type] });
      this.observers.set(type, observer);
    } catch (error) {
      console.warn(`Failed to observe ${type}:`, error);
    }
  }

  private observeLayoutShift(): void {
    let clsValue = 0;
    
    this.observeMetric('layout-shift', (entries) => {
      entries.forEach(entry => {
        const layoutShiftEntry = entry as PerformanceEntry & { hadRecentInput?: boolean; value?: number };
        if (!layoutShiftEntry.hadRecentInput && layoutShiftEntry.value) {
          clsValue += layoutShiftEntry.value;
        }
      });
      this.recordMetric('CLS', clsValue);
    });
  }

  private initNavigationTiming(): void {
    if (typeof window === 'undefined') return;

    window.addEventListener('load', () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        this.recordMetric('TTFB', navigation.responseStart - navigation.requestStart);
        this.recordMetric('DOM_LOAD', navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart);
        this.recordMetric('WINDOW_LOAD', navigation.loadEventEnd - navigation.loadEventStart);
      }
    });
  }

  private recordMetric(name: string, value: number): void {
    const metric: PerformanceMetric = {
      name,
      value: Math.round(value * 100) / 100,
      timestamp: Date.now(),
      isGood: this.isMetricGood(name, value)
    };

    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }
    
    this.metrics.get(name)!.push(metric);

    if (!metric.isGood) {
      this.reportPoorMetric(metric);
    }
  }

  private isMetricGood(name: string, value: number): boolean {
    const threshold = this.thresholds[name as keyof PerformanceThresholds];
    return threshold ? value <= threshold : true;
  }

  private reportPoorMetric(metric: PerformanceMetric): void {
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', 'poor_performance', {
        metric_name: metric.name,
        metric_value: metric.value
      });
    }
  }

  getMetrics(name?: string): PerformanceMetric[] | Record<string, PerformanceMetric[]> {
    return name ? this.metrics.get(name) || [] : Object.fromEntries(this.metrics);
  }

  getLatestMetric(name: string): PerformanceMetric | null {
    const metrics = this.getMetrics(name) as PerformanceMetric[];
    return metrics.length > 0 ? metrics[metrics.length - 1] : null;
  }

  disconnect(): void {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.isInitialized = false;
  }
}

const performanceTracker = new PerformanceTracker();

export const initPerformanceMonitoring = (): PerformanceTracker => {
  performanceTracker.init();
  
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      performanceTracker.disconnect();
    });
  }

  return performanceTracker;
};

export { performanceTracker };
export default performanceTracker;
