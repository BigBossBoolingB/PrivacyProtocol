import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './button';
import { captureException } from '@/utils/error-tracking';

/**
 * Error Boundary component to catch and display errors in the UI
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error to an error reporting service
    captureException(error, { errorInfo });
    this.setState({ errorInfo });
    console.error('Error caught by ErrorBoundary:', error, errorInfo);
  }

  resetErrorBoundary = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
    
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    const { hasError, error } = this.state;
    const { fallback, children } = this.props;
    
    if (hasError) {
      // Custom fallback UI
      if (fallback) {
        return typeof fallback === 'function'
          ? fallback({ error, resetErrorBoundary: this.resetErrorBoundary })
          : fallback;
      }
      
      // Default fallback UI
      return (
        <div className="p-6 rounded-lg bg-red-500/10 border border-red-500/30 text-center">
          <div className="flex justify-center mb-4">
            <AlertTriangle className="h-12 w-12 text-red-500" />
          </div>
          <h3 className="text-xl font-semibold text-red-500 mb-2">
            Something went wrong
          </h3>
          <p className="text-gray-400 mb-4">
            {error?.message || 'An unexpected error occurred'}
          </p>
          <Button 
            onClick={this.resetErrorBoundary}
            variant="outline"
            className="border-red-500/50 text-red-400 hover:bg-red-500/10"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Try again
          </Button>
        </div>
      );
    }

    return children;
  }
}

export { ErrorBoundary };