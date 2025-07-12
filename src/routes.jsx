import { Navigate } from 'react-router-dom';
import Layout from './pages/Layout';
import LoadingSpinner from './components/ui/loading-spinner';
import { createLazyComponent, createLazyRoute } from './utils/lazy-loading';

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
      { path: '/dashboard', element: <Dashboard /> },
      { path: '/analyzer', element: <Analyzer /> },
      { path: '/profile', element: <Profile /> },
      { path: '/history', element: <History /> },
      { path: '/insights', element: <Insights /> },
      { path: '/policy-tracker', element: <PolicyTracker /> },
      { path: '/advanced-insights', element: <AdvancedInsights /> },
      { path: '*', element: <Navigate to="/dashboard" replace /> }
    ]
  }
];