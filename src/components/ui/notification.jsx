import React, { useState, useEffect } from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { cn } from '@/utils';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Notification types
 */
export const NotificationType = {
  SUCCESS: 'success',
  ERROR: 'error',
  INFO: 'info',
  WARNING: 'warning'
};

/**
 * Notification component for displaying alerts and messages
 * 
 * @param {Object} props - Component props
 * @param {string} props.type - Notification type (success, error, info, warning)
 * @param {string} props.title - Notification title
 * @param {string} [props.message] - Notification message
 * @param {boolean} [props.autoClose=true] - Whether to auto-close the notification
 * @param {number} [props.duration=5000] - Auto-close duration in milliseconds
 * @param {Function} [props.onClose] - Callback when notification is closed
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} - Rendered component
 */
export function Notification({
  type = NotificationType.INFO,
  title,
  message,
  autoClose = true,
  duration = 5000,
  onClose,
  className
}) {
  const [isVisible, setIsVisible] = useState(true);

  // Auto-close timer
  useEffect(() => {
    if (autoClose && isVisible) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);
      
      return () => clearTimeout(timer);
    }
  }, [autoClose, duration, isVisible]);

  // Handle close
  const handleClose = () => {
    setIsVisible(false);
    if (onClose) {
      onClose();
    }
  };

  // Get icon and styles based on type
  const getTypeConfig = () => {
    switch (type) {
      case NotificationType.SUCCESS:
        return {
          icon: CheckCircle,
          bgColor: 'bg-green-500/10',
          borderColor: 'border-green-500/30',
          iconColor: 'text-green-500',
          progressColor: 'bg-green-500'
        };
      case NotificationType.ERROR:
        return {
          icon: AlertCircle,
          bgColor: 'bg-red-500/10',
          borderColor: 'border-red-500/30',
          iconColor: 'text-red-500',
          progressColor: 'bg-red-500'
        };
      case NotificationType.WARNING:
        return {
          icon: AlertTriangle,
          bgColor: 'bg-yellow-500/10',
          borderColor: 'border-yellow-500/30',
          iconColor: 'text-yellow-500',
          progressColor: 'bg-yellow-500'
        };
      case NotificationType.INFO:
      default:
        return {
          icon: Info,
          bgColor: 'bg-blue-500/10',
          borderColor: 'border-blue-500/30',
          iconColor: 'text-blue-500',
          progressColor: 'bg-blue-500'
        };
    }
  };

  const { icon: Icon, bgColor, borderColor, iconColor, progressColor } = getTypeConfig();

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={cn(
            "relative overflow-hidden rounded-lg border p-4 shadow-md",
            bgColor,
            borderColor,
            className
          )}
        >
          <div className="flex items-start gap-3">
            <div className={cn("shrink-0", iconColor)}>
              <Icon className="h-5 w-5" />
            </div>
            
            <div className="flex-1 space-y-1">
              {title && (
                <h5 className="font-medium text-gray-200">
                  {title}
                </h5>
              )}
              
              {message && (
                <p className="text-sm text-gray-400">
                  {message}
                </p>
              )}
            </div>
            
            <button
              onClick={handleClose}
              className="shrink-0 rounded-full p-1 text-gray-400 hover:bg-gray-800/50 hover:text-gray-300"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
          
          {autoClose && (
            <motion.div
              initial={{ width: '100%' }}
              animate={{ width: '0%' }}
              transition={{ duration: duration / 1000, ease: 'linear' }}
              className={cn("absolute bottom-0 left-0 h-1", progressColor)}
            />
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * NotificationContainer component for displaying multiple notifications
 * 
 * @param {Object} props - Component props
 * @param {Array} props.notifications - Array of notification objects
 * @param {Function} props.onClose - Callback when a notification is closed
 * @param {string} [props.position='top-right'] - Position of the container
 * @param {string} [props.className] - Additional CSS classes
 * @returns {JSX.Element} - Rendered component
 */
export function NotificationContainer({
  notifications = [],
  onClose,
  position = 'top-right',
  className
}) {
  // Get position classes
  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-0 left-0';
      case 'top-center':
        return 'top-0 left-1/2 -translate-x-1/2';
      case 'bottom-left':
        return 'bottom-0 left-0';
      case 'bottom-right':
        return 'bottom-0 right-0';
      case 'bottom-center':
        return 'bottom-0 left-1/2 -translate-x-1/2';
      case 'top-right':
      default:
        return 'top-0 right-0';
    }
  };

  return (
    <div
      className={cn(
        "fixed z-50 p-4 space-y-4 w-full max-w-sm",
        getPositionClasses(),
        className
      )}
    >
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            layout
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
          >
            <Notification
              {...notification}
              onClose={() => onClose(notification.id)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}