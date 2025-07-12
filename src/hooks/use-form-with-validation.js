import { useState, useCallback } from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';

/**
 * Custom hook for form handling with validation and submission
 * 
 * @param {Object} options - Hook options
 * @param {Object} options.schema - Zod schema for validation
 * @param {Object} [options.defaultValues={}] - Default form values
 * @param {Function} options.onSubmit - Form submission handler
 * @param {string} [options.successMessage] - Success message to display
 * @param {string} [options.errorMessage] - Error message to display
 * @param {boolean} [options.resetOnSuccess=false] - Whether to reset the form on successful submission
 * @returns {Object} - Form handling utilities
 */
export function useFormWithValidation({
  schema,
  defaultValues = {},
  onSubmit,
  successMessage,
  errorMessage,
  resetOnSuccess = false
}) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const form = useForm({
    resolver: schema ? zodResolver(schema) : undefined,
    defaultValues,
    mode: 'onBlur'
  });

  const handleSubmit = useCallback(async (data) => {
    setIsSubmitting(true);
    
    try {
      await onSubmit(data);
      
      if (successMessage) {
        toast.success(successMessage);
      }
      
      if (resetOnSuccess) {
        form.reset(defaultValues);
      }
      
      return true;
    } catch (error) {
      console.error('Form submission error:', error);
      
      toast.error(
        errorMessage || 
        error.message || 
        'An error occurred while submitting the form'
      );
      
      return false;
    } finally {
      setIsSubmitting(false);
    }
  }, [onSubmit, successMessage, errorMessage, resetOnSuccess, form, defaultValues]);

  return {
    form,
    isSubmitting,
    handleSubmit: form.handleSubmit(handleSubmit),
    reset: form.reset,
    formState: form.formState,
    register: form.register,
    control: form.control,
    watch: form.watch,
    setValue: form.setValue,
    getValues: form.getValues
  };
}