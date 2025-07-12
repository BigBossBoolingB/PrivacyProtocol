import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the theme context
const ThemeContext = createContext(null);

/**
 * ThemeProvider component to manage theme state
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Child components
 * @returns {JSX.Element} - Rendered component
 */
export function ThemeProvider({ children }) {
  // Initialize theme from localStorage or default to 'dark'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('privacy-protocol-theme');
    return savedTheme || 'dark';
  });

  // Update document class when theme changes
  useEffect(() => {
    const root = window.document.documentElement;
    
    // Remove both classes first
    root.classList.remove('light', 'dark');
    
    // Add the current theme class
    root.classList.add(theme);
    
    // Save to localStorage
    localStorage.setItem('privacy-protocol-theme', theme);
  }, [theme]);

  /**
   * Toggle between light and dark themes
   */
  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  /**
   * Set a specific theme
   * 
   * @param {string} newTheme - The theme to set ('light' or 'dark')
   */
  const setThemeMode = (newTheme) => {
    if (newTheme === 'light' || newTheme === 'dark') {
      setTheme(newTheme);
    }
  };

  // Context value
  const value = {
    theme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
    toggleTheme,
    setTheme: setThemeMode
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to use the theme context
 * 
 * @returns {Object} - Theme context value
 */
export function useTheme() {
  const context = useContext(ThemeContext);
  
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  
  return context;
}