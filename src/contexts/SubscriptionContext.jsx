import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiRequest } from '@/api/apiClient';
import { subscriptionManager } from '@/api/functions';
import { useAuth } from './AuthContext';
import { SUBSCRIPTION_PLANS } from '@/lib/constants';

// Create the subscription context
const SubscriptionContext = createContext(null);

/**
 * SubscriptionProvider component to manage subscription state
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} - Rendered component
 */
export function SubscriptionProvider({ children }) {
  const { user, isAuthenticated } = useAuth();
  const [subscription, setSubscription] = useState(null);
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load subscription data when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadSubscriptionData();
    } else {
      setSubscription(null);
      setFeatures(null);
      setLoading(false);
    }
  }, [isAuthenticated, user?.id]);

  /**
   * Load subscription data
   * 
   * @returns {Promise<void>}
   */
  const loadSubscriptionData = async () => {
    setLoading(true);
    
    try {
      const { data } = await apiRequest(
        () => subscriptionManager({ action: 'get_subscription' })
      );
      
      if (data) {
        setSubscription(data.subscription);
        setFeatures(data.features);
      }
    } catch (error) {
      console.error('Error loading subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Upgrade to premium subscription
   * 
   * @returns {Promise<void>}
   */
  const upgradeToPremium = async () => {
    try {
      await apiRequest(
        () => subscriptionManager({ action: 'upgrade_subscription' }),
        {
          showSuccessToast: true,
          successMessage: 'Successfully upgraded to premium!',
          errorMessage: 'Failed to upgrade subscription'
        }
      );
      
      await loadSubscriptionData();
    } catch (error) {
      console.error('Error upgrading subscription:', error);
      throw error;
    }
  };

  /**
   * Downgrade to free subscription
   * 
   * @returns {Promise<void>}
   */
  const downgradeToFree = async () => {
    try {
      await apiRequest(
        () => subscriptionManager({ action: 'downgrade_subscription' }),
        {
          showSuccessToast: true,
          successMessage: 'Successfully downgraded to free plan',
          errorMessage: 'Failed to downgrade subscription'
        }
      );
      
      await loadSubscriptionData();
    } catch (error) {
      console.error('Error downgrading subscription:', error);
      throw error;
    }
  };

  /**
   * Check if user has premium features
   * 
   * @returns {boolean} - Whether user has premium features
   */
  const isPremium = () => {
    return subscription?.plan_type === SUBSCRIPTION_PLANS.PREMIUM;
  };

  /**
   * Get usage percentage for the current plan
   * 
   * @returns {number} - Usage percentage (0-100)
   */
  const getUsagePercentage = () => {
    if (isPremium()) return 0;
    
    const used = subscription?.monthly_analyses_used || 0;
    const limit = features?.monthly_analyses_limit || 1;
    
    return Math.min(Math.round((used / limit) * 100), 100);
  };

  // Context value
  const value = {
    subscription,
    features,
    loading,
    isPremium: isPremium(),
    usagePercentage: getUsagePercentage(),
    upgradeToPremium,
    downgradeToFree,
    refreshSubscription: loadSubscriptionData
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
    </SubscriptionContext.Provider>
  );
}

/**
 * Hook to use the subscription context
 * 
 * @returns {Object} - Subscription context value
 */
export function useSubscription() {
  const context = useContext(SubscriptionContext);
  
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  
  return context;
}