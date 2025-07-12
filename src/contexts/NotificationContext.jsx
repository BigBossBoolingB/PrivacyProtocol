import React, { createContext, useContext, useState, useCallback } from 'react';
import { NotificationContainer, NotificationType } from '@/components/ui/notification';
import { uuidv4 } from '@/utils';

// Create the notification context
const NotificationContext = createContext(null);

/**
 * NotificationProvider component to manage global notifications
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} - Rendered component
 */
export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);

  /**
   * Add a notification
   * 
   * @param {Object} notification - Notification object
   * @param {string} notification.type - Notification type
   * @param {string} notification.title - Notification title
   * @param {string} [notification.message] - Notification message
   * @param {boolean} [notification.autoClose=true] - Whether to auto-close
   * @param {number} [notification.duration=5000] - Auto-close duration
   * @returns {string} - Notification ID
   */
  const addNotification = useCallback((notification) => {
    const id = notification.id || uuidv4();
    
    setNotifications(prev => [
      ...prev,
      { ...notification, id }
    ]);
    
    return id;
  }, []);

  /**
   * Remove a notification by ID
   * 
   * @param {string} id - Notification ID
   */
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  /**
   * Show a success notification
   * 
   * @param {string} title - Notification title
   * @param {string} [message] - Notification message
   * @param {Object} [options] - Additional options
   * @returns {string} - Notification ID
   */
  const showSuccess = useCallback((title, message, options = {}) => {
    return addNotification({
      type: NotificationType.SUCCESS,
      title,
      message,
      ...options
    });
  }, [addNotification]);

  /**
   * Show an error notification
   * 
   * @param {string} title - Notification title
   * @param {string} [message] - Notification message
   * @param {Object} [options] - Additional options
   * @returns {string} - Notification ID
   */
  const showError = useCallback((title, message, options = {}) => {
    return addNotification({
      type: NotificationType.ERROR,
      title,
      message,
      ...options
    });
  }, [addNotification]);

  /**
   * Show an info notification
   * 
   * @param {string} title - Notification title
   * @param {string} [message] - Notification message
   * @param {Object} [options] - Additional options
   * @returns {string} - Notification ID
   */
  const showInfo = useCallback((title, message, options = {}) => {
    return addNotification({
      type: NotificationType.INFO,
      title,
      message,
      ...options
    });
  }, [addNotification]);

  /**
   * Show a warning notification
   * 
   * @param {string} title - Notification title
   * @param {string} [message] - Notification message
   * @param {Object} [options] - Additional options
   * @returns {string} - Notification ID
   */
  const showWarning = useCallback((title, message, options = {}) => {
    return addNotification({
      type: NotificationType.WARNING,
      title,
      message,
      ...options
    });
  }, [addNotification]);

  // Context value
  const value = {
    notifications,
    addNotification,
    removeNotification,
    showSuccess,
    showError,
    showInfo,
    showWarning
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
      <NotificationContainer
        notifications={notifications}
        onClose={removeNotification}
        position="top-right"
      />
    </NotificationContext.Provider>
  );
}

/**
 * Hook to use the notification context
 * 
 * @returns {Object} - Notification context value
 */
export function useNotification() {
  const context = useContext(NotificationContext);
  
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  
  return context;
}