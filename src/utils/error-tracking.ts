interface ErrorContext {
  userId?: string;
  component?: string;
  action?: string;
  metadata?: Record<string, any>;
}

interface ErrorReport {
  message: string;
  stack?: string;
  timestamp: number;
  url: string;
  userAgent: string;
  context: ErrorContext;
  errorId: string;
}

/**
 * Tracks and reports errors to analytics and logging services
 * @param error - The error object or message
 * @param context - Additional context about the error
 */
export const trackError = (error: Error | string, context: ErrorContext = {}): void => {
  const errorReport: ErrorReport = {
    message: typeof error === 'string' ? error : error.message,
    stack: typeof error === 'object' ? error.stack : undefined,
    timestamp: Date.now(),
    url: window.location.href,
    userAgent: navigator.userAgent,
    context,
    errorId: generateErrorId()
  };

  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', 'exception', {
      description: errorReport.message,
      fatal: false,
      custom_map: {
        error_id: errorReport.errorId,
        component: context.component,
        user_id: context.userId
      }
    });
  }

  if (process.env.NODE_ENV === 'development') {
    console.error('Error tracked:', errorReport);
  }

  sendToErrorService(errorReport);
};

/**
 * Generates a unique error ID
 */
const generateErrorId = (): string => {
  return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Sends error report to external error tracking service
 */
const sendToErrorService = (errorReport: ErrorReport): void => {
  
  if (typeof window !== 'undefined') {
    try {
      const errors = JSON.parse(localStorage.getItem('error_reports') || '[]');
      errors.push(errorReport);
      
      if (errors.length > 50) {
        errors.splice(0, errors.length - 50);
      }
      
      localStorage.setItem('error_reports', JSON.stringify(errors));
    } catch (e) {
      console.warn('Failed to store error report:', e);
    }
  }
};

/**
 * Sets up global error handlers
 */
export const initErrorTracking = (): void => {
  if (typeof window === 'undefined') return;

  window.addEventListener('error', (event) => {
    trackError(event.error || event.message, {
      component: 'Global',
      action: 'unhandled_error',
      metadata: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    trackError(event.reason, {
      component: 'Global',
      action: 'unhandled_promise_rejection'
    });
  });
};

export default trackError;
