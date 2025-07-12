/**
 * TypeScript validation utilities for form inputs and data
 */

export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

/**
 * Validates an email address format
 */
export const validateEmail = (email: string): ValidationResult => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const isValid = emailRegex.test(email);
  return {
    isValid,
    error: isValid ? undefined : 'Please enter a valid email address'
  };
};

/**
 * Validates password strength
 */
export const validatePassword = (password: string): ValidationResult => {
  const isValid = Boolean(password && password.length >= 8);
  return {
    isValid,
    error: isValid ? undefined : 'Password must be at least 8 characters long'
  };
};

/**
 * Validates URL format
 */
export const validateUrl = (url: string): ValidationResult => {
  try {
    new URL(url);
    return { isValid: true };
  } catch {
    return {
      isValid: false,
      error: 'Please enter a valid URL'
    };
  }
};

/**
 * Validates file size
 */
export const validateFileSize = (file: File, maxSizeMB: number = 10): ValidationResult => {
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  const isValid = file.size <= maxSizeBytes;
  return {
    isValid,
    error: isValid ? undefined : `File size must be less than ${maxSizeMB}MB`
  };
};

/**
 * Validates file type
 */
export const validateFileType = (file: File, allowedTypes: string[] = []): ValidationResult => {
  if (allowedTypes.length === 0) return { isValid: true };
  const isValid = allowedTypes.includes(file.type);
  return {
    isValid,
    error: isValid ? undefined : `File type not allowed. Allowed types: ${allowedTypes.join(', ')}`
  };
};

/**
 * Sanitizes user input by removing potentially dangerous characters
 */
export const sanitizeInput = (input: string): string => {
  if (typeof input !== 'string') return input;
  return input.trim().replace(/[<>]/g, '');
};
