import React, { createContext, useContext, useState, useEffect } from 'react';
import { base44, apiRequest, checkSession } from '@/api/apiClient';
import LoadingSpinner from '@/components/ui/loading-spinner';

// Create the auth context
const AuthContext = createContext(null);

/**
 * AuthProvider component to manage authentication state
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} - Rendered component
 */
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load user data on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const isSessionValid = await checkSession();
        
        if (isSessionValid) {
          const userData = await base44.auth.me();
          setUser(userData);
        }
      } catch (err) {
        console.error('Failed to load user:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  /**
   * Sign in user
   * 
   * @param {Object} credentials - User credentials
   * @param {string} credentials.email - User email
   * @param {string} credentials.password - User password
   * @returns {Promise<Object>} - User data
   */
  const signIn = async (credentials) => {
    setLoading(true);
    
    try {
      const response = await apiRequest(
        () => base44.auth.login(credentials),
        {
          showSuccessToast: true,
          successMessage: 'Signed in successfully',
          errorMessage: 'Failed to sign in'
        }
      );
      
      setUser(response.user);
      return response.user;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  /**
   * Sign out user
   * 
   * @returns {Promise<void>}
   */
  const signOut = async () => {
    setLoading(true);
    
    try {
      await apiRequest(
        () => base44.auth.logout(),
        {
          showSuccessToast: true,
          successMessage: 'Signed out successfully',
          errorMessage: 'Failed to sign out'
        }
      );
      
      setUser(null);
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Context value
  const value = {
    user,
    loading,
    error,
    signIn,
    signOut,
    isAuthenticated: !!user
  };

  // Show loading spinner while initializing
  if (loading && !user) {
    return <LoadingSpinner text="Loading user data..." />;
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use the auth context
 * 
 * @returns {Object} - Auth context value
 */
export function useAuth() {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}