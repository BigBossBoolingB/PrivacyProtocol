/**
 * Unit tests for UI components
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock components for testing
const Button = ({ children, onClick, disabled, variant = 'default' }) => (
  <button 
    onClick={onClick} 
    disabled={disabled}
    className={`btn btn-${variant}`}
    data-testid="button"
  >
    {children}
  </button>
);

const Input = ({ label, value, onChange, type = 'text', error }) => (
  <div>
    {label && <label data-testid="input-label">{label}</label>}
    <input
      type={type}
      value={value}
      onChange={onChange}
      data-testid="input"
      aria-invalid={!!error}
    />
    {error && <span data-testid="input-error">{error}</span>}
  </div>
);

// Button component tests
describe('Button Component', () => {
  test('renders with children', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByTestId('button')).toHaveTextContent('Click me');
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByTestId('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('does not call onClick when disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Click me</Button>);
    fireEvent.click(screen.getByTestId('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });

  test('applies variant class', () => {
    render(<Button variant="primary">Primary Button</Button>);
    expect(screen.getByTestId('button')).toHaveClass('btn-primary');
  });
});

// Input component tests
describe('Input Component', () => {
  test('renders with label', () => {
    render(<Input label="Username" value="" onChange={() => {}} />);
    expect(screen.getByTestId('input-label')).toHaveTextContent('Username');
  });

  test('updates value on change', () => {
    const handleChange = jest.fn();
    render(<Input value="" onChange={handleChange} />);
    
    fireEvent.change(screen.getByTestId('input'), { 
      target: { value: 'test input' } 
    });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  test('displays error message', () => {
    render(
      <Input 
        label="Email" 
        value="invalid" 
        onChange={() => {}} 
        error="Please enter a valid email" 
      />
    );
    
    expect(screen.getByTestId('input-error')).toHaveTextContent('Please enter a valid email');
    expect(screen.getByTestId('input')).toHaveAttribute('aria-invalid', 'true');
  });

  test('renders different input types', () => {
    render(<Input type="password" value="secret" onChange={() => {}} />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'password');
  });
});