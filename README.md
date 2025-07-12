# Privacy Protocol Application

A comprehensive privacy management application built with React and Vite that helps users analyze, monitor, and manage privacy policies and agreements. The application communicates with the Base44 API for data processing and analysis.

<!-- Verification comment added by Devin for testing purposes -->

## Features

- **Privacy Policy Analysis**: Upload and analyze privacy policies to identify potential risks
- **Policy Monitoring**: Track changes to privacy policies over time
- **Privacy Insights**: Get actionable insights about your privacy exposure
- **User Privacy Profile**: Manage your privacy preferences in one place
- **Subscription Management**: Access premium features with subscription plans

## Technology Stack

- **Frontend**: React 18, React Router v7
- **UI Components**: Custom components with Radix UI primitives
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **Form Handling**: React Hook Form with Zod validation
- **API Communication**: Custom hooks with caching
- **Error Handling**: Comprehensive error tracking system
- **Testing**: Jest and React Testing Library

## Getting Started

### Prerequisites

- Node.js 16.x or higher
- npm 8.x or higher

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
# Build optimized production bundle
npm run build

# Preview production build
npm run preview
```

## Testing

The application includes comprehensive test coverage:

```bash
# Run all tests
npm test

# Run tests with coverage report
npm run test:coverage

# Run tests in watch mode during development
npm run test:watch
```

## Project Structure

```
privacy-protocol/
├── src/                  # Source code
│   ├── api/              # API clients and service interfaces
│   ├── components/       # Reusable UI components
│   ├── contexts/         # React context providers
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities and constants
│   ├── pages/            # Page components
│   └── utils/            # Utility functions
├── tests/                # Test files
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── system/           # System/E2E tests
│   ├── performance/      # Performance tests
│   └── security/         # Security tests
└── policies/             # Project policies and guidelines
```

## Key Optimizations

- **API Request Caching**: Implemented stale-while-revalidate caching strategy
- **Error Tracking**: Enhanced error tracking with breadcrumbs and session management
- **Performance Monitoring**: Added performance measurement utilities
- **Code Splitting**: Optimized bundle size with dynamic imports
- **Memoization**: Reduced unnecessary re-renders with React.memo and useMemo

## Policies

This project adheres to comprehensive policies for:

- Testing
- Security
- Error Handling
- Validation
- Process Management
- System Architecture

See the `policies/` directory for detailed documentation.

## Support

For more information and support, please contact Base44 support at app@base44.com.

## License

Proprietary - All rights reserved.
