import React from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * LoadingSpinner component
 * 
 * @param {Object} props - Component props
 * @param {string} [props.size='md'] - Size of the spinner (sm, md, lg)
 * @param {string} [props.className] - Additional CSS classes
 * @param {string} [props.text] - Optional text to display with the spinner
 * @returns {JSX.Element} - Rendered component
 */
export default function LoadingSpinner({ size = 'md', className, text }) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  };

  return (
    <div className="flex flex-col items-center justify-center p-8">
      <Loader2 
        className={cn(
          'animate-spin text-blue-500',
          sizeClasses[size],
          className
        )} 
      />
      {text && (
        <p className="mt-4 text-sm text-gray-400">{text}</p>
      )}
    </div>
  );
}