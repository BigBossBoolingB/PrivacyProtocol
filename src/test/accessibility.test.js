import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { BrowserRouter } from 'react-router-dom';

expect.extend(toHaveNoViolations);

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

export const testAccessibility = async (component, options = {}) => {
  const { container } = renderWithRouter(component);
  const results = await axe(container, {
    rules: {
      'color-contrast': { enabled: true },
      'keyboard-navigation': { enabled: true },
      'focus-management': { enabled: true },
      'aria-labels': { enabled: true },
      ...options.rules
    }
  });
  
  expect(results).toHaveNoViolations();
  return results;
};

export const testKeyboardNavigation = (component) => {
  const { container } = renderWithRouter(component);
  
  const focusableElements = container.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  expect(focusableElements.length).toBeGreaterThan(0);
  
  focusableElements.forEach(element => {
    expect(element).not.toHaveAttribute('tabindex', '-1');
  });
};

export const testAriaLabels = (component) => {
  const { container } = renderWithRouter(component);
  
  const interactiveElements = container.querySelectorAll(
    'button, [role="button"], input, select, textarea'
  );
  
  interactiveElements.forEach(element => {
    const hasLabel = 
      element.hasAttribute('aria-label') ||
      element.hasAttribute('aria-labelledby') ||
      element.textContent.trim() !== '' ||
      element.querySelector('label');
    
    expect(hasLabel).toBe(true);
  });
};
