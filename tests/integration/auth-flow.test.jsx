/**
 * Integration test for authentication flow
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../../src/contexts/AuthContext';

// Mock API client
jest.mock('../../src/api/apiClient', () => ({
  base44: {
    auth: {
      login: jest.fn(),
      logout: jest.fn(),
      me: jest.fn()
    }
  },
  apiRequest: jest.fn((fn, options) => fn().then(res => {
    if (options?.onSuccess) options.onSuccess(res);
    return res;
  })),
  checkSession: jest.fn()
}));

// Import mocked modules
import { base44, apiRequest, checkSession } from '../../src/api/apiClient';

// Test component that uses auth context
const TestAuthComponent = () => {
  const { user, signIn, signOut, isAuthenticated } = useAuth();
  
  const handleLogin = () => {
    signIn({ email: 'test@example.com', password: 'password123' });
  };
  
  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
      </div>
      {user && <div data-testid="user-email">{user.email}</div>}
      <button onClick={handleLogin} data-testid="login-button">
        Login
      </button>
      <button onClick={signOut} data-testid="logout-button">
        Logout
      </button>
    </div>
  );
};

// Wrapper component with providers
const renderWithProviders = (ui) => {
  return render(
    <MemoryRouter>
      <AuthProvider>
        {ui}
      </AuthProvider>
    </MemoryRouter>
  );
};

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Default implementation for checkSession
    checkSession.mockResolvedValue(false);
  });
  
  test('shows unauthenticated state by default', async () => {
    renderWithProviders(<TestAuthComponent />);
    
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });
  });
  
  test('can sign in successfully', async () => {
    // Mock successful login
    base44.auth.login.mockResolvedValue({ 
      user: { id: '123', email: 'test@example.com' },
      token: 'fake-token'
    });
    
    renderWithProviders(<TestAuthComponent />);
    
    // Click login button
    fireEvent.click(screen.getByTestId('login-button'));
    
    // Wait for auth state to update
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
      expect(screen.getByTestId('user-email')).toHaveTextContent('test@example.com');
    });
    
    // Verify login was called with correct params
    expect(base44.auth.login).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123'
    });
  });
  
  test('can sign out successfully', async () => {
    // Mock authenticated user
    checkSession.mockResolvedValue(true);
    base44.auth.me.mockResolvedValue({ 
      id: '123', 
      email: 'test@example.com' 
    });
    
    // Mock successful logout
    base44.auth.logout.mockResolvedValue({ success: true });
    
    renderWithProviders(<TestAuthComponent />);
    
    // Wait for initial authenticated state
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Authenticated');
    });
    
    // Click logout button
    fireEvent.click(screen.getByTestId('logout-button'));
    
    // Wait for auth state to update
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });
    
    // Verify logout was called
    expect(base44.auth.logout).toHaveBeenCalled();
  });
  
  test('handles login errors', async () => {
    // Mock failed login
    const loginError = new Error('Invalid credentials');
    base44.auth.login.mockRejectedValue(loginError);
    
    // Mock apiRequest to capture error
    apiRequest.mockImplementation((fn, options) => {
      return fn().catch(err => {
        if (options?.onError) options.onError(err);
        throw err;
      });
    });
    
    renderWithProviders(<TestAuthComponent />);
    
    // Click login button
    fireEvent.click(screen.getByTestId('login-button'));
    
    // Auth state should remain unauthenticated
    await waitFor(() => {
      expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
    });
  });
});