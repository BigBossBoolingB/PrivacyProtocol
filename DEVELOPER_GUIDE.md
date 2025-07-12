# Developer Guide

> **Complete guide for setting up, developing, and contributing to the Privacy Protocol React application**

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Debugging](#debugging)
- [Performance](#performance)
- [Deployment](#deployment)
- [Contributing](#contributing)

## Prerequisites

### Required Software

- **Node.js**: Version 18.0.0 or higher
- **npm**: Version 8.0.0 or higher (comes with Node.js)
- **Git**: For version control
- **Modern Browser**: Chrome, Firefox, Safari, or Edge

### Recommended Tools

- **VS Code**: With React and JavaScript extensions
- **React Developer Tools**: Browser extension for debugging
- **Git GUI**: GitKraken, SourceTree, or GitHub Desktop (optional)

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/BigBossBoolingB/PrivacyProtocol.git
cd PrivacyProtocol

# Install dependencies
npm install

# Start development server
npm run dev
```

### 2. Verify Installation

Open your browser and navigate to `http://localhost:3000`. You should see the Privacy Protocol application running.

### 3. Test the Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Development Environment

### Environment Configuration

The application uses Vite for development and building. Key configuration files:

- **`vite.config.js`**: Main Vite configuration
- **`package.json`**: Dependencies and scripts
- **`tailwind.config.js`**: Tailwind CSS configuration
- **`eslint.config.js`**: Code linting rules
- **`postcss.config.js`**: CSS processing

### Development Server Features

- **Hot Module Replacement (HMR)**: Instant updates without page refresh
- **Fast Refresh**: Preserves component state during updates
- **Error Overlay**: Clear error messages in the browser
- **Auto-open**: Automatically opens browser on start

### Available Scripts

```bash
# Development
npm run dev          # Start development server (port 3000)
npm run dev:host     # Start server accessible on network

# Building
npm run build        # Build for production
npm run preview      # Preview production build locally

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix auto-fixable ESLint issues
npm run format       # Format code with Prettier

# Testing (if configured)
npm test             # Run test suite
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Generate coverage report
```

## Project Structure

### Directory Overview

```
PrivacyProtocol/
├── public/                 # Static assets
│   ├── favicon.ico
│   └── index.html
├── src/                    # Source code
│   ├── api/               # Base44 API integration
│   ├── components/        # React components
│   ├── contexts/          # React Context providers
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility libraries
│   ├── pages/             # Page components
│   ├── utils/             # Helper functions
│   ├── App.jsx            # Root component
│   ├── main.jsx           # Application entry point
│   └── index.css          # Global styles
├── docs/                  # Documentation
├── policies/              # Policy documents
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS config
├── eslint.config.js       # ESLint configuration
└── README.md              # Project overview
```

### Key Directories Explained

#### `src/api/` - API Integration Layer
- **`apiClient.js`**: Core Base44 API client with error handling
- **`functions.js`**: Business logic API endpoints
- **`entities.js`**: Data model definitions from Base44 API
- **`integrations.js`**: External service integrations (LLM, email, file upload)

#### `src/components/` - React Components
Organized by feature area:
- **`analyzer/`**: Privacy policy analysis components
- **`dashboard/`**: User dashboard and overview components
- **`history/`**: Historical data management components
- **`insights/`**: Community analytics and benchmarking
- **`subscription/`**: Payment and subscription management
- **`ui/`**: Reusable UI component library (50+ components)

#### `src/hooks/` - Custom React Hooks
14 specialized hooks for different functionality:
- **Data Fetching**: `useApiQuery`, `useApiMutation`, `useDebounce`
- **Performance**: `useDeepMemo`, `useMemoizedCallback`, `useExpensiveCalculation`
- **Utilities**: `useLocalStorage`, `useErrorHandler`, `useFormWithValidation`

#### `src/contexts/` - Global State Management
- **`AuthContext.jsx`**: User authentication and session management
- **`SubscriptionContext.jsx`**: Subscription status and feature access
- **`ThemeContext.jsx`**: UI theme and preferences
- **`NotificationContext.jsx`**: Toast notifications and feedback

## Development Workflow

### 1. Feature Development Process

```bash
# 1. Create feature branch
git checkout -b feature/new-analysis-component

# 2. Make changes and test locally
npm run dev

# 3. Run code quality checks
npm run lint
npm run format

# 4. Commit changes
git add .
git commit -m "feat: add new analysis component"

# 5. Push and create PR
git push origin feature/new-analysis-component
```

### 2. Component Development Pattern

When creating new components, follow this structure:

```javascript
// src/components/feature/ComponentName.jsx
import React from 'react';
import { useApiQuery } from '@/hooks';
import { Button, Card } from '@/components/ui';

export function ComponentName({ prop1, prop2, onAction }) {
  const { data, loading, error } = useApiQuery('endpoint');

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <Card>
      <h2>{prop1}</h2>
      <p>{prop2}</p>
      <Button onClick={onAction}>
        Action
      </Button>
    </Card>
  );
}
```

### 3. API Integration Pattern

For new API integrations:

```javascript
// src/api/functions.js
export async function newApiFunction(params) {
  return apiRequest(
    () => base44.someEndpoint(params),
    {
      successMessage: 'Operation completed successfully',
      errorMessage: 'Failed to complete operation'
    }
  );
}

// Usage in component
const { data, loading, error } = useApiQuery('newApiFunction', params);
```

### 4. Custom Hook Pattern

For reusable logic:

```javascript
// src/hooks/use-custom-logic.js
import { useState, useEffect } from 'react';

export function useCustomLogic(initialValue) {
  const [state, setState] = useState(initialValue);

  useEffect(() => {
    // Custom logic here
  }, []);

  return { state, setState };
}
```

## Code Standards

### 1. JavaScript/React Standards

- **ES6+ Features**: Use modern JavaScript features
- **Functional Components**: Prefer function components over class components
- **Hooks**: Use React hooks for state and side effects
- **Destructuring**: Destructure props and state for cleaner code
- **Arrow Functions**: Use arrow functions for inline functions

### 2. File Naming Conventions

- **Components**: PascalCase (e.g., `AnalysisResults.jsx`)
- **Hooks**: camelCase with "use" prefix (e.g., `useApiQuery.js`)
- **Utilities**: camelCase (e.g., `formatters.js`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `API_ENDPOINTS`)

### 3. Import Organization

```javascript
// 1. React and external libraries
import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';

// 2. Internal utilities and hooks
import { useApiQuery } from '@/hooks';
import { formatDate } from '@/utils';

// 3. Components (UI first, then feature components)
import { Button, Card } from '@/components/ui';
import { AnalysisResults } from '@/components/analyzer';
```

### 4. Component Structure

```javascript
// Props destructuring with defaults
export function Component({ 
  title = 'Default Title', 
  data = [], 
  onAction 
}) {
  // Hooks at the top
  const [state, setState] = useState();
  const { apiData } = useApiQuery();

  // Event handlers
  const handleClick = () => {
    // Handler logic
  };

  // Early returns for loading/error states
  if (!data) return <div>Loading...</div>;

  // Main render
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
}
```

### 5. CSS and Styling

- **Tailwind CSS**: Primary styling framework
- **CSS Modules**: For component-specific styles (when needed)
- **Responsive Design**: Mobile-first approach
- **Accessibility**: ARIA labels and semantic HTML

## Testing

### 1. Testing Strategy

The application uses a comprehensive testing approach:

- **Unit Tests**: Individual component and function testing
- **Integration Tests**: API integration and data flow testing
- **E2E Tests**: Complete user workflow testing
- **Visual Tests**: Component appearance and responsive design

### 2. Testing Tools

- **Jest**: JavaScript testing framework
- **React Testing Library**: React component testing
- **MSW**: API mocking for tests
- **Playwright**: End-to-end testing

### 3. Writing Tests

```javascript
// Component test example
import { render, screen, fireEvent } from '@testing-library/react';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  test('renders correctly', () => {
    render(<ComponentName title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  test('handles user interaction', () => {
    const mockAction = jest.fn();
    render(<ComponentName onAction={mockAction} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(mockAction).toHaveBeenCalled();
  });
});
```

### 4. Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test ComponentName.test.jsx
```

## Debugging

### 1. Browser Developer Tools

- **React DevTools**: Inspect component state and props
- **Network Tab**: Monitor API requests and responses
- **Console**: View logs and error messages
- **Performance Tab**: Analyze rendering performance

### 2. Common Debugging Techniques

```javascript
// Console logging
console.log('Debug data:', data);
console.table(arrayData);

// React DevTools debugging
const DebugComponent = () => {
  const debugData = { state, props, apiData };
  console.log('Component debug:', debugData);
  
  return <div>Component content</div>;
};

// Error boundaries
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }
}
```

### 3. API Debugging

```javascript
// API request debugging
export async function debugApiRequest(endpoint, params) {
  console.log('API Request:', { endpoint, params });
  
  try {
    const response = await apiCall(endpoint, params);
    console.log('API Response:', response);
    return response;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

## Performance

### 1. Performance Monitoring

The application includes built-in performance tracking:

- **Core Web Vitals**: LCP, FID, CLS monitoring
- **Custom Metrics**: Component render times, API response times
- **Bundle Analysis**: Code splitting effectiveness
- **Memory Usage**: Memory leak detection

### 2. Optimization Techniques

```javascript
// Component memoization
const ExpensiveComponent = React.memo(({ data }) => {
  return <div>{/* Expensive rendering */}</div>;
});

// Callback memoization
const MemoizedCallback = useCallback(() => {
  // Expensive operation
}, [dependency]);

// Value memoization
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);
```

### 3. Bundle Optimization

The Vite configuration includes strategic code splitting:

```javascript
// vite.config.js
manualChunks: {
  'react-vendor': ['react', 'react-dom', 'react-router-dom'],
  'ui-components': ['@radix-ui/*'],
  'form-utils': ['react-hook-form', 'zod'],
  'data-viz': ['recharts']
}
```

## Deployment

### 1. Production Build

```bash
# Create production build
npm run build

# Test production build locally
npm run preview
```

### 2. Build Optimization

The production build includes:

- **Minification**: JavaScript and CSS minification
- **Tree Shaking**: Unused code elimination
- **Asset Optimization**: Image and font optimization
- **Gzip Compression**: Reduced file sizes

### 3. Environment Variables

```bash
# .env.local (not committed to git)
VITE_BASE44_API_URL=https://api.base44.com
VITE_ANALYTICS_ID=your-analytics-id
```

## Contributing

### 1. Code Review Process

1. **Create Feature Branch**: Use descriptive branch names
2. **Write Tests**: Include tests for new functionality
3. **Run Quality Checks**: Lint, format, and test before PR
4. **Create Pull Request**: Use PR template and clear description
5. **Address Feedback**: Respond to review comments promptly

### 2. Commit Message Format

```bash
# Format: type(scope): description
feat(analyzer): add new risk calculation component
fix(api): handle network timeout errors
docs(readme): update installation instructions
style(ui): improve button component styling
refactor(hooks): simplify useApiQuery implementation
```

### 3. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
```

### 4. Getting Help

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Documentation**: Check existing docs first
- **Code Review**: Learn from PR feedback

---

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 3000
   npx kill-port 3000
   # Or use different port
   npm run dev -- --port 3001
   ```

2. **Module Not Found**
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Build Errors**
   ```bash
   # Check for TypeScript errors
   npm run type-check
   # Clear Vite cache
   rm -rf node_modules/.vite
   ```

4. **API Connection Issues**
   - Check network connectivity
   - Verify API endpoint URLs
   - Check browser console for CORS errors

---

*This developer guide is maintained by the Privacy Protocol team. For questions or improvements, please create an issue or submit a pull request.*
