import React from 'react';
import ErrorBoundary from './ErrorBoundary';

class AsyncErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasAsyncError: false, 
      asyncError: null 
    };
  }

  componentDidMount() {
    window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  componentWillUnmount() {
    window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
  }

  handleUnhandledRejection = (event) => {
    if (this.props.catchAsync) {
      this.setState({
        hasAsyncError: true,
        asyncError: event.reason
      });
      event.preventDefault();
    }
  };

  handleAsyncRetry = () => {
    this.setState({
      hasAsyncError: false,
      asyncError: null
    });
  };

  render() {
    if (this.state.hasAsyncError) {
      const AsyncErrorFallback = ({ error, retry }) => (
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <h3 className="text-lg font-medium text-red-800 mb-2">
            Async Operation Failed
          </h3>
          <p className="text-sm text-red-600 mb-4">
            An asynchronous operation failed: {error?.message || 'Unknown error'}
          </p>
          <button
            onClick={retry}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      );

      return (
        <AsyncErrorFallback 
          error={this.state.asyncError} 
          retry={this.handleAsyncRetry}
        />
      );
    }

    return (
      <ErrorBoundary {...this.props}>
        {this.props.children}
      </ErrorBoundary>
    );
  }
}

export default AsyncErrorBoundary;
