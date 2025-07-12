# Privacy Protocol Examples

> **Practical examples demonstrating how to use the Privacy Protocol React application and integrate with the Base44 API**

## Table of Contents

- [Basic Usage Examples](#basic-usage-examples)
- [Component Integration Examples](#component-integration-examples)
- [API Integration Examples](#api-integration-examples)
- [Advanced Workflows](#advanced-workflows)
- [Running Examples](#running-examples)

## Basic Usage Examples

### 1. Simple Policy Analysis (`basic-usage.jsx`)

Demonstrates the fundamental workflow of analyzing a privacy policy using the Base44 API:

- Text input for policy content and company name
- Integration with `riskScoreCalculator` API function
- Loading states and error handling
- Display of analysis results using `AnalysisResults` component

**Key Features Demonstrated**:
- `useApiQuery` hook for API data fetching
- Manual trigger with `enabled: false` option
- Form validation and user input handling
- Error boundary implementation

### 2. File Upload Analysis (`file-upload-analysis.jsx`)

Shows how to analyze privacy policies from uploaded documents:

- File upload with drag-and-drop interface
- Multi-step API workflow: Upload → Extract → Analyze
- Support for multiple file formats (PDF, DOC, DOCX, TXT)
- Progress indicators and error handling

**Key Features Demonstrated**:
- `FileUploadZone` component integration
- Sequential API calls with proper error handling
- File type validation and size limits
- User feedback during processing

### 3. Dashboard Integration (`dashboard-integration.jsx`)

Complete dashboard implementation with real-time data updates:

- Multiple dashboard components working together
- Real-time data refresh with intervals
- Statistics calculation and display
- Community insights integration

**Key Features Demonstrated**:
- Multiple `useApiQuery` hooks coordination
- Automatic data refresh patterns
- Component composition and layout
- Data transformation and aggregation

### 4. Subscription Management (`subscription-management.jsx`)

Comprehensive subscription handling with payment integration:

- Current plan display and usage tracking
- PayPal payment integration workflow
- Usage limit warnings and upgrade prompts
- Subscription modal integration

**Key Features Demonstrated**:
- `useApiMutation` for subscription updates
- PayPal payment flow integration
- Usage tracking and limit monitoring
- Modal state management

### 5. Policy Monitoring Setup (`policy-monitoring.jsx`)

Automated policy monitoring configuration:

- URL-based monitoring setup
- Frequency and notification preferences
- Active monitor management
- Real-time status updates

**Key Features Demonstrated**:
- Policy monitoring API integration
- Form handling for monitoring configuration
- Active monitor display and management
- Status tracking and notifications

## Component Integration Examples

### Key Components Showcased

1. **AnalysisResults**: Comprehensive display of privacy analysis
2. **FileUploadZone**: Drag-and-drop file upload interface
3. **Dashboard Components**: Stats cards, trends, and insights
4. **SubscriptionModal**: Payment and upgrade interface
5. **UsageTracker**: Subscription usage monitoring
6. **Error Handling**: Consistent error display patterns
7. **Loading States**: User feedback during API operations

### Integration Patterns

```jsx
// Standard component integration pattern
import { ComponentName } from '@/components/feature';
import { useApiQuery } from '@/hooks';
import { apiFunction } from '@/api/functions';

function IntegratedComponent() {
  const { data, loading, error } = useApiQuery('key', apiFunction);
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorAlert error={error} />;
  
  return <ComponentName data={data} />;
}
```

## API Integration Examples

### Base44 API Function Usage

All examples demonstrate proper integration with Base44 API functions:

- **`riskScoreCalculator`**: Privacy policy risk analysis
- **`UploadFile`**: Document upload to Base44
- **`ExtractDataFromUploadedFile`**: Content extraction from documents
- **`communityInsights`**: Community analytics and benchmarking
- **`subscriptionManager`**: Subscription lifecycle management
- **`paypalManager`**: PayPal payment processing
- **`policyMonitor`**: Automated policy monitoring

### Error Handling Patterns

```jsx
// Consistent error handling across examples
try {
  const result = await apiFunction(params);
  setData(result);
} catch (error) {
  setError(error);
  console.error('API Error:', error);
}
```

### Loading State Management

```jsx
// Loading state patterns used in examples
const [loading, setLoading] = useState(false);

const handleAction = async () => {
  setLoading(true);
  try {
    await performAction();
  } finally {
    setLoading(false);
  }
};
```

## Advanced Workflows

### Multi-Step API Workflows

The file upload example demonstrates complex workflows:

1. **File Upload**: Upload document to Base44 API
2. **Content Extraction**: Extract text from uploaded file
3. **Policy Analysis**: Analyze extracted content for privacy risks
4. **Result Display**: Show comprehensive analysis results

### Real-Time Data Updates

Dashboard example shows real-time data patterns:

```jsx
// Auto-refresh pattern
useEffect(() => {
  const interval = setInterval(refreshData, 5 * 60 * 1000);
  return () => clearInterval(interval);
}, [refreshData]);
```

### State Management Integration

Examples demonstrate integration with React Context:

```jsx
// Context integration pattern
const { user } = useAuth();
const { subscription } = useSubscription();
const { showNotification } = useNotification();
```

### Payment Integration Workflows

Subscription management example shows payment processing:

```jsx
// PayPal integration workflow
const { mutate: upgradeSubscription } = useApiMutation(
  async (planId) => {
    const paypalOrder = await paypalManager({
      action: 'create_order',
      plan_id: planId
    });
    
    return subscriptionManager({
      action: 'update',
      plan_id: planId,
      payment_method: { type: 'paypal', token: paypalOrder.order_id }
    });
  }
);
```

## Running Examples

### Prerequisites

1. Privacy Protocol development environment set up
2. Base44 API access configured
3. All dependencies installed (`npm install`)

### Running Individual Examples

```bash
# Start development server
npm run dev

# Import and use examples in your components
import BasicPolicyAnalysis from './examples/basic-usage';
import FileUploadAnalysis from './examples/file-upload-analysis';
import DashboardExample from './examples/dashboard-integration';
import SubscriptionManagement from './examples/subscription-management';
import PolicyMonitoringSetup from './examples/policy-monitoring';
```

### Integration into Main Application

```jsx
// Example of integrating examples into main app
import { Routes, Route } from 'react-router-dom';
import BasicPolicyAnalysis from './examples/basic-usage';
import FileUploadAnalysis from './examples/file-upload-analysis';
import DashboardExample from './examples/dashboard-integration';
import SubscriptionManagement from './examples/subscription-management';
import PolicyMonitoringSetup from './examples/policy-monitoring';

function App() {
  return (
    <Routes>
      <Route path="/examples/basic" element={<BasicPolicyAnalysis />} />
      <Route path="/examples/upload" element={<FileUploadAnalysis />} />
      <Route path="/examples/dashboard" element={<DashboardExample />} />
      <Route path="/examples/subscription" element={<SubscriptionManagement />} />
      <Route path="/examples/monitoring" element={<PolicyMonitoringSetup />} />
    </Routes>
  );
}
```

### Testing Examples

```bash
# Run tests for examples
npm test examples/

# Run specific example tests
npm test examples/basic-usage.test.jsx
npm test examples/file-upload-analysis.test.jsx
npm test examples/dashboard-integration.test.jsx
```

## Example File Structure

```
examples/
├── README.md                    # This documentation
├── basic-usage.jsx             # Simple policy analysis
├── file-upload-analysis.jsx    # File upload workflow
├── dashboard-integration.jsx   # Dashboard components
├── subscription-management.jsx # Subscription handling
├── policy-monitoring.jsx       # Monitoring setup
└── tests/                      # Example tests
    ├── basic-usage.test.jsx
    ├── file-upload.test.jsx
    ├── dashboard.test.jsx
    ├── subscription.test.jsx
    └── monitoring.test.jsx
```

## Best Practices Demonstrated

### 1. Error Handling
- Consistent error state management
- User-friendly error messages
- Graceful degradation on API failures
- Retry mechanisms for transient errors

### 2. Loading States
- Visual feedback during API calls
- Progressive loading for multi-step workflows
- Skeleton screens for better UX
- Cancellation of in-flight requests

### 3. API Integration
- Proper use of custom hooks
- Request deduplication and caching
- Optimistic updates where appropriate
- Rate limiting and quota management

### 4. Component Composition
- Reusable component patterns
- Props interface consistency
- Event handling standardization
- Accessibility compliance

### 5. State Management
- Context API usage patterns
- Local vs global state decisions
- State synchronization strategies
- Performance optimization techniques

### 6. Payment Integration
- Secure payment flow handling
- Error recovery for failed payments
- User feedback during payment processing
- Subscription state synchronization

### 7. Real-time Updates
- Efficient polling strategies
- WebSocket integration patterns
- Cache invalidation on updates
- User notification systems

## Contributing Examples

To add new examples to this collection:

1. Create a new `.jsx` file in the `examples/` directory
2. Follow the established patterns for error handling and API integration
3. Include comprehensive JSDoc comments
4. Add corresponding test files
5. Update this README with documentation
6. Ensure examples work with the current Base44 API version

### Example Template

```jsx
// examples/new-example.jsx
import React, { useState } from 'react';
import { useApiQuery } from '@/hooks';
import { apiFunction } from '@/api/functions';

/**
 * Example Component Description
 * 
 * Demonstrates: List key features and patterns
 * API Functions: List Base44 API functions used
 * Components: List React components used
 */
function NewExample() {
  // Component implementation
  return <div>Example content</div>;
}

export default NewExample;
```

## Common Patterns Reference

### API Query Pattern
```jsx
const { data, loading, error } = useApiQuery(
  'queryKey',
  () => apiFunction(params),
  { enabled: !!condition }
);
```

### API Mutation Pattern
```jsx
const { mutate, loading } = useApiMutation(
  (variables) => apiFunction(variables),
  {
    onSuccess: (data) => handleSuccess(data),
    onError: (error) => handleError(error)
  }
);
```

### Form Handling Pattern
```jsx
const [formData, setFormData] = useState(initialState);
const [errors, setErrors] = useState({});

const handleSubmit = async (e) => {
  e.preventDefault();
  try {
    await submitForm(formData);
  } catch (error) {
    setErrors(error.fieldErrors);
  }
};
```

### File Upload Pattern
```jsx
const handleFileUpload = async (file) => {
  const uploadResult = await UploadFile({ file });
  const extractResult = await ExtractDataFromUploadedFile({
    file_id: uploadResult.file_id
  });
  return extractResult;
};
```

---

*These examples are maintained by the Privacy Protocol development team. For questions about specific examples or to request new examples, please create an issue in the repository.*
