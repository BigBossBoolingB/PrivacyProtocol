import { Navigate } from 'react-router-dom';
import Layout from './pages/Layout';
import LoadingSpinner from './components/ui/loading-spinner';
import { createLazyComponent, createLazyRoute } from './utils/lazy-loading';
import ErrorBoundary from './components/ErrorBoundary';

// Custom loading component
const PageLoading = () => <LoadingSpinner text="Loading page..." />;

// Create lazy-loaded components with performance tracking
const Dashboard = createLazyComponent(
  () => import('./pages/Dashboard'),
  { name: 'Dashboard', Loading: PageLoading }
);

const Analyzer = createLazyComponent(
  () => import('./pages/Analyzer'),
  { name: 'Analyzer', Loading: PageLoading }
);

const Profile = createLazyComponent(
  () => import('./pages/Profile'),
  { name: 'Profile', Loading: PageLoading }
);

const History = createLazyComponent(
  () => import('./pages/History'),
  { name: 'History', Loading: PageLoading }
);

const Insights = createLazyComponent(
  () => import('./pages/Insights'),
  { name: 'Insights', Loading: PageLoading }
);

const PolicyTracker = createLazyComponent(
  () => import('./pages/PolicyTracker'),
  { name: 'PolicyTracker', Loading: PageLoading }
);

const AdvancedInsights = createLazyComponent(
  () => import('./pages/AdvancedInsights'),
  { name: 'AdvancedInsights', Loading: PageLoading }
);

// Define routes with their corresponding components
export const routes = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { path: '/', element: <Navigate to="/dashboard" replace /> },
      { 
        path: '/dashboard', 
        element: (
          <ErrorBoundary name="Dashboard" context={{ page: 'dashboard' }}>
            <Dashboard />
          </ErrorBoundary>
        )
      },
      { 
        path: '/analyzer', 
        element: (
          <ErrorBoundary name="Analyzer" context={{ page: 'analyzer' }}>
            <Analyzer />
          </ErrorBoundary>
        )
      },
      { 
        path: '/profile', 
        element: (
          <ErrorBoundary name="Profile" context={{ page: 'profile' }}>
            <Profile />
          </ErrorBoundary>
        )
      },
      { 
        path: '/history', 
        element: (
          <ErrorBoundary name="History" context={{ page: 'history' }}>
            <History />
          </ErrorBoundary>
        )
      },
      { 
        path: '/insights', 
        element: (
          <ErrorBoundary name="Insights" context={{ page: 'insights' }}>
            <Insights />
          </ErrorBoundary>
        )
      },
      { 
        path: '/policy-tracker', 
        element: (
          <ErrorBoundary name="PolicyTracker" context={{ page: 'policy-tracker' }}>
            <PolicyTracker />
          </ErrorBoundary>
        )
      },
      { 
        path: '/advanced-insights', 
        element: (
          <ErrorBoundary name="AdvancedInsights" context={{ page: 'advanced-insights' }}>
            <AdvancedInsights />
          </ErrorBoundary>
        )
      },
      { path: '*', element: <Navigate to="/dashboard" replace /> }
    ]
  }
];
