/**
 * Global type definitions for the Privacy Protocol application
 */

declare global {
  interface Window {
    gtag?: (command: string, action: string, parameters: Record<string, any>) => void;
  }
}

export {};
