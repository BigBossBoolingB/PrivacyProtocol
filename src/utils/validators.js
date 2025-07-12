import { z } from 'zod';

/**
 * Email validation schema
 */
export const emailSchema = z
  .string()
  .email('Please enter a valid email address')
  .min(1, 'Email is required');

/**
 * Password validation schema
 */
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

/**
 * URL validation schema
 */
export const urlSchema = z
  .string()
  .url('Please enter a valid URL')
  .or(z.literal(''));

/**
 * Name validation schema
 */
export const nameSchema = z
  .string()
  .min(2, 'Name must be at least 2 characters')
  .max(100, 'Name must be less than 100 characters');

/**
 * Phone validation schema
 */
export const phoneSchema = z
  .string()
  .regex(/^\+?[0-9]{10,15}$/, 'Please enter a valid phone number')
  .or(z.literal(''));

/**
 * Login form validation schema
 */
export const loginFormSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional()
});

/**
 * Registration form validation schema
 */
export const registrationFormSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string().min(1, 'Please confirm your password'),
  acceptTerms: z.literal(true, {
    errorMap: () => ({ message: 'You must accept the terms and conditions' })
  })
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Passwords do not match',
  path: ['confirmPassword']
});

/**
 * Privacy profile form validation schema
 */
export const privacyProfileFormSchema = z.object({
  privacy_tolerance: z.enum(['strict', 'moderate', 'relaxed'], {
    errorMap: () => ({ message: 'Please select a privacy tolerance level' })
  }),
  data_sharing_preferences: z.array(z.string()).optional(),
  location_tracking: z.boolean().optional(),
  marketing_communications: z.boolean().optional(),
  third_party_sharing: z.boolean().optional(),
  data_retention_period: z.enum(['30_days', '90_days', '1_year', 'indefinite'], {
    errorMap: () => ({ message: 'Please select a data retention period' })
  }).optional()
});

/**
 * Agreement analysis form validation schema
 */
export const agreementAnalysisFormSchema = z.object({
  url: urlSchema,
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(10, 'Content must be at least 10 characters'),
  company_name: z.string().min(1, 'Company name is required'),
  agreement_type: z.enum(['privacy_policy', 'terms_of_service', 'eula', 'other'], {
    errorMap: () => ({ message: 'Please select an agreement type' })
  })
});

/**
 * Validate an email address
 * 
 * @param {string} email - The email to validate
 * @returns {boolean} - Whether the email is valid
 */
export function isValidEmail(email) {
  return emailSchema.safeParse(email).success;
}

/**
 * Validate a URL
 * 
 * @param {string} url - The URL to validate
 * @returns {boolean} - Whether the URL is valid
 */
export function isValidUrl(url) {
  return urlSchema.safeParse(url).success;
}

/**
 * Validate a password
 * 
 * @param {string} password - The password to validate
 * @returns {Object} - Validation result with success and error message
 */
export function validatePassword(password) {
  const result = passwordSchema.safeParse(password);
  
  return {
    success: result.success,
    error: result.success ? null : result.error.errors[0].message
  };
}